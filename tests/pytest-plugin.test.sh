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
mkdir -p "$fixture/.governance" "$fixture/.githooks"
cp "$root/template/files/wellmanifest_governance.py" "$fixture/"
cat > "$fixture/.governance/agent-hosts.json" <<'EOF'
{"hook":{"path":".githooks/pre-commit","hooksPathConfig":".githooks"}}
EOF
printf '%s\n' '#!/usr/bin/env bash' 'exit 0' > "$fixture/.githooks/pre-commit"
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
[[ "$(git -C "$fixture" config --get core.hooksPath)" == ".githooks" ]] \
  || fail "plugin must activate the managed hook in a fresh clone"

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

source_repo="$tmp/source"
shallow="$tmp/shallow"
mkdir -p "$source_repo/project"
git init -q -b main "$source_repo"
git -C "$source_repo" config user.email "test@example.com"
git -C "$source_repo" config user.name "Test"
cp "$root/template/files/wellmanifest_governance.py" "$source_repo/"
cat > "$source_repo/project/governance-check.sh" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
printf '%s\n' "$@" > .governance-arguments
EOF
chmod +x "$source_repo/project/governance-check.sh"
printf '%s\n' base > "$source_repo/tracked.txt"
git -C "$source_repo" add .
git -C "$source_repo" commit -qm base
event_base="$(git -C "$source_repo" rev-parse HEAD)"
printf '%s\n' head > "$source_repo/tracked.txt"
git -C "$source_repo" commit -qam head
git clone -q --depth=1 "file://$source_repo" "$shallow"
if git -C "$shallow" cat-file -e "$event_base^{commit}" 2>/dev/null; then
  fail "shallow fixture unexpectedly contains the pull-request base"
fi
printf '{"pull_request":{"base":{"sha":"%s"}}}\n' "$event_base" > "$tmp/event.json"
(
  cd "$shallow"
  GITHUB_EVENT_PATH="$tmp/event.json" python3 - <<'PY'
from pathlib import Path
from types import SimpleNamespace
import wellmanifest_governance

session = SimpleNamespace(config=SimpleNamespace(rootpath=Path.cwd()))
wellmanifest_governance.pytest_sessionstart(session)
PY
)
grep -Fxq -- "$event_base" "$shallow/.governance-arguments" \
  || fail "plugin must fetch and bind the exact GitHub event base SHA"
grep -Fxq -- "tracked.txt" "$shallow/.governance-arguments" \
  || fail "plugin must derive changed paths from the fetched PR base"

echo "pytest governance plugin tests passed"
