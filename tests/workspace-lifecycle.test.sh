#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
fixture="$(mktemp -d "${TMPDIR:-/tmp}/new-project-workspace-lifecycle.XXXXXX")"
unknown_root="$(mktemp -d /var/tmp/new-project-workspace-unknown.XXXXXX)"
cleanup() {
  rm -rf "$fixture" "$unknown_root"
}
trap cleanup EXIT INT TERM

validator="$repo_root/scripts/workspace_lifecycle_check.py"
workspace="$fixture/workspace"
primary="$workspace/sample"
legacy_v1="$workspace/.worktrees/sample--ticket-001--legacy-v1"
legacy_v2="$workspace/.worktrees/sample/ticket-002--legacy-v2"
legacy_v3="$workspace/.worktrees/.branches/sample/ticket-003--legacy-v3"
canonical_v4="$primary/worktrees/ticket-004--canonical-v4"
system_temp="$fixture/external/ticket-005--system-temp"
unknown="$unknown_root/ticket-006--unknown"
duplicate="$workspace/sample-pilot"
nested_duplicate="$workspace/archive/sample"
empty_primary="$workspace/empty"
empty_duplicate="$workspace/empty-pilot"
mkdir -p "$workspace"
git init --quiet --initial-branch=main "$primary"
git -C "$primary" config user.email workspace-test@example.invalid
git -C "$primary" config user.name workspace-test
printf '%s\n' sample > "$primary/README.md"
printf '%s\n' /worktrees/ /.subactor/ > "$primary/.gitignore"
git -C "$primary" add README.md .gitignore
git -C "$primary" commit --quiet -m initial
git -C "$primary" remote add origin git@github.com:example/sample.git
mkdir -p "$workspace/.worktrees/.branches/sample" "$unknown_root" \
  "$fixture/external"
git -C "$primary" worktree add --quiet -b ticket/001-legacy-v1 "$legacy_v1"
git -C "$primary" worktree add --quiet -b ticket/002-legacy-v2 "$legacy_v2"
git -C "$primary" worktree add --quiet -b ticket/003-legacy-v3 "$legacy_v3"
git -C "$primary" worktree add --quiet -b ticket/004-canonical-v4 "$canonical_v4"
git -C "$primary" worktree add --quiet -b ticket/005-system-temp "$system_temp"
git -C "$primary" worktree add --quiet -b ticket/006-unknown "$unknown"
git clone --quiet "$primary" "$duplicate"
mkdir -p "$workspace/archive"
git clone --quiet "$primary" "$nested_duplicate"
git init --quiet --initial-branch=main "$empty_primary"
git -C "$empty_primary" remote add origin git@github.com:example/empty.git
git clone --quiet "$empty_primary" "$empty_duplicate"
printf '%s\n' dirty > "$legacy_v1/untracked.txt"
registry_before="$(git -C "$primary" worktree list --porcelain)"

if python3 "$validator" --workspace-root "$workspace" --format json \
  > "$fixture/violations.json"; then
  status=0
else
  status=$?
fi
test "$status" -eq 1
python3 - "$fixture/violations.json" "$legacy_v1" "$legacy_v2" "$legacy_v3" \
  "$canonical_v4" "$system_temp" "$unknown" "$duplicate" \
  "$nested_duplicate" "$empty_duplicate" <<'PY'
import json
import sys

