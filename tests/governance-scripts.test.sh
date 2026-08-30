#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
fixture="$(mktemp -d "${TMPDIR:-/tmp}/new-project-governance-test.XXXXXX")"
cleanup() {
  rm -rf "$fixture"
}
trap cleanup EXIT INT TERM

if grep -R -n 'file:///' \
  "$repo_root/AGENTS.md" "$repo_root/README.md" "$repo_root/llms.txt" >/dev/null; then
  echo 'Documentation contains machine-local file URLs' >&2
  exit 1
fi
if grep -q 'TICKET_MAIN_FILE' "$repo_root/CONTRIBUTING.md"; then
  echo 'Legacy project/README.md ticket ownership remains in the DSL' >&2
  exit 1
fi
test -x "$repo_root/project/new-ticket.sh"
test -x "$repo_root/project/readme.sh"
grep -Fq "@sha256:[a-f0-9]{64}$" "$repo_root/project.bat"
test -f "$repo_root/template/files/human-participant.template.md"
test -f "$repo_root/template/files/agent-participant.template.md"

mkdir -p "$fixture/project" "$fixture/template" "$fixture/.governance"
cp "$repo_root/project/new-ticket.sh" "$fixture/project/new-ticket.sh"
cp "$repo_root/project/readme.sh" "$fixture/project/readme.sh"
cp "$repo_root/scripts/ticket_activity.py" "$fixture/.governance/ticket_activity.py"
cp "$repo_root/governance/ticket-activity.json" "$fixture/.governance/ticket-activity.json"
cp -R "$repo_root/template/files" "$fixture/template/files"
# A real adopted target always carries the work classification contract, because
# the package manifest ships it. The scaffolder reads the accepted dimension
# values from it instead of hardcoding them, so the fixture must mirror that.
cp "$repo_root/governance/work-classification.dsl.json" "$fixture/.governance/work-classification.dsl.json"
cp "$repo_root/governance/manifest.default.json" "$fixture/.governance/manifest.json"
printf '%s\n' '# Analysis-owned project README' > "$fixture/project/README.md"

status=0
(
  cd "$fixture"
  bash project/new-ticket.sh --title 'Missing workstream' > missing-workstream.out 2> missing-workstream.err
) || status=$?
test "$status" -eq 2
grep -q 'Workstream is required' "$fixture/missing-workstream.err"
test ! -d "$fixture/project/ticket-001"

status=0
(
  cd "$fixture"
  bash project/new-ticket.sh --title 'Unknown workstream' --workstream invented \
    > unknown-workstream.out 2> unknown-workstream.err
) || status=$?
test "$status" -eq 1
grep -q 'GOV-WORKSTREAM-001' "$fixture/unknown-workstream.err"
test ! -d "$fixture/project/ticket-001"

mv "$fixture/.governance/manifest.json" "$fixture/manifest.json.bak"
status=0
(
  cd "$fixture"
  bash project/new-ticket.sh --title 'Missing registry' --workstream application \
    > missing-registry.out 2> missing-registry.err
) || status=$?
test "$status" -eq 1
grep -q 'GOV-MANIFEST-001' "$fixture/missing-registry.err"
test ! -d "$fixture/project/ticket-001"
mv "$fixture/manifest.json.bak" "$fixture/.governance/manifest.json"

cp "$fixture/.governance/manifest.json" "$fixture/manifest.json.valid"
printf '%s\n' '{}' > "$fixture/.governance/manifest.json"
status=0
(
  cd "$fixture"
  bash project/new-ticket.sh --title 'Invalid registry' --workstream application \
    > invalid-registry.out 2> invalid-registry.err
) || status=$?
test "$status" -eq 1
grep -q 'GOV-MANIFEST-001' "$fixture/invalid-registry.err"
test ! -d "$fixture/project/ticket-001"
mv "$fixture/manifest.json.valid" "$fixture/.governance/manifest.json"

(
  cd "$fixture"
  bash project/new-ticket.sh --title 'Validate "A&B" / routes' --agent Codex --workstream application --users alice \
    > first.out 2> first.err
)

ticket="$fixture/project/ticket-001"
test -f "$ticket/README.md"
test -f "$ticket/intent.json"
test ! -e "$ticket/preprompt.md"
test ! -e "$ticket/ai-codex.md"
test ! -e "$ticket/ai-codex-logs.txt"
test ! -e "$ticket/changelog.md"
test ! -e "$ticket/user-alice.md"
grep -q 'unresolved:human' "$ticket/README.md"
grep -q '^\- \*\*Status\*\*: IN_PROGRESS$' "$ticket/README.md"
grep -q '^\- \*\*Workflow state\*\*: EDIT$' "$ticket/README.md"
if grep -Eq 'WAIT_FOR_APPROVAL|waiting for approval|Human approval is required before implementation' \
  "$ticket/README.md"; then
  echo 'Generated ticket restored the redundant approval pause' >&2
  exit 1
fi
grep -q 'did not create user-\* files' "$fixture/first.err"
grep -qx '# Analysis-owned project README' "$fixture/project/README.md"
grep -q 'ticket-001' "$fixture/project/TICKETS.md"
if grep -q '{[A-Z_-]*}' "$ticket/README.md"; then
  echo 'Generated ticket contains unresolved template placeholders' >&2
  exit 1
fi
python3 - "$ticket/intent.json" <<'PY'
import json
import sys
intent = json.load(open(sys.argv[1], encoding='utf-8'))
assert intent['schema'] == 'new-project.intent/v3'
assert intent['ticket'] == 'ticket-001'
assert intent['summary'] == 'Validate "A&B" / routes'
assert intent['workstream'] == 'application'
# An unclassified scaffold takes the contract's own answer: W-CLASS-006
# (work-request / maintenance) plus priorityDerivation.serviceDefault.
assert intent['classification'] == {'kind': 'SERVICE', 'priority': 'P2', 'origin': 'health'}
assert intent['allowedPaths'] == ['project/ticket-001/**', 'TODO.md', 'project/TICKETS.md']
assert intent['dependsOn'] == []
assert intent['conflictsWith'] == []
assert intent['integrationTicket'] is None
PY

