#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

fail() {
  echo "FAIL: $*" >&2
  exit 1
}

[[ -x "$root/scripts/install-agent-hosts.sh" ]] || fail "installer must be executable"
[[ -x "$root/.githooks/pre-commit" ]] || fail "hook must be executable"
grep -Fq 'GOV-AGENT-HOST-001' "$root/.githooks/pre-commit" || fail "hook must emit GOV-AGENT-HOST-001"
grep -Fq 'verify-pin --root "$root" --staged' "$root/template/files/pre-commit.template.sh" \
  || fail "managed hook must validate the staged local standard pin"
! grep -Eq 'git[[:space:]]+(fetch|pull)' "$root/template/files/pre-commit.template.sh" \
  || fail "managed pre-commit must never fetch or pull"
grep -Fq 'new-ticket.sh' "$root/GEMINI.md" || fail "GEMINI.md must require new-ticket.sh"
grep -Fq 'new-ticket.sh' "$root/CLAUDE.md" || fail "CLAUDE.md must require new-ticket.sh"
grep -Fq 'alwaysApply: true' "$root/.cursor/rules/new-project-standard.mdc" || fail "Cursor rule must alwaysApply"

mapfile -t closed_statuses < <(python3 - "$root" <<'PY'
import json
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
hub = json.loads((root / "governance/manifest.hub.json").read_text())
default = json.loads((root / "governance/manifest.default.json").read_text())
hub_statuses = hub["ticket"]["closedStatuses"]
default_statuses = default["ticket"]["closedStatuses"]
if hub_statuses != default_statuses:
    raise SystemExit("hub and adopter manifests declare different closedStatuses")
print("\n".join(hub_statuses))
PY
)
[[ "${closed_statuses[*]}" == "DONE CANCELLED" ]] \
  || fail "terminal hook regression must cover every declared closed status"
for closed_status in "${closed_statuses[@]}"; do
  grep -Fq "$closed_status" "$root/.githooks/pre-commit" \
    || fail "hub hook must recognize declared terminal status $closed_status"
  grep -Fq "$closed_status" "$root/template/files/pre-commit.template.sh" \
    || fail "adopter hook must recognize declared terminal status $closed_status"
done

mapfile -t non_active_statuses < <(python3 - "$root" <<'PY'
import json
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
hub = json.loads((root / "governance/manifest.hub.json").read_text())
default = json.loads((root / "governance/manifest.default.json").read_text())
hub_statuses = hub["ticket"]["nonActiveStatuses"]
default_statuses = default["ticket"]["nonActiveStatuses"]
if hub_statuses != default_statuses:
    raise SystemExit("hub and adopter manifests declare different nonActiveStatuses")
print("\n".join(hub_statuses))
PY
)
[[ "${non_active_statuses[*]}" == "BACKLOG PLAN BLOCKED" ]] \
  || fail "non-active hook regression must cover every declared non-active status"
for non_active_status in "${non_active_statuses[@]}"; do
  grep -Fq "$non_active_status" "$root/.githooks/pre-commit" \
    || fail "hub hook must recognize declared non-active status $non_active_status"
  grep -Fq "$non_active_status" "$root/template/files/pre-commit.template.sh" \
    || fail "adopter hook must recognize declared non-active status $non_active_status"
done

python3 - "$root" <<'PY'
import json
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
package = json.loads((root / "governance/package-manifest.json").read_text())
findings = []
for entry in package["files"]:
    if entry["strategy"] not in {"managed", "extendable"}:
        continue
    source = root / entry["source"]
    for number, line in enumerate(source.read_bytes().splitlines(), start=1):
        if line.endswith((b" ", b"\t")):
            findings.append(f"{entry['source']}:{number}")
if findings:
    print("managed package sources contain trailing whitespace:", file=sys.stderr)
    print("\n".join(findings), file=sys.stderr)
    raise SystemExit(1)
PY

