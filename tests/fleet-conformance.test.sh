#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

fail() {
  echo "FAIL: $*" >&2
  exit 1
}

runner="$root/scripts/fleet_conformance.py"
[[ -x "$runner" ]] || fail "fleet conformance audit must be executable"

# One governed checkout whose declarations describe itself and nothing else.
make_repo() {
  local path="$1" owner_repo="$2"
  mkdir -p "$path/.governance" "$path/.github/workflows" "$path/project"
  git -C "$path" init --quiet
  git -C "$path" remote add origin "git@github.com:${owner_repo}.git"
  cat > "$path/.github/workflows/governance.yml" <<'EOF'
name: governance
jobs:
  enforce:
    name: governance / enforce
    steps:
      - run: bash project/governance-check.sh
EOF
  cat > "$path/.governance/required-checks.json" <<EOF
{
  "schema": "new-project.required-checks/v1",
  "version": 1,
  "repository": "${owner_repo}",
  "workflowFile": ".github/workflows/governance.yml",
  "requiredCheckNames": ["governance / enforce"]
}
EOF
  printf '#!/usr/bin/env bash\nexit 0\n' > "$path/project/governance-check.sh"
  chmod +x "$path/project/governance-check.sh"
}

clean="$tmp/fleet/own-instance"
make_repo "$clean" "wellmanifest/own-instance"
status=0
python3 "$runner" "$tmp/fleet" --format text > "$tmp/clean.out" 2>&1 || status=$?
[[ "$status" -eq 0 ]] || fail "a repository that describes itself must produce no error"
grep -Fq "1 governed checkouts, 0 errors" "$tmp/clean.out" \
  || fail "the clean baseline must be reported as clean: $(cat "$tmp/clean.out")"

# FLEET-INSTANCE-001: the seed was copied without adaptation, so the instance
# names the hub while living somewhere else. Measured in 30 checkouts.
foreign="$tmp/fleet/foreign"
make_repo "$foreign" "wellmanifest/foreign"
python3 - "$foreign" <<'PY'
import json, pathlib, sys
p = pathlib.Path(sys.argv[1]) / ".governance/required-checks.json"
d = json.loads(p.read_text())
d["repository"] = "wellmanifest/new-project"
p.write_text(json.dumps(d, indent=2) + "\n")
PY
status=0
python3 "$runner" "$foreign" --format text > "$tmp/foreign.out" 2>&1 || status=$?
[[ "$status" -eq 1 ]] || fail "a foreign instance identity must be an error"
grep -Fq 'FLEET-INSTANCE-001' "$tmp/foreign.out" || fail "expected FLEET-INSTANCE-001"
grep -Fq "declares repository 'wellmanifest/new-project'" "$tmp/foreign.out" \
  || fail "the finding must name both the declared and the real identity"

# FLEET-CHECK-002: a required name no workflow publishes can never turn green,
# so every pull request in that repository stays blocked.
phantom="$tmp/fleet/phantom"
make_repo "$phantom" "wellmanifest/phantom"
python3 - "$phantom" <<'PY'
import json, pathlib, sys
p = pathlib.Path(sys.argv[1]) / ".governance/required-checks.json"
d = json.loads(p.read_text())
d["requiredCheckNames"] = ["test", "windows-governance"]
p.write_text(json.dumps(d, indent=2) + "\n")
PY
status=0
python3 "$runner" "$phantom" --format text > "$tmp/phantom.out" 2>&1 || status=$?
[[ "$status" -eq 1 ]] || fail "an unprovidable required check must be an error"
grep -Fq 'FLEET-CHECK-002' "$tmp/phantom.out" || fail "expected FLEET-CHECK-002"
grep -Fq "publishes ['governance / enforce']" "$tmp/phantom.out" \
  || fail "the finding must report what the repository actually publishes"

# FLEET-GATE-004: the gate exists and nothing runs it, which reads as
# protection that is not there.
inert="$tmp/fleet/inert"
make_repo "$inert" "wellmanifest/inert"
cat > "$inert/.github/workflows/governance.yml" <<'EOF'
name: governance
jobs:
  enforce:
    name: governance / enforce
    steps:
      - run: echo nothing
EOF
python3 "$runner" "$inert" --format text > "$tmp/inert.out" 2>&1 || true
grep -Fq 'FLEET-GATE-004' "$tmp/inert.out" || fail "expected FLEET-GATE-004"
grep -Fq 'no workflow invokes' "$tmp/inert.out" || fail "gate finding must say why"

# FLEET-MANAGED-003: drift is measured against the repository's own pinned
# lock, so a matching digest is clean and a hand edit is not.
managed="$tmp/fleet/managed"
make_repo "$managed" "wellmanifest/managed"
printf 'managed body\n' > "$managed/AGENTS.md"
relock() {
  python3 - "$managed" <<'PY'
import hashlib, json, pathlib, sys
root = pathlib.Path(sys.argv[1])
body = (root / "AGENTS.md").read_bytes()
(root / ".governance/manifest.lock.json").write_text(json.dumps({
    "standard": {"sourceRevision": "a" * 40},
    "managedFiles": {"AGENTS.md": hashlib.sha256(body).hexdigest()},
}, indent=2) + "\n")
PY
}
relock
python3 "$runner" "$managed" --format text > "$tmp/managed.out" 2>&1 || true
grep -Fq 'FLEET-MANAGED-003' "$tmp/managed.out" \
  && fail "a managed file matching its own digest is not drift"
printf 'hand edited\n' > "$managed/AGENTS.md"
python3 "$runner" "$managed" --format text > "$tmp/drift.out" 2>&1 || true
grep -Fq 'FLEET-MANAGED-003' "$tmp/drift.out" || fail "expected FLEET-MANAGED-003"

# Selecting one rule must not silently report the others.
python3 "$runner" "$tmp/fleet" --code FLEET-GATE-004 --format json > "$tmp/one.json" 2>&1 || true
python3 - "$tmp/one.json" <<'PY'
import json, sys
report = json.load(open(sys.argv[1]))
codes = {item["code"] for item in report["findings"]}
assert codes <= {"FLEET-GATE-004"}, f"rule selection leaked {codes}"
assert report["schema"] == "new-project.fleet-conformance-report/v1"
PY

# The rule set is data: every declared check must have an implementation, and
# every implementation must be reachable from the rules.
python3 - "$root" <<'PY'
import json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(sys.argv[1]) / "scripts"))
import fleet_conformance as fc
rules = json.loads(
    (pathlib.Path(sys.argv[1]) / "governance/fleet-conformance.rules.json").read_text()
)["rules"]
declared = {rule["check"] for rule in rules}
assert declared <= set(fc.CHECKS), f"rule names an unimplemented check: {declared - set(fc.CHECKS)}"
assert set(fc.CHECKS) <= declared, f"implementation is unreachable from rules: {set(fc.CHECKS) - declared}"
codes = [rule["code"] for rule in rules]
assert len(codes) == len(set(codes)), "duplicate rule codes"
for rule in rules:
    assert rule["severity"] in {"error", "warning"}, rule
    assert rule["remediation"].strip(), rule
PY

echo "fleet conformance audit: OK"
