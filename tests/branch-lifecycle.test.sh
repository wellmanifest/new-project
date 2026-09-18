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

cat > "$fixture/focus.json" <<'JSON'
{"schema":"new-project.branch-lifecycle-snapshot/v1","repository":"wellmanifest/example","defaultBranch":"main","deleteBranchOnMerge":true,"branches":["main","ticket/018","orphan-work"],"openPullRequests":[{"number":18,"headRepository":"wellmanifest/example","headRef":"ticket/018"}]}
JSON
if python3 "$validator" --snapshot "$fixture/focus.json" \
  --expected-repository wellmanifest/example > "$fixture/focus-unscoped.out"; then
  status=0
else
  status=$?
fi
test "$status" -eq 1
grep -Fq '"orphanedBranches":["orphan-work"]' "$fixture/focus-unscoped.out"

python3 "$validator" --snapshot "$fixture/focus.json" \
  --expected-repository wellmanifest/example \
  --focus-branch ticket/018 > "$fixture/focus-owned.out"
grep -Fxq 'GOV-BRANCH-PASS: passed (0 errors, 0 warnings)' "$fixture/focus-owned.out"

if python3 "$validator" --snapshot "$fixture/focus.json" \
  --expected-repository wellmanifest/example \
  --focus-branch orphan-work > "$fixture/focus-orphan.out"; then
  status=0
else
  status=$?
fi
test "$status" -eq 1
grep -Fq '"orphanedBranches":["orphan-work"]' "$fixture/focus-orphan.out"

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

# Canonical navigation must follow the emitted code, not a remembered label.
# These two cases used to have their meanings exchanged in diagnostics.json.
python3 - "$repo_root" <<'PY'
import importlib.util
import json
from pathlib import Path
import sys

root = Path(sys.argv[1])
spec = importlib.util.spec_from_file_location("branch_navigation", root / "scripts/branch_lifecycle_check.py")
runtime = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = runtime
spec.loader.exec_module(runtime)
catalog = json.loads((root / "governance/diagnostics.json").read_text())["codes"]
snapshot = {"repository": "wellmanifest/example", "defaultBranch": "main",
            "deleteBranchOnMerge": True, "branches": ["main"], "openPullRequests": []}
cases = [
    ("GOV-BRANCH-LIFECYCLE-001", {**snapshot, "deleteBranchOnMerge": False}),
    ("GOV-BRANCH-LIFECYCLE-002", {**snapshot, "branches": ["main", "retained-work"]}),
    ("GOV-BRANCH-LIFECYCLE-003", {**snapshot, "openPullRequests": [
        {"number": 7, "headRepository": "wellmanifest/example", "headRef": "missing"}]}),
]
managed = json.loads((root / "governance/package-manifest.json").read_text())["files"]
for code, observation in cases:
    findings = runtime.evaluate(observation)
    assert len(findings) == 1 and findings[0].code == code, findings
    assert findings[0].message == catalog[code]["message"], (code, findings[0], catalog[code])
    assert findings[0].severity == "error", "This navigation fix cannot relax a gate"
    report = runtime.report_payload(findings)
    assert report["status"] == "failed" and report["summary"]["errors"] == 1
    path = catalog[code]["documentation"]
    assert code in (root / path).read_text(), code
    assert any(item["source"] == path and item["target"] == ".governance/" + path
               and item["strategy"] == "managed" for item in managed), path
assert runtime.evaluate(snapshot) == []
print("branch diagnostic navigation: PASS (3 emitted cases, managed runbook, unchanged refusals)")
PY

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
grep -Fq 'runner-label:' "$repo_root/.github/workflows/governance.yml"
grep -Fq 'default: ubuntu-latest' "$repo_root/.github/workflows/governance.yml"
grep -A5 -F 'runner-label:' "$repo_root/.github/workflows/governance.yml" \
  | grep -Fq 'required: false'
grep -A5 -F 'runner-label:' "$repo_root/.github/workflows/governance.yml" \
  | grep -Fq 'type: string'
grep -Fq 'runs-on: ${{ inputs.runner-label }}' "$repo_root/.github/workflows/governance.yml"
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
grep -Fq 'arguments+=(--focus-branch "$HEAD_REF")' "$repo_root/.github/workflows/ci.yml"
grep -Fq 'arguments+=(--focus-branch "$HEAD_REF")' "$repo_root/.github/workflows/governance.yml"

target_workflow="$repo_root/template/files/new-project-governance.workflow.yml"
grep -Fq 'arguments+=(--focus-branch "$HEAD_REF")' "$target_workflow"
grep -Fq '    - cron: "17 3 * * *"' "$target_workflow"
if grep -Fq "    - cron: '17 3 * * *'" "$target_workflow"; then
  echo 'managed governance workflow uses non-canonical cron quoting' >&2
  exit 1
fi
grep -Fq "new-project.branch-lifecycle-snapshot/v1" "$target_workflow"
grep -Fq 'deleteBranchOnMerge: settings.repository.deleteBranchOnMerge' "$target_workflow"
grep -Fq 'python3 .governance/branch_lifecycle_check.py' "$target_workflow"
test "$(grep -Fc "runs-on: \${{ vars.NEW_PROJECT_RUNNER_LABEL || 'ubuntu-latest' }}" \
  "$target_workflow")" -eq 2
grep -A2 -F 'name: Set up Python' "$target_workflow" \
  | grep -Fq "if: runner.environment == 'github-hosted'"
grep -A6 -F 'name: Require provisioned Python on self-hosted runner' \
  "$target_workflow" | grep -Fq "if: runner.environment == 'self-hosted'"
grep -A6 -F 'name: Require provisioned Python on self-hosted runner' \
  "$target_workflow" | grep -Fq "sys.version_info >= (3, 11)"
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

PYTHONDONTWRITEBYTECODE=1 python3 "$repo_root/tests/branch_intent_reconciliation_test.py"
