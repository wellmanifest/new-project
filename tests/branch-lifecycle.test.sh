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
if python3 "$validator" --snapshot "$fixture/violations.json" \
  --expected-repository wellmanifest/example > "$fixture/violations.1.out"; then
  status=0
else
  status=$?
fi
if python3 "$validator" --snapshot "$fixture/violations.json" \
  --expected-repository wellmanifest/example > "$fixture/violations.2.out"; then
  repeat_status=0
else
  repeat_status=$?
fi
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
if python3 "$validator" --snapshot "$fixture/missing-head.json" \
  --expected-repository wellmanifest/example > "$fixture/missing-head.out"; then
  status=0
else
  status=$?
fi
test "$status" -eq 1
grep -q '^GOV-BRANCH-LIFECYCLE-003 ERROR:' "$fixture/missing-head.out"
grep -Fq '"missingInternalHeads":["ticket/018"]' "$fixture/missing-head.out"

cat > "$fixture/malformed.json" <<'JSON'
{"schema":"new-project.branch-lifecycle-snapshot/v1","repository":"wellmanifest/example","defaultBranch":"main","deleteBranchOnMerge":true,"branches":["main"],"openPullRequests":[],"decision":"delete"}
JSON
if python3 "$validator" --snapshot "$fixture/malformed.json" \
  --expected-repository wellmanifest/other > "$fixture/malformed.out"; then
  status=0
else
  status=$?
fi
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
grep -Fq 'const repositorySettings = await github.graphql' \
  "$repo_root/.github/workflows/governance.yml"
grep -Fq 'deleteBranchOnMerge: repositorySettings.repository.deleteBranchOnMerge' \
  "$repo_root/.github/workflows/governance.yml"
if grep -Fq 'repository.data.delete_branch_on_merge' \
  "$repo_root/.github/workflows/governance.yml"; then
  echo 'branch lifecycle snapshot relies on optional REST repository metadata' >&2
  exit 1
fi
grep -Fq 'bash tests/branch-lifecycle.test.sh' "$repo_root/.github/workflows/ci.yml"
grep -Fq 'Acquire live GitHub branch lifecycle snapshot' \
  "$repo_root/.github/workflows/ci.yml"
grep -Fq 'python3 scripts/branch_lifecycle_check.py' \
  "$repo_root/.github/workflows/ci.yml"
grep -Fq 'pull-requests: read' "$repo_root/.github/workflows/ci.yml"
test "$(grep -Fc "if: github.event_name == 'pull_request' || github.ref == 'refs/heads/main'" \
  "$repo_root/.github/workflows/ci.yml")" -eq 2

target_workflow="$repo_root/template/files/new-project-governance.workflow.yml"
grep -Fq '    - cron: "17 3 * * *"' "$target_workflow"
if grep -Fq "    - cron: '17 3 * * *'" "$target_workflow"; then
  echo 'managed governance workflow uses non-canonical cron quoting' >&2
  exit 1
fi
grep -Fq "new-project.branch-lifecycle-snapshot/v1" "$target_workflow"
grep -Fq 'deleteBranchOnMerge: settings.repository.deleteBranchOnMerge' "$target_workflow"
grep -Fq 'python3 .governance/branch_lifecycle_check.py' "$target_workflow"
python3 - "$repo_root/governance/package-manifest.json" <<'PY'
import json
import sys

package = json.load(open(sys.argv[1], encoding="utf-8"))
by_target = {item["target"]: item for item in package["files"]}
assert by_target[".governance/branch_lifecycle_check.py"]["strategy"] == "managed"
assert by_target[".governance/workspace_lifecycle_check.py"]["strategy"] == "managed"
assert by_target[".github/workflows/new-project-governance.yml"] == {
    "source": "template/files/new-project-governance.workflow.yml",
    "target": ".github/workflows/new-project-governance.yml",
    "strategy": "managed",
    "executable": False,
}
PY

echo 'branch lifecycle validator: PASS'
