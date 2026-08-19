#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
fixture="$(mktemp -d "${TMPDIR:-/tmp}/new-project-worktree-overlap.XXXXXX")"
cleanup() {
  rm -rf "$fixture"
}
trap cleanup EXIT INT TERM

checker="$repo_root/scripts/worktree_overlap_check.py"
guard="$repo_root/scripts/worktree_guard.py"
workspace="$fixture/workspace"
primary="$workspace/sample"
linked="$workspace/.worktrees/sample-ticket-a"
linked_b="$workspace/.worktrees/sample-ticket-b"

mkdir -p "$workspace/.worktrees"
git init --quiet --initial-branch=main "$primary"
git -C "$primary" config user.email overlap-test@example.invalid
git -C "$primary" config user.name overlap-test
printf '%s\n' sample > "$primary/README.md"
printf '%s\n' src > "$primary/app.py"
git -C "$primary" add README.md app.py
git -C "$primary" commit --quiet -m initial
git -C "$primary" remote add origin git@github.com:example/sample.git
git -C "$primary" worktree add --quiet -b ticket/010 "$linked"
git -C "$primary" worktree add --quiet -b ticket/011 "$linked_b"

# Same file dirtied in two worktrees — this is the merge-conflict precursor.
printf '%s\n' left > "$linked/app.py"
printf '%s\n' right > "$linked_b/app.py"

if python3 "$checker" --workspace-root "$workspace" --format json \
  > "$fixture/overlap.json"; then
  status=0
else
  status=$?
fi
test "$status" -eq 1
python3 - "$fixture/overlap.json" "$linked" "$linked_b" <<'PY'
import json
import sys

report = json.load(open(sys.argv[1], encoding="utf-8"))
assert report["schema"] == "new-project.worktree-overlap-report/v1"
assert report["status"] == "failed"
assert report["summary"]["errors"] >= 1
codes = {finding["code"] for finding in report["findings"]}
assert "GOV-WORKTREE-OVERLAP-001" in codes
finding = next(
    item for item in report["findings"] if item["code"] == "GOV-WORKTREE-OVERLAP-001"
)
assert "app.py" in finding["evidence"]["overlappingPaths"]
assert {finding["evidence"]["left"], finding["evidence"]["right"]} == {
    sys.argv[2],
    sys.argv[3],
}
PY

# Distinct files in two worktrees must pass the path check.
git -C "$linked" checkout -- app.py
git -C "$linked_b" checkout -- app.py
printf '%s\n' only-a > "$linked/left-only.txt"
printf '%s\n' only-b > "$linked_b/right-only.txt"
python3 "$checker" --workspace-root "$workspace" --format json > "$fixture/disjoint.json"
python3 - "$fixture/disjoint.json" <<'PY'
import json
import sys

report = json.load(open(sys.argv[1], encoding="utf-8"))
assert report["status"] == "passed", report
assert report["summary"]["errors"] == 0
assert report["summary"]["checkouts"] >= 3
PY

# Intent overlap without conflictsWith.
mkdir -p "$linked/project/ticket-010" "$linked_b/project/ticket-011"
cat > "$linked/project/ticket-010/README.md" <<'MD'
- **Status**: IN_PROGRESS
MD
cat > "$linked_b/project/ticket-011/README.md" <<'MD'
- **Status**: IN_PROGRESS
MD
printf '%s\n' '{"ticket":"ticket-010","allowedPaths":["src/**","app.py"],"conflictsWith":[],"workstream":"application"}' \
  > "$linked/project/ticket-010/intent.json"
printf '%s\n' '{"ticket":"ticket-011","allowedPaths":["app.py","docs/**"],"conflictsWith":[],"workstream":"application"}' \
  > "$linked_b/project/ticket-011/intent.json"

if python3 "$checker" --workspace-root "$workspace" --format json \
  > "$fixture/intent.json"; then
  status=0
else
  status=$?
fi
test "$status" -eq 1
python3 - "$fixture/intent.json" <<'PY'
import json
import sys

report = json.load(open(sys.argv[1], encoding="utf-8"))
assert "GOV-WORKTREE-OVERLAP-002" in {item["code"] for item in report["findings"]}
PY

