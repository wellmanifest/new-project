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
linked_two="$workspace/worktrees/sample-worktree-two"
external_linked="$fixture/external/sample-worktree"
duplicate="$workspace/sample-pilot"
nested_duplicate="$workspace/archive/sample"
mkdir -p "$workspace"
git init --quiet --initial-branch=main "$primary"
git -C "$primary" config user.email workspace-test@example.invalid
git -C "$primary" config user.name workspace-test
printf '%s\n' sample > "$primary/README.md"
git -C "$primary" add README.md
git -C "$primary" commit --quiet -m initial
git -C "$primary" remote add origin git@github.com:example/sample.git
git -C "$primary" worktree add --quiet -b ticket/001 "$linked"
mkdir -p "$workspace/worktrees"
git -C "$primary" worktree add --quiet -b ticket/002 "$linked_two"
mkdir -p "$fixture/external"
git -C "$primary" worktree add --quiet -b ticket/003 "$external_linked"
git clone --quiet "$primary" "$duplicate"
mkdir -p "$workspace/archive"
git clone --quiet "$primary" "$nested_duplicate"
printf '%s\n' dirty > "$linked/untracked.txt"

if python3 "$validator" --workspace-root "$workspace" --format json \
  > "$fixture/violations.json"; then
  status=0
else
  status=$?
fi
test "$status" -eq 1
python3 - "$fixture/violations.json" "$linked" "$external_linked" \
  "$duplicate" "$nested_duplicate" <<'PY'
import json
import sys

report = json.load(open(sys.argv[1], encoding="utf-8"))
assert report["schema"] == "new-project.workspace-lifecycle-report/v1"
assert report["status"] == "failed"
assert report["summary"] == {"errors": 5, "warnings": 0, "findings": 5}
assert {finding["code"] for finding in report["findings"]} == {
    "GOV-WORKSPACE-LIFECYCLE-001",
    "GOV-WORKSPACE-LIFECYCLE-002",
}
linked = [
    finding for finding in report["findings"]
    if finding["code"] == "GOV-WORKSPACE-LIFECYCLE-001"
]
duplicates = [
    finding for finding in report["findings"]
    if finding["code"] == "GOV-WORKSPACE-LIFECYCLE-002"
]
assert len(linked) == 3
assert len(duplicates) == 2
dirty = next(item for item in linked if item["evidence"]["path"] == sys.argv[2])
assert dirty["evidence"]["dirty"] is True
assert any(item["evidence"]["path"] == sys.argv[3] for item in linked)
assert {item["evidence"]["path"] for item in duplicates} == {sys.argv[4], sys.argv[5]}
assert all(item["evidence"]["primary"].endswith("/sample") for item in report["findings"])
PY

python3 "$validator" --workspace-root "$workspace" \
  --allow "$linked" --allow "$linked_two" --allow "$external_linked" \
  --allow "$duplicate" \
  --allow "$nested_duplicate" > "$fixture/allowed.out"
grep -Fxq 'GOV-WORKSPACE-PASS: passed (0 errors, 0 warnings)' "$fixture/allowed.out"

git -C "$primary" worktree remove --force "$linked"
git -C "$primary" worktree remove --force "$linked_two"
git -C "$primary" worktree remove --force "$external_linked"
rm -rf "$duplicate"
rm -rf "$nested_duplicate"
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