git init -q "$tmp/adopter"
git -C "$tmp/adopter" config user.email "test@example.com"
git -C "$tmp/adopter" config user.name "Test"
git -C "$tmp/adopter" config commit.gpgsign false
echo "readme" > "$tmp/adopter/README.md"
git -C "$tmp/adopter" add README.md
git -C "$tmp/adopter" commit -qm "seed"
"$root/scripts/install-agent-hosts.sh" --source "$root" --target "$tmp/adopter"
[[ -f "$tmp/adopter/GEMINI.md" ]] || fail "installer must copy GEMINI.md"
[[ -f "$tmp/adopter/CLAUDE.md" ]] || fail "installer must copy CLAUDE.md"
[[ -x "$tmp/adopter/.githooks/pre-commit" ]] || fail "installer must copy executable hook"
[[ -f "$tmp/adopter/.governance/worktree_guard.py" ]] || fail "installer must copy worktree guard"
[[ "$(git -C "$tmp/adopter" config --get core.hooksPath)" == ".githooks" ]] || fail "installer must set core.hooksPath"

# Replace the real runner with a deterministic spy. The overlap algorithm has
# its own suite; this fixture proves the managed lifecycle hook composes it into
# every successful path and propagates a negative verdict.
cat > "$tmp/adopter/.governance/worktree_guard.py" <<'PY'
from pathlib import Path
import sys

root = Path(__file__).resolve().parents[1]
counter = root / ".guard-invocations"
count = int(counter.read_text(encoding="utf-8")) if counter.exists() else 0
counter.write_text(str(count + 1), encoding="utf-8")
if (root / ".guard-fail").exists():
    print("GOV-WORKTREE-OVERLAP-FAIL: deterministic fixture rejection", file=sys.stderr)
    raise SystemExit(1)
PY

echo "change" >> "$tmp/adopter/README.md"
git -C "$tmp/adopter" add README.md
if git -C "$tmp/adopter" commit -qm "unbound"; then
  fail "commit on main without a ticket must be rejected"
fi
git -C "$tmp/adopter" checkout -qb ticket/001-demo
if git -C "$tmp/adopter" commit -qm "missing ticket dir"; then
  fail "ticket branch without project/ticket-001 must be rejected"
fi

mkdir -p "$tmp/adopter/project/ticket-001"
cat > "$tmp/adopter/project/ticket-001/README.md" <<'EOF'
# Ticket 001

- **Status**: BACKLOG
EOF
git -C "$tmp/adopter" add project/ticket-001/README.md README.md
if git -C "$tmp/adopter" commit -qm "not in progress"; then
  fail "BACKLOG ticket must be rejected"
fi

sed -i 's/BACKLOG/IN_PROGRESS/' "$tmp/adopter/project/ticket-001/README.md"
git -C "$tmp/adopter" add project/ticket-001/README.md README.md

touch "$tmp/adopter/.guard-fail"
if git -C "$tmp/adopter" commit -qm "overlap verdict bypass" 2> "$tmp/guard-fail.err"; then
  fail "negative worktree guard verdict must reject an IN_PROGRESS commit"
fi
grep -Fq 'GOV-WORKTREE-OVERLAP-FAIL' "$tmp/guard-fail.err" \
  || fail "negative guard verdict must remain visible"
[[ "$(cat "$tmp/adopter/.guard-invocations")" == "1" ]] \
  || fail "IN_PROGRESS path must invoke the guard before rejecting"
rm "$tmp/adopter/.guard-fail"
git -C "$tmp/adopter" commit -qm "bound to ticket-001" || fail "IN_PROGRESS ticket branch must commit"
[[ "$(cat "$tmp/adopter/.guard-invocations")" == "2" ]] \
  || fail "IN_PROGRESS success must invoke the guard"

for non_active_status in "${non_active_statuses[@]}"; do
  sed -i "s/IN_PROGRESS/$non_active_status/" "$tmp/adopter/project/ticket-001/README.md"
  git -C "$tmp/adopter" add project/ticket-001/README.md
  git -C "$tmp/adopter" commit -qm "pause ticket-001 as $non_active_status" \
    || fail "$non_active_status governance-only transition must commit"

  echo "implementation while $non_active_status" >> "$tmp/adopter/README.md"
  git -C "$tmp/adopter" add README.md
  if git -C "$tmp/adopter" commit -qm "non-active implementation"; then
    fail "$non_active_status ticket must reject implementation"
  fi
  git -C "$tmp/adopter" reset -q --hard HEAD

  sed -i "s/$non_active_status/IN_PROGRESS/" "$tmp/adopter/project/ticket-001/README.md"
  git -C "$tmp/adopter" add project/ticket-001/README.md
  git -C "$tmp/adopter" commit -qm "resume ticket-001 from $non_active_status" \
    || fail "IN_PROGRESS resume from $non_active_status must commit"
