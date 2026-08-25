#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

fail() {
  echo "FAIL: $*" >&2
  exit 1
}

fixture="$tmp/adopter"
git init -q "$fixture"
git -C "$fixture" config user.email "test@example.com"
git -C "$fixture" config user.name "Test"
mkdir -p "$fixture/project"
cp "$root/template/files/wellmanifest_governance.py" "$fixture/"
cat > "$fixture/project/governance-check.sh" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
printf '%s\n' "$@" > .governance-arguments
count=0
[[ ! -f .governance-invocations ]] || count="$(cat .governance-invocations)"
printf '%s\n' "$((count + 1))" > .governance-invocations
[[ ! -f .governance-reject ]]
EOF
chmod +x "$fixture/project/governance-check.sh"
printf '%s\n' seed > "$fixture/tracked.txt"
git -C "$fixture" add tracked.txt
git -C "$fixture" commit -qm seed
base="$(git -C "$fixture" rev-parse HEAD)"
printf '%s\n' staged > "$fixture/staged.txt"
git -C "$fixture" add staged.txt

(
  cd "$fixture"
  python3 - <<'PY'
from pathlib import Path
from types import SimpleNamespace
import wellmanifest_governance

session = SimpleNamespace(config=SimpleNamespace(rootpath=Path.cwd()))
wellmanifest_governance.pytest_sessionstart(session)
PY
)
[[ "$(cat "$fixture/.governance-invocations")" == "1" ]] \
  || fail "plugin must invoke governance exactly once"
grep -Fxq -- "--base" "$fixture/.governance-arguments" \
  || fail "plugin must pass an explicit base"
grep -Fxq -- "$base" "$fixture/.governance-arguments" \
  || fail "plugin must bind the current base SHA"
grep -Fxq -- "--changed-file" "$fixture/.governance-arguments" \
  || fail "plugin must pass changed-file evidence"
grep -Fxq -- "staged.txt" "$fixture/.governance-arguments" \
  || fail "plugin must include staged paths"

touch "$fixture/.governance-reject"
if (
  cd "$fixture"
  python3 - <<'PY'
from pathlib import Path
from types import SimpleNamespace
import wellmanifest_governance

session = SimpleNamespace(config=SimpleNamespace(rootpath=Path.cwd()))
wellmanifest_governance.pytest_sessionstart(session)
PY
); then
  fail "negative governance verdict must stop the pytest lifecycle"
fi
[[ "$(cat "$fixture/.governance-invocations")" == "2" ]] \
  || fail "negative path must still invoke the managed gate exactly once"

echo "pytest governance plugin tests passed"