# Declared conflictsWith serializes the same scope.
python3 - "$linked_b/project/ticket-011/intent.json" <<'PY'
import json
from pathlib import Path
path = Path(__import__("sys").argv[1] if False else "")
PY
python3 -c '
import json
from pathlib import Path
path = Path("'"$linked_b"'/project/ticket-011/intent.json")
data = json.loads(path.read_text())
data["conflictsWith"] = ["ticket-010"]
path.write_text(json.dumps(data))
'
python3 "$checker" --workspace-root "$workspace" --format json > "$fixture/declared.json"
python3 - "$fixture/declared.json" <<'PY'
import json
import sys

report = json.load(open(sys.argv[1], encoding="utf-8"))
assert "GOV-WORKTREE-OVERLAP-002" not in {item["code"] for item in report["findings"]}
assert report["status"] == "passed", report
PY

# Guard runner (once) uses the hub yaml when present.
if python3 -c "import yaml" >/dev/null 2>&1; then
  python3 "$guard" --root "$repo_root" --once --format json > "$fixture/guard.json" || true
  python3 - "$fixture/guard.json" <<'PY'
import json
import sys
from pathlib import Path
raw = Path(sys.argv[1]).read_text(encoding="utf-8").strip()
# The hub itself may already have overlapping new-project worktrees.
assert raw, "guard produced no output"
PY
fi

if python3 "$checker" --workspace-root "$fixture/missing" \
  > "$fixture/missing.out" 2>&1; then
  status=0
else
  status=$?
fi
test "$status" -eq 1
grep -q '^GOV-WORKTREE-OVERLAP-003 ERROR:' "$fixture/missing.out"

# A merged-but-still-IN_PROGRESS ticket directory is present in every sibling
# worktree. Only the checkout whose branch is that ticket's branch is writing
# it, so a third worktree carrying stale copies must not be paired.
linked_c="$workspace/.worktrees/sample-ticket-c"
git -C "$primary" worktree add --quiet -b ticket/012 "$linked_c"
python3 -c '
import json
from pathlib import Path
path = Path("'"$linked_b"'/project/ticket-011/intent.json")
data = json.loads(path.read_text())
data["conflictsWith"] = []
path.write_text(json.dumps(data))
'
mkdir -p "$linked_c/project"
cp -r "$linked/project/ticket-010" "$linked_c/project/ticket-010"
cp -r "$linked_b/project/ticket-011" "$linked_c/project/ticket-011"

if python3 "$checker" --workspace-root "$workspace" --format json \
  > "$fixture/attribution.json"; then
  status=0
else
  status=$?
fi
test "$status" -eq 1
python3 - "$fixture/attribution.json" "$linked" "$linked_b" <<'PY'
import json
import sys

report = json.load(open(sys.argv[1], encoding="utf-8"))
scoped = [item for item in report["findings"] if item["code"] == "GOV-WORKTREE-OVERLAP-002"]
assert len(scoped) == 1, [item["evidence"] for item in scoped]
evidence = scoped[0]["evidence"]
assert {evidence["left"], evidence["right"]} == {sys.argv[2], sys.argv[3]}, evidence
assert sorted(evidence["tickets"]) == ["ticket-010", "ticket-011"], evidence
PY

# --report writes the JSON verdict where a scheduled scan can leave it.
cp "$repo_root/worktree-guard.yaml" "$workspace/worktree-guard.yaml"
python3 "$guard" --root "$workspace" --config "$workspace/worktree-guard.yaml" \
  --checker "$checker" --once --format json \
  --report "$fixture/state/report.json" >/dev/null || true
python3 - "$fixture/state/report.json" <<'PY'
import json
import sys

report = json.load(open(sys.argv[1], encoding="utf-8"))
assert report["schema"] == "new-project.worktree-overlap-report/v1"
assert report["status"] in {"passed", "failed"}
PY

# The pyqual snippet is the contract between the runner and the installer.
python3 "$guard" --print-pyqual-stage > "$fixture/pyqual-snippet.json"
python3 - "$fixture/pyqual-snippet.json" <<'PY'
import json
import sys

snippet = json.load(open(sys.argv[1], encoding="utf-8"))
assert snippet["custom_tools"][0]["name"] == "worktree_guard"
assert snippet["custom_tools"][0]["allow_failure"] is False
assert snippet["stages"][0]["tool"] == "worktree_guard"
assert snippet["stages"][0]["optional"] is False
PY

# Installer: workspace units, plus a safe and idempotent pyqual insert.
if command -v systemd-escape >/dev/null 2>&1 && python3 -c "import yaml" >/dev/null 2>&1; then
  cat > "$fixture/pyqual.yaml" <<'YAML'