done
[[ "$(cat "$tmp/adopter/.guard-invocations")" == "8" ]] \
  || fail "non-active transitions and resumes must invoke the guard"

# The pin validator reads only the local staged manifest, lock and managed
# digests. A command spy proves that no fetch/pull is attempted, and the check
# leaves both HEAD and the index/worktree status unchanged.
pinrepo="$tmp/pinrepo"
mkdir -p "$pinrepo/.subactor" "$pinrepo/.governance" "$tmp/fakebin"
git init -q "$pinrepo"
git -C "$pinrepo" config user.email "test@example.com"
git -C "$pinrepo" config user.name "Test"
cp "$root/.subactor/manifest.json" "$pinrepo/.subactor/manifest.json"
cp "$root/.subactor/.gitignore" "$pinrepo/.subactor/.gitignore"
cp "$root/scripts/work_continuity.py" "$pinrepo/.governance/work_continuity.py"
python3 - "$pinrepo" <<'PY'
import hashlib
import json
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
managed = {}
for relative in ('.subactor/manifest.json', '.subactor/.gitignore'):
    managed[relative] = hashlib.sha256((root / relative).read_bytes()).hexdigest()
lock = {
    'schema': 'new-project.lock/v1',
    'standard': {
        'id': 'wellmanifest/new-project',
        'version': '0.20.2',
        'sourceRepository': 'wellmanifest/new-project',
        'sourceRevision': '1' * 40,
        'publicationStatus': 'published',
    },
    'managedFiles': managed,
}
(root / '.governance/manifest.lock.json').write_text(
    json.dumps(lock, indent=2) + '\n', encoding='utf-8'
)
PY
git -C "$pinrepo" add .
real_git="$(command -v git)"
cat > "$tmp/fakebin/git" <<EOF
#!/usr/bin/env bash
printf '%s\n' "\$*" >> "\$GIT_TRACE_ARGS"
exec "$real_git" "\$@"
EOF
chmod +x "$tmp/fakebin/git"
pin_trace="$tmp/pin-git-commands"
before_pin_status="$(git -C "$pinrepo" status --porcelain=v1)"
before_pin_head="$(git -C "$pinrepo" rev-parse --verify HEAD 2>/dev/null || true)"
GIT_TRACE_ARGS="$pin_trace" PATH="$tmp/fakebin:$PATH" \
  python3 "$pinrepo/.governance/work_continuity.py" verify-pin \
    --root "$pinrepo" --staged > "$tmp/pin-pass.json"
grep -q '"networkAccess": false' "$tmp/pin-pass.json"
grep -q '"mutated": false' "$tmp/pin-pass.json"
! grep -Eq '(^| )(fetch|pull)( |$)' "$pin_trace" || fail "pin validation used the network"
[[ "$(git -C "$pinrepo" status --porcelain=v1)" == "$before_pin_status" ]] \
  || fail "pin validation mutated index or worktree"
[[ "$(git -C "$pinrepo" rev-parse --verify HEAD 2>/dev/null || true)" == "$before_pin_head" ]] \
  || fail "pin validation mutated HEAD"

python3 - "$pinrepo/.subactor/manifest.json" <<'PY'
import json
import sys
path = sys.argv[1]
value = json.load(open(path, encoding='utf-8'))
value['continuity']['checkpointIndexMaxEntries'] = 1
open(path, 'w', encoding='utf-8').write(json.dumps(value, indent=2) + '\n')
PY
git -C "$pinrepo" add .subactor/manifest.json
status=0
python3 "$pinrepo/.governance/work_continuity.py" verify-pin \
  --root "$pinrepo" --staged > "$tmp/pin-drift.out" 2> "$tmp/pin-drift.err" || status=$?
test "$status" -eq 2
grep -Fq 'GOV-CONTINUITY-001' "$tmp/pin-drift.err"

# Status authority comes from the staged snapshot. An unstaged IN_PROGRESS
# working-tree value must not authorize a staged BACKLOG ticket plus source.
sed -i 's/IN_PROGRESS/BACKLOG/' "$tmp/adopter/project/ticket-001/README.md"
git -C "$tmp/adopter" add project/ticket-001/README.md
sed -i 's/BACKLOG/IN_PROGRESS/' "$tmp/adopter/project/ticket-001/README.md"
echo "staged bypass" >> "$tmp/adopter/README.md"
git -C "$tmp/adopter" add README.md
if git -C "$tmp/adopter" commit -qm "staged status bypass"; then
  fail "unstaged IN_PROGRESS must not override staged BACKLOG"
