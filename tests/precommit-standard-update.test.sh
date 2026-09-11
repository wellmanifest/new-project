#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

fail() {
  echo "FAIL: $*" >&2
  exit 1
}

runner="$root/scripts/precommit_standard_update.py"
[[ -x "$runner" ]] || fail "standard update controller must be executable"
python3 "$root/tests/precommit-local-pin.test.py"

mkdir -p "$tmp/plain" "$tmp/adopter/.governance" "$tmp/fakebin"
python3 "$runner" --root "$tmp/plain" --ticket ticket-184 \
  || fail "repository without an adoption must remain compatible"
printf '{}\n' > "$tmp/adopter/.governance/standard-adoption.json"

cat > "$tmp/fakebin/goal" <<'EOF'
#!/usr/bin/env bash
printf '%s\n' "$*" > "$GOAL_ARGS_CAPTURE"
exit "${GOAL_EXIT_CODE:-0}"
EOF
chmod +x "$tmp/fakebin/goal"

cat > "$tmp/fakebin/koru" <<'EOF'
#!/usr/bin/env bash
printf '%s\n' "$*" > "$KORU_ARGS_CAPTURE"
exit "${KORU_EXIT_CODE:-0}"
EOF
chmod +x "$tmp/fakebin/koru"

GOAL_ARGS_CAPTURE="$tmp/goal.args" PATH="$tmp/fakebin:$PATH" \
  python3 "$runner" --root "$tmp/adopter" --ticket ticket-184
grep -Fxq "governance adopt --latest --pre-commit --target-root $tmp/adopter --ticket ticket-184" \
  "$tmp/goal.args" || fail "controller must pass the exact bounded Goal protocol"

status=0
GOAL_ARGS_CAPTURE="$tmp/goal.args" GOAL_EXIT_CODE=3 PATH="$tmp/fakebin:$PATH" \
  python3 "$runner" --root "$tmp/adopter" --ticket ticket-184 \
  > "$tmp/refusal.out" 2> "$tmp/refusal.err" || status=$?
[[ "$status" -eq 3 ]] || fail "controller must preserve Goal's non-zero result"
grep -Fq 'GOV-STANDARD-UPDATE-001' "$tmp/refusal.err" \
  || fail "Goal refusal must expose the canonical diagnostic"

cat > "$tmp/adopter/.governance/standard-adoption.json" <<'EOF'
{
  "updates": {
    "enabled": false,
    "trigger": "pre-commit",
    "action": "prepare-and-abort",
    "executor": "goal"
  }
}
EOF
rm -f "$tmp/goal.args"
GOAL_ARGS_CAPTURE="$tmp/goal.args" PATH="$tmp/fakebin:$PATH" \
  python3 "$runner" --root "$tmp/adopter" --ticket ticket-184
[[ ! -e "$tmp/goal.args" ]] || fail "disabled policy must not invoke Goal"

cat > "$tmp/adopter/.governance/standard-adoption.json" <<'EOF'
{
  "updates": {
    "enabled": true,
    "trigger": "pre-commit",
    "action": "prepare-and-abort",
    "executor": "koru-goal"
  }
}
EOF
KORU_ARGS_CAPTURE="$tmp/koru.args" PATH="$tmp/fakebin:$PATH" \
  python3 "$runner" --root "$tmp/adopter" --ticket ticket-184
grep -Fxq "goal --project $tmp/adopter --goal-executable $tmp/fakebin/goal -- governance adopt --latest --pre-commit --target-root $tmp/adopter --ticket ticket-184" \
  "$tmp/koru.args" || fail "Koru executor must supervise the exact Goal protocol"

printf '{ invalid\n' > "$tmp/adopter/.governance/standard-adoption.json"
status=0
PATH="$tmp/fakebin:$PATH" python3 "$runner" \
  --root "$tmp/adopter" --ticket ticket-184 \
  > "$tmp/config.out" 2> "$tmp/config.err" || status=$?
[[ "$status" -eq 2 ]] || fail "invalid update configuration must fail closed"
grep -Fq 'GOV-STANDARD-UPDATE-001' "$tmp/config.err" \
  || fail "invalid configuration must expose the canonical diagnostic"