status=0
(
  cd "$fixture"
  bash project/new-ticket.sh --title 'Must reuse active ticket' --agent codex --workstream application \
    > second.out 2> second.err
) || status=$?
test "$status" -eq 3
grep -q "Active ticket conflicts with workstream 'application': project/ticket-001" "$fixture/second.err"
test ! -d "$fixture/project/ticket-002"

# Lifecycle vocabulary is registry-owned. A non-default active status must take
# effect without changing the allocator, while the old literal stops reserving.
python3 - "$fixture/.governance/manifest.json" <<'PY'
import json
import sys
path = sys.argv[1]
manifest = json.load(open(path, encoding='utf-8'))
manifest['ticket']['activeStatuses'] = ['RESERVED']
open(path, 'w', encoding='utf-8').write(json.dumps(manifest, indent=2) + '\n')
PY
sed -i 's/\*\*Status\*\*: IN_PROGRESS/**Status**: RESERVED/' "$ticket/README.md"
status=0
(
  cd "$fixture"
  bash project/new-ticket.sh --title 'Must reuse registry-active ticket' --agent codex --workstream application \
    > registry-active.out 2> registry-active.err
) || status=$?
test "$status" -eq 3
grep -q "Active ticket conflicts with workstream 'application': project/ticket-001" "$fixture/registry-active.err"

sed -i 's/\*\*Status\*\*: RESERVED/**Status**: IN_PROGRESS/' "$ticket/README.md"
(
  cd "$fixture"
  bash project/new-ticket.sh --title 'Replacement application ticket' --agent codex-2 \
    --workstream application > replacement.out
)
test -d "$fixture/project/ticket-002"
grep -q '"workstream": "application"' "$fixture/project/ticket-002/intent.json"

python3 - "$fixture/.governance/manifest.json" <<'PY'
import json
import sys
path = sys.argv[1]
manifest = json.load(open(path, encoding='utf-8'))
manifest['ticket']['activeStatuses'] = ['IN_PROGRESS']
open(path, 'w', encoding='utf-8').write(json.dumps(manifest, indent=2) + '\n')
PY

(
  cd "$fixture"
  bash project/new-ticket.sh --title 'Parallel interface ticket' --agent codex-2 \
    --workstream interfaces > parallel.out
)
test -d "$fixture/project/ticket-003"
grep -q '"workstream": "interfaces"' "$fixture/project/ticket-003/intent.json"

sed -i 's/\*\*Status\*\*: IN_PROGRESS/**Status**: DONE/' "$ticket/README.md"
sed -i 's/\*\*Status\*\*: IN_PROGRESS/**Status**: DONE/' "$fixture/project/ticket-002/README.md"
sed -i 's/\*\*Status\*\*: IN_PROGRESS/**Status**: DONE/' "$fixture/project/ticket-003/README.md"
(
  cd "$fixture"
  bash project/new-ticket.sh --title 'Second ticket' --agent codex --workstream application > third.out
  cp project/TICKETS.md index.before
  bash project/readme.sh > /dev/null
  cmp -s index.before project/TICKETS.md
)
test -d "$fixture/project/ticket-004"
grep -q 'ticket-001' "$fixture/project/TICKETS.md"
grep -q 'ticket-002' "$fixture/project/TICKETS.md"
grep -q 'ticket-003' "$fixture/project/TICKETS.md"
grep -q 'ticket-004' "$fixture/project/TICKETS.md"

# Adopted targets receive new-ticket.sh but not the hub-only authoring
# templates. Its built-in fallback must expose the same autonomous default.
fallback="$fixture/fallback"
mkdir -p "$fallback/project" "$fallback/.governance"
cp "$repo_root/project/new-ticket.sh" "$fallback/project/new-ticket.sh"
cp "$repo_root/governance/work-classification.dsl.json" \
  "$fallback/.governance/work-classification.dsl.json"
cp "$repo_root/governance/manifest.default.json" "$fallback/.governance/manifest.json"
(
  cd "$fallback"
  bash project/new-ticket.sh --title 'Fallback autonomous ticket' \
    --agent codex --workstream application > fallback.out
)
grep -q '^\- \*\*Status\*\*: IN_PROGRESS$' "$fallback/project/ticket-001/README.md"
grep -q '^\- \*\*Workflow state\*\*: EDIT$' "$fallback/project/ticket-001/README.md"
test -f "$fallback/project/ticket-001/intent.json"
test ! -e "$fallback/project/ticket-001/preprompt.md"
test ! -e "$fallback/project/ticket-001/ai-codex.md"

status=0
(
  cd "$fixture"
  T2C_TICKET_INDEX_FILE='../outside.md' bash project/readme.sh > /dev/null 2> traversal.err
) || status=$?
test "$status" -eq 2
test ! -e "$fixture/../outside.md"

if [[ -n "${TODO2CODE_CLI:-}" ]]; then
  node "$TODO2CODE_CLI" communication "$fixture" \
    --project-dir project --ticket ticket-001 --no-ast \
    --out "$fixture/communication-analysis.json" >/dev/null
  node - "$fixture/communication-analysis.json" <<'NODE'
const fs = require('node:fs');
const analysis = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
if (!analysis.participants.some((item) =>
  item.participant === 'agent:codex' && item.role === 'agent')) {
  throw new Error('todo2code did not preserve the generated agent identity');
}
if (analysis.participants.some((item) => item.role === 'human')) {
  throw new Error('ticket scaffolding invented a human participant');
}
if (!analysis.issues.some((item) => item.responseRequiredRole === 'human'
  && item.responseRequiredFrom.includes('unresolved:human'))) {
  throw new Error('missing human ownership was not routed explicitly');
}
NODE
fi

# Classification is a normative property, so it needs a positive assertion above
# and negative mutations here: a value outside the contract must be refused, and
# refusal must not leave a half-created ticket behind. The count is taken rather
# than a fixed name, because earlier cases have already created several tickets.
count_tickets() {
  find "$fixture/project" -maxdepth 1 -type d -name 'ticket-*' | wc -l
}
tickets_before="$(count_tickets)"