fi
git -C "$tmp/adopter" reset -q --hard HEAD

# Tracking carriers cannot manufacture a repository delivery on their own.
printf '%s\n' 'status-only evidence' >> "$tmp/adopter/project/ticket-001/README.md"
git -C "$tmp/adopter" add project/ticket-001/README.md
if git -C "$tmp/adopter" commit -qm "ticket-only status" 2> "$tmp/tracking-only.err"; then
  fail "ticket-only commit must be rejected"
fi
grep -Fq 'GOV-AGENT-HOST-007' "$tmp/tracking-only.err" \
  || fail "ticket-only rejection must expose GOV-AGENT-HOST-007"
git -C "$tmp/adopter" reset -q --hard HEAD

# Terminal state belongs to the protected external receipt. Neither a
# governance-only payload nor a material payload may create a closure commit.
for terminal_status in DONE CANCELLED; do
  sed -i "s/IN_PROGRESS/$terminal_status/" "$tmp/adopter/project/ticket-001/README.md"
  echo "attempted $terminal_status closure" >> "$tmp/adopter/README.md"
  git -C "$tmp/adopter" add project/ticket-001/README.md README.md
  if git -C "$tmp/adopter" commit -qm "terminal closure $terminal_status" 2> "$tmp/terminal.err"; then
    fail "$terminal_status repository closure must be rejected"
  fi
  grep -Fq 'GOV-AGENT-HOST-003' "$tmp/terminal.err" \
    || fail "$terminal_status closure must expose GOV-AGENT-HOST-003"
  git -C "$tmp/adopter" reset -q --hard HEAD
done

user_home="$tmp/home"
mkdir -p "$user_home"
HOME="$user_home" "$root/scripts/install-agent-hosts.sh" --source "$root" --user
[[ -f "$user_home/.cursor/rules/new-project-standard.mdc" ]] || fail "--user must install Cursor rule"
grep -Fq 'wellmanifest/new-project host contract' "$user_home/.gemini/GEMINI.md" || fail "--user must install Gemini pointer"
grep -Fq 'wellmanifest/new-project host contract' "$user_home/.claude/CLAUDE.md" || fail "--user must install Claude pointer"

# --- ticket-106: deterministic host and packaging validator -------------------

checker="$root/scripts/agent_host_check.py"
[[ -f "$checker" ]] || fail "agent_host_check.py must exist"

# The validator exits non-zero on findings, which is the behaviour under test;
# capture the report first so pipefail does not abort the suite.
codes() {
  local report="$tmp/agent-host-report.json"
  python3 "$checker" --root "$1" --actor "${2:-agent}" --format json > "$report" || true
  python3 -c 'import json,sys; print(" ".join(f["code"] for f in json.load(open(sys.argv[1]))["findings"]))' "$report"
}

assert_has() {
  local haystack="$1" needle="$2" context="$3"
  [[ "$haystack" == *"$needle"* ]] || fail "$context: expected $needle in '$haystack'"
}

assert_lacks() {
  local haystack="$1" needle="$2" context="$3"
  [[ "$haystack" != *"$needle"* ]] || fail "$context: unexpected $needle in '$haystack'"
}

fixture="$tmp/fixture"
mkdir -p "$fixture/.governance" "$fixture/.cursor/rules" "$fixture/.githooks"
git init -q "$fixture"
git -C "$fixture" config user.email "test@example.com"
git -C "$fixture" config user.name "Test"
cp "$root/governance/agent-hosts.json" "$fixture/.governance/agent-hosts.json"
# Derive the fixture's host files from the contract, so adding a host to
# agent-hosts.json cannot silently leave this fixture behind.
while read -r host_file; do
  mkdir -p "$fixture/$(dirname "$host_file")"
  printf '%s\n' "stub" > "$fixture/$host_file"