report = json.load(open(sys.argv[1], encoding="utf-8"))
assert report["schema"] == "new-project.workspace-lifecycle-report/v1"
assert report["status"] == "failed"
assert report["summary"] == {"errors": 15, "warnings": 0, "findings": 15}
assert report["inventory"]["schema"] == "wellmanifest.worktrees/v4"
assert report["inventory"]["readOnly"] is True
assert {finding["code"] for finding in report["findings"]} == {
    "GOV-WORKSPACE-LIFECYCLE-001",
    "GOV-WORKSPACE-LIFECYCLE-002",
    "GOV-WORKSPACE-LIFECYCLE-004",
}
linked = [
    finding for finding in report["findings"]
    if finding["code"] == "GOV-WORKSPACE-LIFECYCLE-001"
]
duplicates = [
    finding for finding in report["findings"]
    if finding["code"] == "GOV-WORKSPACE-LIFECYCLE-002"
]
branches = [
    finding for finding in report["findings"]
    if finding["code"] == "GOV-WORKSPACE-LIFECYCLE-004"
]
assert len(linked) == 6
assert len(duplicates) == 3
assert len(branches) == 6
assert {item["evidence"]["branch"] for item in branches} == {
    "ticket/001-legacy-v1", "ticket/002-legacy-v2", "ticket/003-legacy-v3",
    "ticket/004-canonical-v4", "ticket/005-system-temp", "ticket/006-unknown",
}
assert all(item["evidence"]["defaultBranch"] == "main" for item in branches)
assert all(item["evidence"]["checkout"] is not None for item in branches)
dirty = next(item for item in linked if item["evidence"]["path"] == sys.argv[2])
assert dirty["evidence"]["dirty"] is True
classifications = {
    item["evidence"]["path"]:
    item["evidence"]["workspaceClassification"]["classification"]
    for item in linked
}
assert classifications == {
    sys.argv[2]: "legacy-v1",
    sys.argv[3]: "legacy-v2",
    sys.argv[4]: "legacy-v3",
    sys.argv[5]: "canonical-v4",
    sys.argv[6]: "system-temp",
    sys.argv[7]: "unknown",
}, classifications
assert {item["evidence"]["path"] for item in duplicates} == {
    sys.argv[8], sys.argv[9], sys.argv[10]
}
assert all(
    item["evidence"]["workspaceClassification"]["cloneClassification"]
    == "duplicate-clone"
    for item in duplicates
)
empty = next(item for item in duplicates if item["evidence"]["path"] == sys.argv[10])
assert empty["evidence"]["head"] is None
assert empty["evidence"]["primary"].endswith("/empty")
assert all(
    item["evidence"]["primary"].endswith("/sample")
    for item in report["findings"]
    if item is not empty
)
PY

test "$registry_before" = "$(git -C "$primary" worktree list --porcelain)"
for preserved in "$legacy_v1" "$legacy_v2" "$legacy_v3" "$canonical_v4" \
  "$system_temp" "$unknown"; do
  test -d "$preserved"
done
test -f "$legacy_v1/untracked.txt"

python3 "$validator" --workspace-root "$workspace" \
  --allow "$legacy_v1" --allow "$legacy_v2" --allow "$legacy_v3" \
  --allow "$canonical_v4" --allow "$system_temp" --allow "$unknown" \
  --allow "$duplicate" \
  --allow "$nested_duplicate" --allow "$empty_duplicate" \
  > "$fixture/allowed.out"
grep -Fxq 'GOV-WORKSPACE-PASS: passed (0 errors, 0 warnings)' "$fixture/allowed.out"

git -C "$primary" worktree remove --force "$legacy_v1"
git -C "$primary" worktree remove --force "$legacy_v2"
git -C "$primary" worktree remove --force "$legacy_v3"
git -C "$primary" worktree remove --force "$canonical_v4"
git -C "$primary" worktree remove --force "$system_temp"
git -C "$primary" worktree remove --force "$unknown"
rm -rf "$duplicate"
rm -rf "$nested_duplicate"
rm -rf "$empty_duplicate"

# Releasing a worktree is not enough: its local branch remains in refs/heads.
# The checker reports all three exact refs without deleting them.
if python3 "$validator" --workspace-root "$workspace" --format json \
  > "$fixture/orphan-branches.json"; then
  status=0
else
  status=$?
fi
test "$status" -eq 1
python3 - "$fixture/orphan-branches.json" <<'PY'
import json
import sys

report = json.load(open(sys.argv[1], encoding="utf-8"))
assert report["summary"] == {"errors": 6, "warnings": 0, "findings": 6}
assert {finding["code"] for finding in report["findings"]} == {
    "GOV-WORKSPACE-LIFECYCLE-004",
}
assert {finding["evidence"]["branch"] for finding in report["findings"]} == {
    "ticket/001-legacy-v1", "ticket/002-legacy-v2", "ticket/003-legacy-v3",
    "ticket/004-canonical-v4", "ticket/005-system-temp", "ticket/006-unknown",
}
assert all(finding["evidence"]["checkout"] is None for finding in report["findings"])
assert all(finding["evidence"]["defaultBranch"] == "main" for finding in report["findings"])
PY
test "$(git -C "$primary" for-each-ref --format='%(refname:short)' refs/heads/ticket | wc -l)" -eq 6
git -C "$primary" branch -d ticket/001-legacy-v1 ticket/002-legacy-v2 \
  ticket/003-legacy-v3 ticket/004-canonical-v4 ticket/005-system-temp \
  ticket/006-unknown