pipeline:
  name: fixture

  custom_tools:
    - name: existing
      binary: true
      command: true

  stages:
    - name: existing
      tool: existing
YAML
  XDG_DATA_HOME="$fixture/xdg/data" \
  XDG_STATE_HOME="$fixture/xdg/state" \
  XDG_CONFIG_HOME="$fixture/xdg/config" \
    "$repo_root/scripts/install-worktree-guard.sh" \
      --source "$repo_root" --workspace "$workspace" \
      --pyqual "$fixture/pyqual.yaml" --interval 300 > "$fixture/install.out"
  test -f "$fixture/xdg/config/systemd/user/worktree-guard@.service"
  test -f "$fixture/xdg/config/systemd/user/worktree-guard@.timer"
  test -f "$fixture/xdg/config/systemd/user/worktree-guard@.path"
  grep -q '^OnUnitActiveSec=300s$' "$fixture/xdg/config/systemd/user/worktree-guard@.timer"
  grep -q '^PathModified=%f/.worktrees$' "$fixture/xdg/config/systemd/user/worktree-guard@.path"
  python3 - "$fixture/pyqual.yaml" <<'PY'
import sys

import yaml

config = yaml.safe_load(open(sys.argv[1], encoding="utf-8"))
tools = [item["name"] for item in config["pipeline"]["custom_tools"]]
stages = [item["name"] for item in config["pipeline"]["stages"]]
assert tools == ["worktree_guard", "existing"], tools
assert stages == ["worktree-overlap", "existing"], stages
PY
  cp "$fixture/pyqual.yaml" "$fixture/pyqual.once.yaml"
  XDG_DATA_HOME="$fixture/xdg/data" \
  XDG_STATE_HOME="$fixture/xdg/state" \
  XDG_CONFIG_HOME="$fixture/xdg/config" \
    "$repo_root/scripts/install-worktree-guard.sh" \
      --source "$repo_root" --pyqual "$fixture/pyqual.yaml" > /dev/null
  cmp "$fixture/pyqual.once.yaml" "$fixture/pyqual.yaml"
fi

# A repository gate answers only for its own repository. A second, unrelated
# repository in the same workspace must not block it.
other="$workspace/other"
git init --quiet --initial-branch=main "$other"
git -C "$other" config user.email overlap-test@example.invalid
git -C "$other" config user.name overlap-test
printf '%s\n' other > "$other/other.py"
git -C "$other" add other.py
git -C "$other" commit --quiet -m initial
git -C "$other" remote add origin git@github.com:example/other.git
other_linked="$workspace/.worktrees/other-ticket-a"
git -C "$other" worktree add --quiet -b ticket/020 "$other_linked"
printf '%s\n' dirty-here > "$other/other.py"
printf '%s\n' dirty-there > "$other_linked/other.py"

# Unscoped: both repositories are reported.
python3 "$checker" --workspace-root "$workspace" --format json \
  > "$fixture/two-repos.json" || true
# Scoped to "other": the sample repository's findings disappear.
python3 "$checker" --workspace-root "$workspace" --identity-of "$other" \
  --format json > "$fixture/scoped.json" || true
python3 - "$fixture/two-repos.json" "$fixture/scoped.json" <<'PY'
import json
import sys

wide = json.load(open(sys.argv[1], encoding="utf-8"))
scoped = json.load(open(sys.argv[2], encoding="utf-8"))
identities = {item["evidence"]["identity"] for item in wide["findings"]}
assert identities == {
    "remote:github.com/example/sample",
    "remote:github.com/example/other",
}, identities
assert wide["scope"] == "workspace", wide["scope"]
assert scoped["scope"] == "remote:github.com/example/other", scoped["scope"]
assert {item["evidence"]["identity"] for item in scoped["findings"]} == {
    "remote:github.com/example/other"
}, scoped["findings"]
# Discovery is still workspace-wide; only reporting is narrowed.
assert scoped["summary"]["checkouts"] == wide["summary"]["checkouts"]
PY

# The runner picks repository scope on its own when --root is a checkout.
python3 "$guard" --root "$other" --config "$repo_root/worktree-guard.yaml" \
  --checker "$checker" --once --format json > "$fixture/auto-scope.json" || true
python3 - "$fixture/auto-scope.json" <<'PY'
import json
import sys

report = json.load(open(sys.argv[1], encoding="utf-8"))
assert report["scope"] == "remote:github.com/example/other", report["scope"]
PY

echo 'worktree overlap guard: PASS'