done < <(python3 -c '
import json, sys
contract = json.load(open(sys.argv[1], encoding="utf-8"))
print("\n".join(host["file"] for host in contract["hosts"]))
' "$fixture/.governance/agent-hosts.json")
printf '%s\n' '#!/usr/bin/env bash' > "$fixture/.githooks/pre-commit"
chmod +x "$fixture/.githooks/pre-commit"
cat > "$fixture/.governance/manifest.lock.json" <<'LOCK'
{
  "schema": "new-project.lock/v1",
  "standard": {
    "id": "wellmanifest/new-project",
    "publicationStatus": "published",
    "sourceRepository": "wellmanifest/new-project",
    "sourceRevision": "1111111111111111111111111111111111111111",
    "version": "9.9.9"
  },
  "managedFiles": {}
}
LOCK

# An unset core.hooksPath means no commit in this clone is actually gated.
assert_has "$(codes "$fixture")" "GOV-AGENT-HOST-006" "unset hooksPath"
# CI checkouts never run local hooks, so that finding must not fire there.
assert_lacks "$(codes "$fixture" ci)" "GOV-AGENT-HOST-006" "ci actor"

git -C "$fixture" config core.hooksPath .githooks
[[ -z "$(codes "$fixture")" ]] || fail "activated fixture must pass: $(codes "$fixture")"

# A missing host instruction file fails closed.
mv "$fixture/GEMINI.md" "$fixture/GEMINI.md.bak"
assert_has "$(codes "$fixture")" "GOV-AGENT-HOST-004" "missing host file"
mv "$fixture/GEMINI.md.bak" "$fixture/GEMINI.md"

# Bootstrap into a fresh clone must deliver the contract too, not only the
# instruction files: without it the target cannot be activated at all.
[[ -f "$tmp/adopter/.governance/agent-hosts.json" ]] || fail "bootstrap must copy the host contract"
[[ -f "$tmp/adopter/.cursor/rules/new-project-standard.mdc" ]] \
  || fail "bootstrap must copy every declared host file"

# A hook that cannot execute is the same defect as a hook that is absent.
chmod -x "$fixture/.githooks/pre-commit"
assert_has "$(codes "$fixture")" "GOV-AGENT-HOST-005" "non-executable hook"
chmod +x "$fixture/.githooks/pre-commit"

# A stack marker with no governance declaration and no lifecycle binding.
cat > "$fixture/pyproject.toml" <<'TOML'
[project]
name = "fixture"
version = "0.1.0"
TOML
observed="$(codes "$fixture")"
assert_has "$observed" "GOV-PACKAGING-001" "undeclared pyproject"
assert_has "$observed" "GOV-PACKAGING-003" "unbound pytest lifecycle"

# A declaration that drifted away from the adoption lock.
cat > "$fixture/pyproject.toml" <<'TOML'
[project]
name = "fixture"
version = "0.1.0"

[tool.wellmanifest]
standard = "0.0.1"
revision = "1111111111111111111111111111111111111111"
gate = "project/governance-check.sh"

[tool.pytest.ini_options]
addopts = "-p wellmanifest_governance"
TOML
mkdir -p "$fixture/project"
printf '%s\n' '#!/usr/bin/env bash' > "$fixture/project/governance-check.sh"
observed="$(codes "$fixture")"
assert_has "$observed" "GOV-PACKAGING-002" "drifted standard version"
assert_lacks "$observed" "GOV-PACKAGING-003" "bound pytest lifecycle"

# The same declaration in agreement with the lock passes.
sed -i 's/standard = "0.0.1"/standard = "9.9.9"/' "$fixture/pyproject.toml"
[[ -z "$(codes "$fixture")" ]] || fail "aligned pyproject must pass: $(codes "$fixture")"

# npm is the one ecosystem that can install the hook without being asked.
cat > "$fixture/package.json" <<'JSON'
{
  "name": "fixture",
  "version": "0.1.0",
  "wellmanifest": {
    "standard": "9.9.9",
    "revision": "1111111111111111111111111111111111111111",
    "gate": "project/governance-check.sh"
  }
}
JSON
assert_has "$(codes "$fixture")" "GOV-PACKAGING-003" "missing npm prepare"
python3 - "$fixture/package.json" <<'PYNPM'
import json, sys
path = sys.argv[1]
document = json.load(open(path, encoding="utf-8"))
document["scripts"] = {"prepare": "./scripts/install-agent-hosts.sh"}
json.dump(document, open(path, "w", encoding="utf-8"), indent=2)
PYNPM
[[ -z "$(codes "$fixture")" ]] || fail "aligned package.json must pass: $(codes "$fixture")"

# Every code the validator can emit must be registered in the catalog.
python3 "$root/scripts/audit_diagnostics.py" --root "$root" >/dev/null \
  || fail "diagnostics catalog must cover every emitted code"

echo "agent-hosts.test.sh OK"