for mutation in '--kind NOPE' '--priority P9' '--origin invented'; do
  status=0
  (
    cd "$fixture"
    # shellcheck disable=SC2086
    bash project/new-ticket.sh --title 'Rejected classification' --workstream interfaces $mutation \
      > mutation.out 2> mutation.err
  ) || status=$?
  test "$status" -eq 1
  grep -q 'GOV-CLASS-001' "$fixture/mutation.err"
  test "$(count_tickets)" -eq "$tickets_before"
done

# Without the contract there is nothing to validate against, and guessing would
# defeat the point; the scaffolder must say so rather than emit an unchecked value.
mv "$fixture/.governance/work-classification.dsl.json" "$fixture/work-classification.dsl.json.bak"
status=0
(
  cd "$fixture"
  bash project/new-ticket.sh --title 'No contract' --workstream interfaces \
    > nocontract.out 2> nocontract.err
) || status=$?
test "$status" -eq 1
grep -q 'GOV-CLASS-000' "$fixture/nocontract.err"
test "$(count_tickets)" -eq "$tickets_before"
mv "$fixture/work-classification.dsl.json.bak" "$fixture/.governance/work-classification.dsl.json"

# Allocation must skip an id already claimed on a branch the clone knows about,
# and the index must not reference tickets git does not track. Both are exercised
# in a throwaway repository so the fixture stays independent of this checkout.
race="$(mktemp -d "${TMPDIR:-/tmp}/new-project-race-test.XXXXXX")"
trap 'rm -rf "$fixture" "$race"' EXIT INT TERM

git -C "$race" init -q origin.git --bare
git -C "$race" clone -q origin.git upstream
mkdir -p "$race/upstream/project/ticket-007"
printf '# Ticket 007\n' > "$race/upstream/project/ticket-007/README.md"
git -C "$race/upstream" -c user.email=t@e -c user.name=t add -A
git -C "$race/upstream" -c user.email=t@e -c user.name=t commit -qm init
git -C "$race/upstream" push -q origin HEAD:main
# A second worker claims 008 on a branch and pushes it without merging.
mkdir -p "$race/upstream/project/ticket-008"
printf '# Ticket 008\n' > "$race/upstream/project/ticket-008/README.md"
git -C "$race/upstream" -c user.email=t@e -c user.name=t add -A
git -C "$race/upstream" -c user.email=t@e -c user.name=t commit -qm claim
git -C "$race/upstream" push -q origin HEAD:refs/heads/ticket/008-other

git -C "$race" clone -q origin.git mine
mkdir -p "$race/mine/project" "$race/mine/template" "$race/mine/.governance"
cp "$repo_root/project/new-ticket.sh" "$race/mine/project/new-ticket.sh"
cp "$repo_root/project/readme.sh" "$race/mine/project/readme.sh"
cp -R "$repo_root/template/files" "$race/mine/template/files"
cp "$repo_root/governance/work-classification.dsl.json" "$race/mine/.governance/work-classification.dsl.json"
cp "$repo_root/governance/manifest.default.json" "$race/mine/.governance/manifest.json"

# A third claim appears only after the worker clone exists. Explicit refresh
# must discover it; routine offline allocation does not require network I/O.
mkdir -p "$race/upstream/project/ticket-009"
printf '# Ticket 009\n' > "$race/upstream/project/ticket-009/README.md"
git -C "$race/upstream" -c user.email=t@e -c user.name=t add -A
git -C "$race/upstream" -c user.email=t@e -c user.name=t commit -qm 'late claim'
git -C "$race/upstream" push -q origin HEAD:refs/heads/ticket/009-late

(
  cd "$race/mine"
  bash project/new-ticket.sh --refresh-remote \
    --title 'Must not reuse a remote claim' --workstream application > alloc.out 2>&1
)
# 008 and 009 exist only on unmerged remote branches; 009 was unknown locally
# before the explicitly requested refresh.
test ! -d "$race/mine/project/ticket-008"
test ! -d "$race/mine/project/ticket-009"
test -d "$race/mine/project/ticket-010"

# ticket-010 is untracked in that clone, so the index must leave it out.
(
  cd "$race/mine"
  bash project/readme.sh > index.out 2> index.err
)
grep -q 'skipping untracked project/ticket-010' "$race/mine/index.err"
if grep -q 'ticket-010' "$race/mine/project/TICKETS.md"; then
  echo 'Index referenced an untracked ticket' >&2
  exit 1
fi

# The shared high-water mark must keep 010 reserved after its uncommitted
# directory disappears, which models allocation from another linked worktree.
# A managed base manifest is a sufficient local contract, and the default path
# must not contact even an unavailable remote.
rm -rf "$race/mine/project/ticket-010"
mv "$race/mine/.governance/manifest.json" "$race/mine/.governance/manifest.base.json"
git -C "$race/mine" remote set-url origin file:///definitely-unavailable/new-project.git
(
  cd "$race/mine"
  bash project/new-ticket.sh --title 'Must not recycle 010' --workstream integration > reserve.out 2>&1
)
test -d "$race/mine/project/ticket-011"
test ! -d "$race/mine/project/ticket-010"

# The adopted Bash entrypoint executes a dependency-free TypeScript-compatible
# runtime. Exercise exact Git/contract bindings and adversarial evidence here so
# the existing required CI job cannot omit the new contract test.
evaluation_root="$fixture/change-evaluation"
evaluation_repo="$evaluation_root/repository"
mkdir -p "$evaluation_repo"
git -C "$evaluation_repo" init -q -b main
git -C "$evaluation_repo" config user.email test@new-project.local
git -C "$evaluation_repo" config user.name new-project-test
printf '%s\n' '# Fixture' > "$evaluation_repo/README.md"
git -C "$evaluation_repo" add README.md
git -C "$evaluation_repo" commit -qm 'chore: baseline'
evaluation_base="$(git -C "$evaluation_repo" rev-parse HEAD)"
mkdir -p "$evaluation_repo/src"
printf '%s\n' 'export const answer: number = 42;' > "$evaluation_repo/src/example.ts"
git -C "$evaluation_repo" add src/example.ts
git -C "$evaluation_repo" commit -qm 'feat: add typed answer'
evaluation_head="$(git -C "$evaluation_repo" rev-parse HEAD)"
evaluation_merge_base="$(git -C "$evaluation_repo" merge-base "$evaluation_base" "$evaluation_head")"