python3 "$validator" --workspace-root "$workspace" > "$fixture/clean.out"
grep -Fxq 'GOV-WORKSPACE-PASS: passed (0 errors, 0 warnings)' "$fixture/clean.out"

# A manually created ticket in a linked worktree did not pass through the
# clone-wide allocator, so its number exceeds both refs and the shared
# high-water mark. Allowlisting the active worktree must not hide that claim.
allocation_workspace="$fixture/allocation-workspace"
allocation_primary="$allocation_workspace/allocation"
allocation_linked="$allocation_workspace/allocation-ticket"
mkdir -p "$allocation_workspace"
git init --quiet --initial-branch=main "$allocation_primary"
git -C "$allocation_primary" config user.email workspace-test@example.invalid
git -C "$allocation_primary" config user.name workspace-test
git -C "$allocation_primary" remote add origin git@github.com:example/allocation.git
mkdir -p "$allocation_primary/project/ticket-007"
printf '%s\n' \
  '{"ticket":"ticket-007","summary":"baseline","workstream":"governance"}' \
  > "$allocation_primary/project/ticket-007/intent.json"
git -C "$allocation_primary" add project/ticket-007/intent.json
git -C "$allocation_primary" commit --quiet -m baseline
git -C "$allocation_primary" worktree add --quiet -b ticket/008 "$allocation_linked"
mkdir -p "$allocation_linked/project/ticket-008"
printf '%s\n' \
  '{"ticket":"ticket-008","summary":"manual claim","workstream":"governance"}' \
  > "$allocation_linked/project/ticket-008/intent.json"

if python3 "$validator" --workspace-root "$allocation_workspace" \
  --allow "$allocation_linked" --format json > "$fixture/unreserved.json"; then
  status=0
else
  status=$?
fi
test "$status" -eq 1
python3 - "$fixture/unreserved.json" <<'PY'
import json
import sys

report = json.load(open(sys.argv[1], encoding="utf-8"))
assert report["summary"]["errors"] == 1
finding = report["findings"][0]
assert finding["code"] == "GOV-TICKET-ALLOCATION-001"
assert finding["evidence"]["ticket"] == "ticket-008"
assert finding["evidence"]["refHighest"] == 7
PY

# A real allocator reservation makes the same single claim valid.
printf '%s\n' 8 > "$allocation_primary/.git/new-project-ticket-high-water"
python3 "$validator" --workspace-root "$allocation_workspace" \
  --allow "$allocation_linked" > "$fixture/reserved.out"
grep -Fxq 'GOV-WORKSPACE-PASS: passed (0 errors, 0 warnings)' "$fixture/reserved.out"

# Reusing the reserved number for a different intent in another linked
# worktree is a collision even though the numeric high-water is sufficient.
mkdir -p "$allocation_primary/project/ticket-008"
printf '%s\n' \
  '{"ticket":"ticket-008","summary":"different claim","workstream":"infrastructure"}' \
  > "$allocation_primary/project/ticket-008/intent.json"
if python3 "$validator" --workspace-root "$allocation_workspace" \
  --allow "$allocation_linked" --format json > "$fixture/collision.json"; then
  status=0
else
  status=$?
fi
test "$status" -eq 1
python3 - "$fixture/collision.json" <<'PY'
import json
import sys

report = json.load(open(sys.argv[1], encoding="utf-8"))
assert report["summary"]["errors"] == 1
finding = report["findings"][0]
assert finding["code"] == "GOV-TICKET-ALLOCATION-002"
assert finding["evidence"]["ticket"] == "ticket-008"
assert {claim["summary"] for claim in finding["evidence"]["claims"]} == {
    "manual claim", "different claim",
}
PY

if python3 "$validator" --workspace-root "$fixture/missing" \
  > "$fixture/missing.out" 2>&1; then
  status=0
else
  status=$?
fi
test "$status" -eq 1
grep -q '^GOV-WORKSPACE-LIFECYCLE-003 ERROR:' "$fixture/missing.out"

echo 'workspace lifecycle validator: PASS'
