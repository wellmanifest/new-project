#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
fixture="$(mktemp -d "${TMPDIR:-/tmp}/new-project-branch-lifecycle.XXXXXX")"
cleanup() {
  rm -rf "$fixture"
}
trap cleanup EXIT INT TERM

validator="$repo_root/scripts/branch_lifecycle_check.py"
test -f "$validator"

cat > "$fixture/clean.json" <<'JSON'
{"schema":"new-project.branch-lifecycle-snapshot/v1","repository":"wellmanifest/example","defaultBranch":"main","deleteBranchOnMerge":true,"branches":["main"],"openPullRequests":[]}
JSON
python3 "$validator" --snapshot "$fixture/clean.json" \
  --expected-repository wellmanifest/example > "$fixture/clean.out"
grep -Fxq 'GOV-BRANCH-PASS: passed (0 errors, 0 warnings)' "$fixture/clean.out"

cat > "$fixture/owned.json" <<'JSON'
{"schema":"new-project.branch-lifecycle-snapshot/v1","repository":"wellmanifest/example","defaultBranch":"main","deleteBranchOnMerge":true,"branches":["main","ticket/018"],"openPullRequests":[{"number":18,"headRepository":"wellmanifest/example","headRef":"ticket/018"},{"number":19,"headRepository":"someone/fork","headRef":"fork-change"}]}
JSON
python3 "$validator" --snapshot "$fixture/owned.json" \
  --expected-repository wellmanifest/example --format json > "$fixture/owned.out"
python3 - "$fixture/owned.out" <<'PY'
import json
import sys
report = json.load(open(sys.argv[1], encoding="utf-8"))
assert report == {
    "schema": "new-project.branch-lifecycle-report/v1",
    "status": "passed",
    "summary": {"errors": 0, "warnings": 0, "findings": 0},
    "findings": [],
}
PY

cat > "$fixture/violations.json" <<'JSON'
{"schema":"new-project.branch-lifecycle-snapshot/v1","repository":"wellmanifest/example","defaultBranch":"main","deleteBranchOnMerge":false,"branches":["main","old-work"],"openPullRequests":[]}
JSON
set +e
python3 "$validator" --snapshot "$fixture/violations.json" \
  --expected-repository wellmanifest/example > "$fixture/violations.1.out"
status=$?
python3 "$validator" --snapshot "$fixture/violations.json" \
  --expected-repository wellmanifest/example > "$fixture/violations.2.out"
repeat_status=$?
set -e
test "$status" -eq 1
test "$repeat_status" -eq 1
cmp -s "$fixture/violations.1.out" "$fixture/violations.2.out"
grep -q '^GOV-BRANCH-LIFECYCLE-001 ERROR:' "$fixture/violations.1.out"
grep -q '^GOV-BRANCH-LIFECYCLE-002 ERROR:' "$fixture/violations.1.out"
grep -Fq '"orphanedBranches":["old-work"]' "$fixture/violations.1.out"
grep -Fxq 'GOV-BRANCH-FAIL: failed (2 errors, 0 warnings)' "$fixture/violations.1.out"

cat > "$fixture/missing-head.json" <<'JSON'
{"schema":"new-project.branch-lifecycle-snapshot/v1","repository":"wellmanifest/example","defaultBranch":"main","deleteBranchOnMerge":true,"branches":["main"],"openPullRequests":[{"number":18,"headRepository":"wellmanifest/example","headRef":"ticket/018"}]}
JSON
set +e
python3 "$validator" --snapshot "$fixture/missing-head.json" \
  --expected-repository wellmanifest/example > "$fixture/missing-head.out"
status=$?
set -e
test "$status" -eq 1
grep -q '^GOV-BRANCH-LIFECYCLE-003 ERROR:' "$fixture/missing-head.out"
grep -Fq '"missingInternalHeads":["ticket/018"]' "$fixture/missing-head.out"

cat > "$fixture/malformed.json" <<'JSON'
{"schema":"new-project.branch-lifecycle-snapshot/v1","repository":"wellmanifest/example","defaultBranch":"main","deleteBranchOnMerge":true,"branches":["main"],"openPullRequests":[],"decision":"delete"}
JSON
set +e
python3 "$validator" --snapshot "$fixture/malformed.json" \
  --expected-repository wellmanifest/other > "$fixture/malformed.out"
status=$?
set -e
test "$status" -eq 1
grep -q '^GOV-BRANCH-LIFECYCLE-003 ERROR:' "$fixture/malformed.out"
grep -Fq 'snapshot fields are invalid' "$fixture/malformed.out"

python3 - "$validator" <<'PY'
import re
import sys
source = open(sys.argv[1], encoding="utf-8").read()
emitted = set(re.findall(r'code="(GOV-BRANCH-LIFECYCLE-[0-9]{3})"', source))
assert emitted == {
    "GOV-BRANCH-LIFECYCLE-001",
    "GOV-BRANCH-LIFECYCLE-002",
    "GOV-BRANCH-LIFECYCLE-003",
}
for forbidden in ("import requests", "import urllib", "import socket", "import subprocess"):
    assert forbidden not in source
PY

grep -Fq "new-project.branch-lifecycle-snapshot/v1" "$repo_root/.github/workflows/governance.yml"
grep -Fq 'deleteBranchOnMerge: repository.data.delete_branch_on_merge' \
  "$repo_root/.github/workflows/governance.yml"
grep -Fq 'bash tests/branch-lifecycle.test.sh' "$repo_root/.github/workflows/ci.yml"

echo 'branch lifecycle validator: PASS'