cat > "$evaluation_root/intent.json" <<'JSON'
{
  "schema": "new-project.intent/v3",
  "ticket": "ticket-014",
  "summary": "Validate a TypeScript change",
  "workstream": "application",
  "classification": {"kind": "FEATURE", "priority": "P1", "origin": "requested"},
  "allowedPaths": ["src/**"],
  "forbiddenPaths": [],
  "stacks": ["typescript"],
  "dependsOn": [],
  "conflictsWith": [],
  "integrationTicket": null
}
JSON
printf '%s\n' '{"schema":"new-project.adoption-lock/v1","managedFiles":{}}' \
  > "$evaluation_root/manifest.lock.json"

python3 - \
  "$evaluation_root/evaluation.json" \
  "$evaluation_root/intent.json" \
  "$repo_root/CONTRIBUTING.md" \
  "$evaluation_root/manifest.lock.json" \
  "$evaluation_base" \
  "$evaluation_head" \
  "$evaluation_merge_base" <<'PY'
import copy
import hashlib
import json
import sys

output, intent_path, policy_path, lock_path, base, head, merge_base = sys.argv[1:]

def digest_bytes(value):
    return "sha256:" + hashlib.sha256(value).hexdigest()

def digest_file(file_path):
    with open(file_path, "rb") as handle:
        return digest_bytes(handle.read())