python3 - "$root" <<'PY'
import json
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
manifest = json.loads((root / "governance/package-manifest.json").read_text())
bindings = {entry["target"]: entry for entry in manifest["files"]}
assert bindings[".governance/precommit_standard_update.py"] == {
    "source": "scripts/precommit_standard_update.py",
    "target": ".governance/precommit_standard_update.py",
    "strategy": "managed",
    "executable": True,
}
assert ".governance/error/GOV-STANDARD-UPDATE.md" in bindings

schema = json.loads((root / "governance/standard-adoption.schema.json").read_text())
updates = schema["properties"]["updates"]
assert updates["properties"]["executor"]["enum"] == ["goal", "koru-goal"]
default = json.loads((root / "governance/standard-adoption.default.json").read_text())
assert default["updates"] == {
    "enabled": True,
    "trigger": "pre-commit",
    "action": "prepare-and-abort",
    "executor": "goal",
}
PY

# Staleness is not drift. The standard published seven revisions on 2026-09-08;
# an implementation ticket can never be the governance adoption ticket Goal
# demands, so the gate held five clean pull-request repairs in one adopter for a
# full day. A commit that leaves every managed file matching its own pinned lock
# has caused nothing and now proceeds with the staleness reported.
drift_repo="$tmp/drift"
mkdir -p "$drift_repo/.governance" "$tmp/stalebin"
git -C "$drift_repo" init --quiet
printf '{}\n' > "$drift_repo/.governance/standard-adoption.json"
printf 'managed contract body\n' > "$drift_repo/AGENTS.md"

cat > "$tmp/stalebin/goal" <<'EOF'
#!/usr/bin/env bash
echo "Error: GOV-STANDARD-UPDATE-001: pre-commit standard update requires a staged governance adoption intent binding aaa to bbb in ticket-058" >&2
exit 1
EOF
chmod +x "$tmp/stalebin/goal"

cat > "$tmp/stalebin/broken-goal" <<'EOF'
#!/usr/bin/env bash
echo "Error: the requested standard revision does not publish VERSION" >&2
exit 1
EOF
chmod +x "$tmp/stalebin/broken-goal"

relock() {
  python3 - "$drift_repo" <<'PY'
import hashlib, json, pathlib, sys
root = pathlib.Path(sys.argv[1])
body = (root / "AGENTS.md").read_bytes()
(root / ".governance/manifest.lock.json").write_text(json.dumps({
    "standard": {"sourceRevision": "a" * 40, "version": "0.20.9"},
    "managedFiles": {"AGENTS.md": hashlib.sha256(body).hexdigest()},
}, indent=2) + "\n", encoding="utf-8")
PY
  git -C "$drift_repo" add -A
}

relock
status=0
PATH="$tmp/stalebin:$PATH" python3 "$runner" --root "$drift_repo" --ticket ticket-058 \
  > "$tmp/stale.out" 2> "$tmp/stale.err" || status=$?
[[ "$status" -eq 0 ]] || fail "a stale pin without managed drift must not block an unrelated commit"
grep -Fq 'no managed file drifted' "$tmp/stale.err" \
  || fail "the allowed commit must still report the staleness it did not cause"

printf 'hand edited managed contract\n' > "$drift_repo/AGENTS.md"
git -C "$drift_repo" add -A
status=0
PATH="$tmp/stalebin:$PATH" python3 "$runner" --root "$drift_repo" --ticket ticket-058 \
  > "$tmp/drift.out" 2> "$tmp/drift.err" || status=$?
[[ "$status" -eq 1 ]] || fail "managed drift must keep failing closed"
grep -Fq 'GOV-STANDARD-UPDATE-001' "$tmp/drift.err" \
  || fail "a drifted refusal must expose the canonical diagnostic"

relock
status=0
PATH="$tmp/stalebin:$PATH" python3 "$runner" --root "$drift_repo" --ticket ticket-058 \
  --goal-executable broken-goal > "$tmp/other.out" 2> "$tmp/other.err" || status=$?
[[ "$status" -eq 1 ]] || fail "a refusal that is not adoption authorization must stay closed"

git -C "$drift_repo" rm --cached --quiet .governance/manifest.lock.json
status=0
PATH="$tmp/stalebin:$PATH" python3 "$runner" --root "$drift_repo" --ticket ticket-058 \
  > "$tmp/nolock.out" 2> "$tmp/nolock.err" || status=$?
[[ "$status" -eq 1 ]] || fail "evidence that cannot be read must never relax the gate"
