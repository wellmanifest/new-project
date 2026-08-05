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
cp -R "$repo_root/template/files" "$fixture/template/files"
# A real adopted target always carries the work classification contract, because
# the package manifest ships it. The scaffolder reads the accepted dimension
# values from it instead of hardcoding them, so the fixture must mirror that.
cp "$repo_root/governance/work-classification.dsl.json" "$fixture/.governance/work-classification.dsl.json"
printf '%s\n' '# Analysis-owned project README' > "$fixture/project/README.md"

status=0
(
  cd "$fixture"
  bash project/new-ticket.sh --title 'Missing workstream' > missing-workstream.out 2> missing-workstream.err
) || status=$?
test "$status" -eq 2
grep -q 'Workstream is required' "$fixture/missing-workstream.err"
test ! -d "$fixture/project/ticket-001"

(
  cd "$fixture"
  bash project/new-ticket.sh --title 'Validate "A&B" / routes' --agent Codex --workstream application --users alice \
    > first.out 2> first.err
)

ticket="$fixture/project/ticket-001"
test -f "$ticket/README.md"
test -f "$ticket/preprompt.md"
test -f "$ticket/intent.json"
test -f "$ticket/ai-codex.md"
test -f "$ticket/ai-codex-logs.txt"
test -f "$ticket/changelog.md"
test ! -e "$ticket/user-alice.md"
grep -q 'unresolved:human' "$ticket/README.md"
grep -q 'participant-id: agent:codex' "$ticket/ai-codex.md"
grep -q 'did not create user-\* files' "$fixture/first.err"
grep -qx '# Analysis-owned project README' "$fixture/project/README.md"
grep -q 'ticket-001' "$fixture/project/TICKETS.md"
if grep -q '{[A-Z_-]*}' "$ticket/README.md" "$ticket/preprompt.md" "$ticket/ai-codex.md"; then
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

sed -i 's/\*\*Status\*\*: PLAN/**Status**: IN_PROGRESS/' "$ticket/README.md"

status=0
(
  cd "$fixture"
  bash project/new-ticket.sh --title 'Must reuse active ticket' --agent codex --workstream application \
    > second.out 2> second.err
) || status=$?
test "$status" -eq 3
grep -q "Active ticket conflicts with workstream 'application': project/ticket-001" "$fixture/second.err"
test ! -d "$fixture/project/ticket-002"

sed -i 's/\*\*Status\*\*: IN_PROGRESS/**Status**: BLOCKED/' "$ticket/README.md"
(
  cd "$fixture"
  bash project/new-ticket.sh --title 'Replacement application ticket' --agent codex-2 \
    --workstream application > replacement.out
)
test -d "$fixture/project/ticket-002"
grep -q '"workstream": "application"' "$fixture/project/ticket-002/intent.json"

(
  cd "$fixture"
  bash project/new-ticket.sh --title 'Parallel interface ticket' --agent codex-2 \
    --workstream interfaces > parallel.out
)
test -d "$fixture/project/ticket-003"
grep -q '"workstream": "interfaces"' "$fixture/project/ticket-003/intent.json"

sed -i 's/\*\*Status\*\*: BLOCKED/**Status**: DONE/' "$ticket/README.md"
sed -i 's/\*\*Status\*\*: PLAN/**Status**: DONE/' "$fixture/project/ticket-002/README.md"
sed -i 's/\*\*Status\*\*: PLAN/**Status**: DONE/' "$fixture/project/ticket-003/README.md"
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
git -C "$race/mine" fetch -q origin '+refs/heads/*:refs/remotes/origin/*'

(
  cd "$race/mine"
  bash project/new-ticket.sh --title 'Must not reuse 008' --workstream application > alloc.out 2>&1
)
# 008 exists only on an unmerged remote branch, so disk alone would have picked it.
test ! -d "$race/mine/project/ticket-008"
test -d "$race/mine/project/ticket-009"

# ticket-009 is untracked in that clone, so the index must leave it out.
(
  cd "$race/mine"
  bash project/readme.sh > index.out 2> index.err
)
grep -q 'skipping untracked project/ticket-009' "$race/mine/index.err"
if grep -q 'ticket-009' "$race/mine/project/TICKETS.md"; then
  echo 'Index referenced an untracked ticket' >&2
  exit 1
fi

# The shared high-water mark must keep 009 reserved after its uncommitted
# directory disappears, which models allocation from another linked worktree.
rm -rf "$race/mine/project/ticket-009"
(
  cd "$race/mine"
  bash project/new-ticket.sh --title 'Must not recycle 009' --workstream integration > reserve.out 2>&1
)
test -d "$race/mine/project/ticket-010"
test ! -d "$race/mine/project/ticket-009"

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

echo 'governance scripts: PASS'
