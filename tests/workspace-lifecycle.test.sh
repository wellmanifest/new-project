#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
fixture="$(mktemp -d "${TMPDIR:-/tmp}/new-project-workspace-lifecycle.XXXXXX")"
cleanup() {
  rm -rf "$fixture"
}
trap cleanup EXIT INT TERM

validator="$repo_root/scripts/workspace_lifecycle_check.py"
workspace="$fixture/workspace"
primary="$workspace/sample"
linked="$workspace/sample-worktree"
duplicate="$workspace/sample-pilot"
mkdir -p "$workspace"
git init --quiet --initial-branch=main "$primary"
git -C "$primary" config user.email workspace-test@example.invalid
git -C "$primary" config user.name workspace-test
printf '%s\n' sample > "$primary/README.md"
git -C "$primary" add README.md
git -C "$primary" commit --quiet -m initial
git -C "$primary" remote add origin git@github.com:example/sample.git
git -C "$primary" worktree add --quiet -b ticket/001 "$linked"
git clone --quiet "$primary" "$duplicate"
printf '%s\n' dirty > "$linked/untracked.txt"

if python3 "$validator" --workspace-root "$workspace" --format json \
  > "$fixture/violations.json"; then
  status=0
else
  status=$?
fi
test "$status" -eq 1
python3 - "$fixture/violations.json" "$linked" "$duplicate" <<'PY'
import json
import sys

report = json.load(open(sys.argv[1], encoding="utf-8"))
assert report["schema"] == "new-project.workspace-lifecycle-report/v1"
assert report["status"] == "failed"
assert report["summary"] == {"errors": 2, "warnings": 0, "findings": 2}
by_code = {finding["code"]: finding for finding in report["findings"]}
assert set(by_code) == {
    "GOV-WORKSPACE-LIFECYCLE-001",
    "GOV-WORKSPACE-LIFECYCLE-002",
}
assert by_code["GOV-WORKSPACE-LIFECYCLE-001"]["evidence"]["path"] == sys.argv[2]
assert by_code["GOV-WORKSPACE-LIFECYCLE-001"]["evidence"]["dirty"] is True
assert by_code["GOV-WORKSPACE-LIFECYCLE-002"]["evidence"]["path"] == sys.argv[3]
PY

python3 "$validator" --workspace-root "$workspace" \
  --allow "$linked" --allow "$duplicate" > "$fixture/allowed.out"
grep -Fxq 'GOV-WORKSPACE-PASS: passed (0 errors, 0 warnings)' "$fixture/allowed.out"

git -C "$primary" worktree remove --force "$linked"
rm -rf "$duplicate"
python3 "$validator" --workspace-root "$workspace" > "$fixture/clean.out"
grep -Fxq 'GOV-WORKSPACE-PASS: passed (0 errors, 0 warnings)' "$fixture/clean.out"

if python3 "$validator" --workspace-root "$fixture/missing" > "$fixture/missing.out"; then
  status=0
else
  status=$?
fi
test "$status" -eq 1
grep -q '^GOV-WORKSPACE-LIFECYCLE-003 ERROR:' "$fixture/missing.out"

echo 'workspace lifecycle validator: PASS'

