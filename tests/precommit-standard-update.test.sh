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
grep -Fq 'run_standard_update_controller' "$root/template/files/pre-commit.template.sh" \
  || fail "managed hook must compose the standard update controller"

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
