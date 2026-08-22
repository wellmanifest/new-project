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
grep -Fq 'new-ticket.sh' "$root/GEMINI.md" || fail "GEMINI.md must require new-ticket.sh"
grep -Fq 'new-ticket.sh' "$root/CLAUDE.md" || fail "CLAUDE.md must require new-ticket.sh"
grep -Fq 'alwaysApply: true' "$root/.cursor/rules/new-project-standard.mdc" || fail "Cursor rule must alwaysApply"

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
[[ "$(git -C "$tmp/adopter" config --get core.hooksPath)" == ".githooks" ]] || fail "installer must set core.hooksPath"

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
git -C "$tmp/adopter" commit -qm "bound to ticket-001" || fail "IN_PROGRESS ticket branch must commit"

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

# A terminal ticket may publish only its own closure evidence and the two
# repository-level governance indexes plus the exact generated artifact receipt.
sed -i 's/IN_PROGRESS/DONE/' "$tmp/adopter/project/ticket-001/README.md"
printf '%s\n' '# TODO' '- [x] ticket-001: DONE / DONE' > "$tmp/adopter/TODO.md"
mkdir -p "$tmp/adopter/project"
printf '%s\n' '# Tickets' '- ticket-001' > "$tmp/adopter/project/TICKETS.md"
mkdir -p "$tmp/adopter/config"
printf '%s\n' '{"schema":"fixture.artifact-registry/v1"}' > \
  "$tmp/adopter/config/artifact-registry.json"
git -C "$tmp/adopter" add project/ticket-001/README.md TODO.md project/TICKETS.md \
  config/artifact-registry.json
git -C "$tmp/adopter" commit -qm "close ticket-001" || fail "DONE governance-only closure must commit"

printf '%s\n' 'terminal evidence update' >> "$tmp/adopter/project/ticket-001/README.md"
printf '%s\n' '{"schema":"fixture.other/v1"}' > "$tmp/adopter/config/other-generated.json"
git -C "$tmp/adopter" add project/ticket-001/README.md config/other-generated.json
if git -C "$tmp/adopter" commit -qm "foreign generated closure"; then
  fail "DONE closure must reject non-receipt config paths"
fi
git -C "$tmp/adopter" reset -q --hard HEAD

echo "implementation after close" >> "$tmp/adopter/README.md"
git -C "$tmp/adopter" add README.md
if git -C "$tmp/adopter" commit -qm "closed implementation"; then
  fail "DONE ticket must reject implementation"
fi
git -C "$tmp/adopter" reset -q --hard HEAD

mkdir -p "$tmp/adopter/project/ticket-002"
printf '%s\n' '# Foreign ticket' '- **Status**: DONE' > "$tmp/adopter/project/ticket-002/README.md"
git -C "$tmp/adopter" add project/ticket-002/README.md
if git -C "$tmp/adopter" commit -qm "foreign closure"; then
  fail "DONE ticket must reject foreign ticket evidence"
fi
git -C "$tmp/adopter" reset -q --hard HEAD

git -C "$tmp/adopter" rm -q TODO.md
if git -C "$tmp/adopter" commit -qm "delete closure index"; then
  fail "DONE ticket must reject deletions"
fi
git -C "$tmp/adopter" reset -q --hard HEAD

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
for host in AGENTS.md CLAUDE.md GEMINI.md; do
  printf '%s\n' "stub" > "$fixture/$host"
done
printf '%s\n' "stub" > "$fixture/.cursor/rules/new-project-standard.mdc"
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