def write(name, value):
    with open(name, "w", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write("\n")

scope = {
    "actor": "github:reviewer",
    "headSha": head,
    "pullRequest": 1,
    "repository": "example/typescript-project",
    "ticket": "ticket-014",
}
scope_hash = digest_bytes(
    json.dumps(scope, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode()
)
evaluation = {
    "schemaVersion": "t2c.change-evaluation/v1",
    "subject": {
        "repository": "example/typescript-project",
        "event": "pull_request",
        "pullRequest": 1,
        "baseSha": base,
        "headSha": head,
        "mergeBaseSha": merge_base,
        "evaluatedAt": "2026-08-05T00:00:00Z",
    },
    "contract": {
        "ticket": "ticket-014",
        "workstream": "application",
        "criteria": ["AC-01"],
        "intentHash": digest_file(intent_path),
        "policyHash": digest_file(policy_path),
        "manifestLockHash": digest_file(lock_path),
        "approvalScopeHash": scope_hash,
    },
    "actors": [
        {"id": "github:author", "role": "author", "contributionTypes": ["implementation", "tests"]},
        {"id": "github:reviewer", "role": "reviewer", "contributionTypes": ["review"]},
    ],
    "changeSet": {
        "commits": [head],
        "changedPaths": ["src/example.ts"],
        "changedSymbols": ["answer"],
        "publicApiChanges": [],
        "dependencyChanges": [],
    },
    "criteriaEvaluation": [{
        "criterion": "AC-01",
        "status": "SATISFIED",
        "implementationEvidence": [
            {"type": "code-symbol", "path": "src/example.ts", "symbol": "answer", "revision": head}
        ],
        "validationEvidence": [
            {"type": "test", "reference": "runtime.accepts-exact-change", "result": "PASSED"}
        ],
        "missingEvidence": [],
        "confidence": 1.0,
    }],
    "gates": {
        "governance": "PASS",
        "scope": "PASS",
        "secrets": "PASS",
        "tests": "PASS",
        "regression": "PASS",
        "documentation": "NOT_APPLICABLE",
        "approval": "PASS",
        "evidenceCompleteness": "PASS",
    },
    "dimensions": {
        "governanceCompliance": "PASS",
        "intentAlignment": "PASS",
        "implementationCorrectness": "PASS",
        "projectDirection": "PASS",
        "changeReasonableness": "PASS",
        "contributionValue": "PASS",
        "evidenceConfidence": "PASS",
    },
    "approval": {
        "status": "VERIFIED",
        "source": "github-review",
        "actor": "github:reviewer",
        "actorRole": "human",
        "verificationMethod": "github-api-allowlist",
        "headSha": head,
        "approvalScopeHash": scope_hash,
        "evidenceDigest": "sha256:" + "a" * 64,
    },
    "findings": [],
    "contribution": {"claims": [{
        "actor": "github:author",
        "type": "implementation",
        "criterion": "AC-01",
        "evidence": [{"type": "commit", "reference": head, "revision": head}],
    }]},
    "verdict": {
        "merge": "ALLOWED",
        "completion": "ACCEPTED",
        "reasonCodes": [],
        "requiredHumanDecisions": [],
    },
    "confidence": {"overall": 1.0, "unknowns": []},
    "provenance": {
        "evaluatorVersion": "todo2code-test",
        "generatedByWorkflow": "todo2code/change-evaluation",
    },
}
write(output, evaluation)

mutation = copy.deepcopy(evaluation)
mutation["contract"]["intentHash"] = "sha256:" + "0" * 64
write(output.replace("evaluation.json", "hash-mismatch.json"), mutation)

mutation = copy.deepcopy(evaluation)
mutation["criteriaEvaluation"][0]["validationEvidence"] = []
write(output.replace("evaluation.json", "missing-evidence.json"), mutation)

mutation = copy.deepcopy(evaluation)
mutation["approval"]["headSha"] = base
write(output.replace("evaluation.json", "stale-approval.json"), mutation)

mutation = copy.deepcopy(evaluation)
mutation["gates"]["tests"] = "FAILED"
write(output.replace("evaluation.json", "failed-gate.json"), mutation)

mutation = copy.deepcopy(evaluation)
mutation["gates"]["tests"] = "FAILED"
mutation["verdict"]["merge"] = "BLOCKED"
mutation["verdict"]["completion"] = "NOT_DONE"
mutation["verdict"]["reasonCodes"] = ["EVD-GATE-TESTS"]
write(output.replace("evaluation.json", "blocked.json"), mutation)
PY

python3 - \
  "$repo_root/governance/change-evaluation.schema.json" \
  "$evaluation_root/evaluation.json" <<'PY'
import json
import sys
from jsonschema import Draft202012Validator

schema = json.load(open(sys.argv[1], encoding="utf-8"))
evaluation = json.load(open(sys.argv[2], encoding="utf-8"))
Draft202012Validator.check_schema(schema)
Draft202012Validator(schema, format_checker=Draft202012Validator.FORMAT_CHECKER).validate(evaluation)
PY

runtime="$repo_root/scripts/runtime.sh"
bash "$runtime" policy --policy "$repo_root/CONTRIBUTING.md" > "$evaluation_root/policy.json"
grep -Fq '"valid": true' "$evaluation_root/policy.json"

validate_evaluation() {
  local evaluation="$1"
  shift
  bash "$runtime" validate \
    --evaluation "$evaluation" \
    --intent "$evaluation_root/intent.json" \
    --policy "$repo_root/CONTRIBUTING.md" \
    --manifest-lock "$evaluation_root/manifest.lock.json" \
    --repository-root "$evaluation_repo" \
    "$@"
}

validate_evaluation "$evaluation_root/evaluation.json" \
  --json-out "$evaluation_root/validated.json" \
  --markdown-out "$evaluation_root/evaluation.md" > "$evaluation_root/first.json"
validate_evaluation "$evaluation_root/evaluation.json" > "$evaluation_root/second.json"
cmp -s "$evaluation_root/first.json" "$evaluation_root/second.json"
cmp -s "$evaluation_root/first.json" "$evaluation_root/validated.json"
grep -Fq '"valid": true' "$evaluation_root/first.json"
grep -Fq '"mergeAllowed": true' "$evaluation_root/first.json"
grep -Fq 'Merge verdict: ALLOWED' "$evaluation_root/evaluation.md"

expect_evaluation_failure() {
  local code="$1"
  local evaluation="$2"
  local output="$3"
  if validate_evaluation "$evaluation" > "$output" 2> "$output.err"; then
    echo "expected evaluation failure containing $code" >&2
    exit 1
  fi
  grep -Fq "$code" "$output"
}

expect_evaluation_failure \
  INT-HASH-001 "$evaluation_root/hash-mismatch.json" "$evaluation_root/hash-mismatch.out"
expect_evaluation_failure \
  EVD-CRITERION-002 "$evaluation_root/missing-evidence.json" "$evaluation_root/missing-evidence.out"
expect_evaluation_failure \
  APR-STALE-001 "$evaluation_root/stale-approval.json" "$evaluation_root/stale-approval.out"
expect_evaluation_failure \
  INT-VERDICT-001 "$evaluation_root/failed-gate.json" "$evaluation_root/failed-gate.out"

if validate_evaluation "$evaluation_root/blocked.json" > "$evaluation_root/blocked.out"; then
  echo 'expected a valid BLOCKED evaluation to stop publication' >&2
  exit 1
fi
grep -Fq '"valid": true' "$evaluation_root/blocked.out"
grep -Fq '"mergeAllowed": false' "$evaluation_root/blocked.out"

python3 - \
  "$evaluation_root/intent.json" \
  "$evaluation_root/scope-intent.json" \
  "$evaluation_root/evaluation.json" \
  "$evaluation_root/scope.json" <<'PY'
import hashlib
import json
import sys

source_intent, scoped_intent, source_evaluation, scoped_evaluation = sys.argv[1:]
intent = json.load(open(source_intent, encoding="utf-8"))
intent["allowedPaths"] = ["docs/**"]
with open(scoped_intent, "w", encoding="utf-8") as handle:
    json.dump(intent, handle, indent=2)
    handle.write("\n")
evaluation = json.load(open(source_evaluation, encoding="utf-8"))
evaluation["contract"]["intentHash"] = (
    "sha256:" + hashlib.sha256(open(scoped_intent, "rb").read()).hexdigest()
)
json.dump(evaluation, open(scoped_evaluation, "w", encoding="utf-8"), indent=2)
PY
if bash "$runtime" validate \
  --evaluation "$evaluation_root/scope.json" \
  --intent "$evaluation_root/scope-intent.json" \
  --policy "$repo_root/CONTRIBUTING.md" \
  --manifest-lock "$evaluation_root/manifest.lock.json" \
  --repository-root "$evaluation_repo" > "$evaluation_root/scope.out"; then
  echo 'expected out-of-scope evaluation to fail' >&2
  exit 1
fi
grep -Fq 'GOV-SCOPE-001' "$evaluation_root/scope.out"

sed '/^RULE C-EVALUATION-010 /d' \
  "$repo_root/CONTRIBUTING.md" > "$evaluation_root/incomplete-policy.md"
if bash "$runtime" policy \
  --policy "$evaluation_root/incomplete-policy.md" > "$evaluation_root/incomplete-policy.out"; then
  echo 'expected incomplete evaluation policy to fail' >&2
  exit 1
fi
grep -Fq 'EVD-POLICY-001' "$evaluation_root/incomplete-policy.out"

remediation_root="$fixture/remediation-intent"
mkdir -p "$remediation_root"
python3 - "$remediation_root" <<'PY'
import copy
import hashlib
import json
import pathlib
import sys

root = pathlib.Path(sys.argv[1])

def finding(fid, category, priority, code, current, required, path, criterion, *, excluded=None):
    return {
        "id": fid,
        "category": category,
        "status": "CONFIRMED",
        "priority": priority,
        "summary": f"Evidence-backed scenario for {code}.",
        "diagnostic": {"code": code, "current": current, "required": required},
        "evidence": [{"ref": f"diagit-report.json#/{fid}", "observation": f"Observed {code}."}],
        "applicability": {
            "requiredSignals": [f"Positive runtime signal for {code}."],
            "excludedSignals": excluded or [],
            "unknownOutcome": "BLOCK",
        },
        "desiredOutcome": f"Make {code} deterministic without expanding scope.",
        "affectedPaths": [path],
        "dependsOn": [],
        "acceptanceCriteria": [criterion],
    }

findings = [
    finding(
        "F-OPENROUTER", "FALSE_POSITIVE", "P1", "OPENROUTER_APP_IDENTITY_MISSING",
        "FALSE_POSITIVE", "REFINE", "src/openrouter_detector.py", "AC-01",
        excluded=["Detector source, documentation and tests merely mention OPENROUTER_* variables."],
    ),
    finding(
        "F-UNREADABLE", "SILENT_OMISSION", "P1", "DISCOVERY_PATH_UNREADABLE",
        "MISSING", "EMIT", "src/discovery.py", "AC-02",
    ),
    finding(
        "F-LAYOUT", "AMBIGUOUS_HEURISTIC", "P2", "DISCOVERY_LAYOUT_AMBIGUOUS",
        "DRIFT", "REFINE", "src/discovery.py", "AC-03",
    ),
    finding(
        "F-INVENTORY", "MISSING_INVENTORY", "P2", "EXPECTED_REPOSITORY_MISSING",
        "MISSING", "EMIT", "inventory/repositories.json", "AC-04",
    ),
    finding(
        "F-DIRTY", "STATE_RISK", "P1", "WORKTREE_DIRTY",
        "EMITTED", "PRESERVE", "worktrees/**", "AC-05",
    ),
    finding(
        "F-RELEASE", "CONTRACT_DRIFT", "P2", "RELEASE_VERSION_DRIFT",
        "DRIFT", "REFINE", "CHANGELOG.md", "AC-06",
    ),
]

action_specs = [
    ("A-OPENROUTER", "F-OPENROUTER", "IMPLEMENT", ["src/openrouter_detector.py"], []),
    ("A-UNREADABLE", "F-UNREADABLE", "IMPLEMENT", ["src/discovery.py"], []),
    ("A-LAYOUT", "F-LAYOUT", "IMPLEMENT", ["src/discovery.py"], ["A-UNREADABLE"]),
    ("A-INVENTORY", "F-INVENTORY", "IMPLEMENT", ["inventory/repositories.json"], []),
    ("A-PRESERVE", "F-DIRTY", "PRESERVE", ["worktrees/**"], []),
    (
        "A-RELEASE", "F-RELEASE", "RELEASE", ["CHANGELOG.md", "VERSION"],
        ["A-OPENROUTER", "A-UNREADABLE", "A-PRESERVE"],
    ),
]
actions = []
verifications = []
criteria = []
for index, ((aid, fid, operation, paths, depends), item) in enumerate(zip(action_specs, findings), 1):
    vid = f"V-{index:02d}"
    action = {
        "id": aid,
        "findingIds": [fid],
        "operation": operation,
        "description": f"Resolve {fid} and preserve its applicability contract.",
        "paths": paths,
        "dependsOn": depends,
        "verificationIds": [vid],
        "risk": {
            "level": "READ_ONLY" if operation == "PRESERVE" else "REVERSIBLE_WRITE",
            "authorization": "NOT_APPLICABLE" if operation == "PRESERVE" else "SESSION_EXECUTION_AUTHORIZATION",
            "automation": "PROHIBITED" if operation == "PRESERVE" else "ALLOWED",
            "preservesUserData": True,
        },
    }
    actions.append(action)
    verifications.append({
        "id": vid,
        "type": "COMMAND",
        "command": f"pytest -q tests/test_{index:02d}.py",
        "expected": f"Deterministic regression for {fid} passes.",
        "deterministic": True,
        "covers": [fid, aid],
    })
    criteria.append({
        "id": f"AC-{index:02d}",
        "statement": f"{fid} has the required diagnostic transition and regression proof.",
        "findingIds": [fid],
        "verificationIds": [vid],
    })

intent = {
    "schema": "new-project.remediation-intent/v1",
    "intentId": "RI-DIAGIT-DISCOVERY",
    "ticket": "ticket-123",
    "repository": "subactor/diagit",
    "ownerRoute": "github:subactor-maintainer",
    "status": "READY",
    "source": {
        "producer": {"name": "diagit", "version": "0.10.1"},
        "observedAt": "2026-08-12T10:00:00Z",
        "reportDigest": hashlib.sha256(b"diagit fleet report").hexdigest(),
    },
    "objective": {
        "outcome": "Make discovery findings applicable, complete and safe before publication.",
        "nonGoals": ["Do not clean dirty worktrees or publish from this planning intent."],
        "constraints": ["Preserve user state and require explicit signals before suppressing a finding."],
    },
    "scope": {
        "allowedPaths": ["src/**", "tests/**", "inventory/**", "worktrees/**", "CHANGELOG.md", "VERSION"],
        "forbiddenPaths": [".env", "secrets/**"],
        "preservePaths": ["worktrees/**"],
    },
    "findings": findings,
    "actions": actions,
    "verifications": verifications,
    "acceptanceCriteria": criteria,
    "llmGuidance": {
        "role": "Plan a bounded refactoring from accepted findings; do not approve or publish it.",
        "mustPreserve": ["Dirty and unclassified worktrees.", "Positive and excluded applicability signals."],
        "forbiddenAssumptions": ["Do not treat detector source as a real OpenRouter client.", "Do not infer a missing repository or unreadable path is absent."],
        "planningOrder": [item[0] for item in action_specs],
        "openQuestions": [],
    },
    "todo2code": {
        "enabled": True,
        "taskPath": "project/ticket-123/REMEDIATION.task.md",
        "todoPath": "project/ticket-123/REMEDIATION.todo.md",
        "planSchema": "t2c.code-change-plan/v1",
        "requiredDiagnosticCodes": [
            "AMBIGUOUS_REQUIREMENT",
            "HUMAN_AGENT_CONFLICT",
            "HUMAN_COMMUNICATION_CONFLICT",
            "PLANNED_NOT_IMPLEMENTED",
        ],
    },
}

def write(name, value):
    (root / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

write("intent.json", intent)
mutations = {
    "missing-exclusion.json": lambda value: value["findings"][0]["applicability"].update(excludedSignals=[]),
    "action-cycle.json": lambda value: value["actions"][0].update(dependsOn=["A-RELEASE"]),
    "unsafe-preserve.json": lambda value: value["actions"][4]["risk"].update(automation="ALLOWED"),
    "release-too-early.json": lambda value: value["actions"][5].update(dependsOn=[]),
    "unresolved-owner.json": lambda value: value.update(ownerRoute="unresolved:human"),
    "missing-t2c-capability.json": lambda value: value["todo2code"].update(
        requiredDiagnosticCodes=["AMBIGUOUS_REQUIREMENT"]
    ),
}
for name, mutate in mutations.items():
    value = copy.deepcopy(intent)
    mutate(value)
    write(name, value)

graph = {
    "schemaVersion": "t2c.graph/v1",
    "records": [
        {
            "id": "INT-NL-projection-task",
            "source": {"path": intent["todo2code"]["taskPath"]},
        },
        {
            "id": "INT-TODO-projection-todo",
            "source": {"path": intent["todo2code"]["todoPath"]},
        },
        {
            "id": "INT-TODO-unrelated-history",
            "source": {"path": "TODO.md"},
        },
    ],
}
diagnostics = {
    "schemaVersion": "t2c.diagnostics/v1",
    "diagnostics": [{
        "id": "DIAG-UNRELATED",
        "code": "AMBIGUOUS_REQUIREMENT",
        "recordIds": ["INT-TODO-unrelated-history"],
        "detail": "Unrelated historical ambiguity must not enter this overlay.",
        "suggestedAction": "Repair the unrelated historical ticket separately.",
    }],
}
plan_text = " ".join(
    [item["id"] + " " + item["diagnostic"]["code"] for item in findings]
    + [item["id"] + " " + item["statement"] for item in criteria]
)
plans = {
    "schemaVersion": "t2c.code-change-plan-set/v1",
    "generation": {"runtimeVersion": "0.17.2"},
    "plans": [{
        "schemaVersion": "t2c.code-change-plan/v1",
        "id": "CPLAN-DIAGIT",
        "title": plan_text,
        "priority": "P1",
        "target": {"paths": ["src/openrouter_detector.py", "src/discovery.py", "inventory/repositories.json", "worktrees/**", "CHANGELOG.md", "VERSION"]},
        "changes": [{"path": "src/discovery.py", "action": "modify"}],
        "acceptanceCriteria": [item["id"] + " " + item["statement"] for item in criteria],
        "evidence": {"recordIds": ["INT-NL-projection-task"]},
    }, {
        "schemaVersion": "t2c.code-change-plan/v1",
        "id": "CPLAN-HISTORY",
        "title": "Unrelated historical plan.",
        "priority": "P0",
        "target": {"paths": ["secrets/history.txt"]},
        "changes": [{"path": "secrets/history.txt", "action": "delete"}],
        "acceptanceCriteria": ["Unrelated history remains independent."],
        "evidence": {"recordIds": ["INT-TODO-unrelated-history"]},
    }],
}
write("graph.json", graph)
write("diagnostics.json", diagnostics)
write("plans.json", plans)
relevant_diagnostics = copy.deepcopy(diagnostics)
relevant_diagnostics["diagnostics"][0]["id"] = "DIAG-RELEVANT"
relevant_diagnostics["diagnostics"][0]["recordIds"] = ["INT-TODO-projection-todo"]
relevant_diagnostics["diagnostics"][0]["detail"] = "Relevant projection ambiguity."
write("relevant-diagnostics.json", relevant_diagnostics)
unsafe_plans = copy.deepcopy(plans)
unsafe_plans["plans"][0]["target"]["paths"].append("secrets.txt")
unsafe_plans["plans"][0]["changes"].append({"path": "worktrees/local", "action": "delete"})
write("unsafe-plans.json", unsafe_plans)
PY

python3 - \
  "$repo_root/governance/remediation-intent.schema.json" \
  "$repo_root/template/files/remediation-intent.template.dsl.json" \
  "$remediation_root/intent.json" <<'PY'
import json
import sys
from jsonschema import Draft202012Validator

schema = json.load(open(sys.argv[1], encoding="utf-8"))
Draft202012Validator.check_schema(schema)
validator = Draft202012Validator(schema, format_checker=Draft202012Validator.FORMAT_CHECKER)
validator.validate(json.load(open(sys.argv[2], encoding="utf-8")))
validator.validate(json.load(open(sys.argv[3], encoding="utf-8")))
PY

remediation="$repo_root/scripts/remediation_intent.py"
python3 "$remediation" validate "$remediation_root/intent.json" --format json > "$remediation_root/validation.json"
grep -Fq '"ok": true' "$remediation_root/validation.json"
python3 "$remediation" validate "$repo_root/template/files/remediation-intent.template.dsl.json" > "$remediation_root/template.out"
grep -Fq '0 errors' "$remediation_root/template.out"
if python3 "$remediation" render-llm \
  "$repo_root/template/files/remediation-intent.template.dsl.json" \
  > "$remediation_root/draft-brief.out" 2>&1; then
  echo 'expected DRAFT remediation intent to be rejected before LLM projection' >&2
  exit 1
fi
grep -Fq 'GOV-REMEDIATION-001' "$remediation_root/draft-brief.out"

python3 "$remediation" render-llm "$remediation_root/intent.json" --out "$remediation_root/brief.md"
grep -Fq 'OPENROUTER_APP_IDENTITY_MISSING' "$remediation_root/brief.md"
grep -Fq 'Detector source, documentation and tests' "$remediation_root/brief.md"
grep -Fq 'Dirty and unclassified worktrees' "$remediation_root/brief.md"
python3 "$remediation" render-todo2code "$remediation_root/intent.json" \
  --task-out "$remediation_root/task.md" --todo-out "$remediation_root/TODO.md"
grep -Fq 'F-UNREADABLE/DISCOVERY_PATH_UNREADABLE/P1' "$remediation_root/task.md"
grep -Fq 'AC-05' "$remediation_root/TODO.md"
python3 - "$remediation_root/task.md" "$remediation_root/TODO.md" <<'PY'
import pathlib
import re
import sys

task = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8").splitlines()
todo = pathlib.Path(sys.argv[2]).read_text(encoding="utf-8").splitlines()
task_records = [line for line in task if line and not line.startswith("#")]
todo_records = [re.sub(r"^- \[ \] ", "", line) for line in todo if line.startswith("- [ ] ")]
assert len(task_records) == 6, task_records
assert task_records == todo_records
assert all(re.match(r"^(?:fix|test|docs|build|chore)\(remediation\):", line) for line in task_records)
assert all("verification V-" in line and "expected=" in line for line in task_records)
PY

projection_repo="$remediation_root/projection-repo"
mkdir -p "$projection_repo"
python3 "$remediation" render-todo2code "$remediation_root/intent.json" --root "$projection_repo"
python3 "$remediation" verify-todo2code "$remediation_root/intent.json" \
  --root "$projection_repo" --format json > "$remediation_root/projection-verification.json"
grep -Fq '"ok": true' "$remediation_root/projection-verification.json"
printf '%s\n' 'manual drift' >> "$projection_repo/project/ticket-123/REMEDIATION.task.md"
if python3 "$remediation" verify-todo2code "$remediation_root/intent.json" \
  --root "$projection_repo" > "$remediation_root/projection-drift.out" 2>&1; then
  echo 'expected byte-drifted remediation projection to fail' >&2
  exit 1
fi
grep -Fq 'GOV-REMEDIATION-004' "$remediation_root/projection-drift.out"
python3 "$remediation" render-todo2code "$remediation_root/intent.json" --root "$projection_repo"
python3 - "$projection_repo/project/ticket-123/REMEDIATION.todo.md" <<'PY'
import pathlib
import sys
pathlib.Path(sys.argv[1]).unlink()
PY
if python3 "$remediation" verify-todo2code "$remediation_root/intent.json" \
  --root "$projection_repo" > "$remediation_root/projection-missing.out" 2>&1; then
  echo 'expected missing remediation projection to fail' >&2
  exit 1
fi
grep -Fq 'GOV-REMEDIATION-004' "$remediation_root/projection-missing.out"
escape_repo="$remediation_root/escape-repo"
escape_target="$remediation_root/escape-target"
mkdir -p "$escape_repo" "$escape_target"
ln -s "$escape_target" "$escape_repo/project"
if python3 "$remediation" render-todo2code "$remediation_root/intent.json" \
  --root "$escape_repo" > "$remediation_root/projection-escape.out" 2>&1; then
  echo 'expected symlink-escaped remediation projection to fail' >&2
  exit 1
fi
grep -Fq 'GOV-REMEDIATION-004' "$remediation_root/projection-escape.out"

expect_remediation_failure() {
  local input="$1"
  local output="$2"
  if python3 "$remediation" validate "$input" > "$output" 2>&1; then
    echo "expected remediation validation failure for $input" >&2
    exit 1
  fi
  grep -Fq 'GOV-REMEDIATION-001' "$output"
}
expect_remediation_failure "$remediation_root/missing-exclusion.json" "$remediation_root/missing-exclusion.out"
expect_remediation_failure "$remediation_root/action-cycle.json" "$remediation_root/action-cycle.out"
expect_remediation_failure "$remediation_root/unsafe-preserve.json" "$remediation_root/unsafe-preserve.out"
expect_remediation_failure "$remediation_root/release-too-early.json" "$remediation_root/release-too-early.out"
expect_remediation_failure "$remediation_root/unresolved-owner.json" "$remediation_root/unresolved-owner.out"
expect_remediation_failure "$remediation_root/missing-t2c-capability.json" "$remediation_root/missing-t2c-capability.out"

python3 "$remediation" analyze-todo2code "$remediation_root/intent.json" \
  --graph "$remediation_root/graph.json" \
  --diagnostics "$remediation_root/diagnostics.json" \
  --plans "$remediation_root/plans.json" \
  --out "$remediation_root/analyzed.json"
python3 "$remediation" validate "$remediation_root/analyzed.json" --format json > "$remediation_root/analyzed-validation.json"
grep -Fq '"ok": true' "$remediation_root/analyzed-validation.json"
grep -Fq '"authority": "ADVISORY"' "$remediation_root/analyzed.json"
grep -Fq '"graphDigest"' "$remediation_root/analyzed.json"
grep -Fq 'INT-NL-projection-task' "$remediation_root/analyzed.json"
grep -Fq 'INT-TODO-projection-todo' "$remediation_root/analyzed.json"
grep -Fq 'CPLAN-DIAGIT' "$remediation_root/analyzed.json"
if grep -Fq 'CPLAN-HISTORY' "$remediation_root/analyzed.json"; then
  echo 'unrelated historical todo2code plan entered remediation overlay' >&2
  exit 1
fi
if grep -Fq 'Unrelated historical ambiguity' "$remediation_root/analyzed.json"; then
  echo 'unrelated historical todo2code diagnostic entered remediation overlay' >&2
  exit 1
fi

python3 "$remediation" analyze-todo2code "$remediation_root/intent.json" \
  --graph "$remediation_root/graph.json" \
  --diagnostics "$remediation_root/relevant-diagnostics.json" \
  --plans "$remediation_root/plans.json" \
  --out "$remediation_root/relevant-ambiguity.json"
grep -Fq 'T2C_AMBIGUOUS_INTENT' "$remediation_root/relevant-ambiguity.json"
grep -Fq 'Relevant projection ambiguity' "$remediation_root/relevant-ambiguity.json"

if python3 "$remediation" analyze-todo2code "$remediation_root/intent.json" \
  --graph "$remediation_root/graph.json" \
  --diagnostics "$remediation_root/diagnostics.json" \
  --plans "$remediation_root/unsafe-plans.json" \
  --out "$remediation_root/unsafe-analyzed.json" > "$remediation_root/unsafe.out" 2>&1; then
  echo 'expected unsafe todo2code plan to block' >&2
  exit 1
fi
grep -Fq 'GOV-REMEDIATION-002' "$remediation_root/unsafe.out"
grep -Fq 'T2C_SCOPE_EXPANSION' "$remediation_root/unsafe-analyzed.json"
grep -Fq 'T2C_UNAUTHORIZED_DELETION' "$remediation_root/unsafe-analyzed.json"

python3 - "$remediation_root/analyzed.json" "$remediation_root/stale.json" <<'PY'
import json
import sys
value = json.load(open(sys.argv[1], encoding="utf-8"))
value["objective"]["outcome"] += " Changed after analysis."
with open(sys.argv[2], "w", encoding="utf-8") as handle:
    json.dump(value, handle, ensure_ascii=False, indent=2)
    handle.write("\n")
PY
if python3 "$remediation" validate "$remediation_root/stale.json" > "$remediation_root/stale.out" 2>&1; then
  echo 'expected stale advisory digest to fail' >&2
  exit 1
fi
grep -Fq 'GOV-REMEDIATION-003' "$remediation_root/stale.out"

echo 'governance scripts: PASS'
