#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
fixture="$(mktemp -d "${TMPDIR:-/tmp}/new-project-validator-test.XXXXXX")"
cleanup() {
  rm -rf "$fixture"
}
trap cleanup EXIT INT TERM

python3 - "$repo_root/governance/manifest.schema.json" "$repo_root/governance/manifest.default.json" \
  "$repo_root/governance/approval-evidence.schema.json" <<'PY'
import json
import sys

schema = json.load(open(sys.argv[1], encoding='utf-8'))
manifest = json.load(open(sys.argv[2], encoding='utf-8'))
approval_schema = json.load(open(sys.argv[3], encoding='utf-8'))
assert schema['additionalProperties'] is False
assert set(manifest) <= set(schema['properties'])
assert set(schema['required']) <= set(manifest)
assert manifest['schema'] == schema['properties']['schema']['const']
assert manifest['standard']['version'] == '0.9.0'
ticket = manifest['ticket']
assert ticket['activeStatuses'] == ['IN_PROGRESS']
assert ticket['nonActiveStatuses'] == ['BACKLOG', 'PLAN', 'BLOCKED']
assert not set(ticket['activeStatuses']) & set(ticket['nonActiveStatuses'])
assert 'github-app-review' in manifest['trustedApprovalSources']
assert manifest['approvalEvidence']['schema'] == 'new-project.approval-evidence/v1'
assert approval_schema['properties']['headSha']['pattern'] == '^[0-9a-f]{40}$'
PY
python3 - "$repo_root/scripts/governance_check.py" <<'PY'
import importlib.util
import sys

spec = importlib.util.spec_from_file_location('governance_check', sys.argv[1])
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
assert module.matches('src/nested/app.js', ['src/**'])
assert not module.matches('src/nested/app.js', ['src/*'])
assert module.patterns_may_overlap('future/**', 'future/*.js')
assert not module.patterns_may_overlap('src/**/x.json', 'src/**/y.json')
assert module.pattern_covered_by('src/**/*.js', 'src/**')
PY
python3 - "$repo_root/scripts/governance_check.py" "$repo_root/governance/diagnostics.json" <<'PY'
import json
import re
import sys

source = open(sys.argv[1], encoding='utf-8').read()
catalog = set(json.load(open(sys.argv[2], encoding='utf-8'))['codes'])
emitted = set(re.findall(r'report\.add\(\s*["\'](GOV-[A-Z]+-[0-9]+)', source))
assert emitted == catalog, (sorted(emitted - catalog), sorted(catalog - emitted))
PY
grep -q 'review.commit_id === head' "$repo_root/.github/workflows/governance.yml"
grep -Fq '^[0-9a-f]{40}$' "$repo_root/.github/workflows/governance.yml"
grep -q 'trustedReviewers.has(normalize(review.user.login))' "$repo_root/.github/workflows/governance.yml"
grep -q 'trustedValidatorApps.has(normalize(review.user.login))' "$repo_root/.github/workflows/governance.yml"
grep -q 'trustedReviewers.size + trustedValidatorApps.size === 0' "$repo_root/.github/workflows/governance.yml"
grep -q "process.env.TRUSTED_REVIEWERS" "$repo_root/.github/workflows/governance.yml"
grep -q "process.env.TRUSTED_VALIDATOR_APPS" "$repo_root/.github/workflows/governance.yml"
grep -q 'APPROVAL_EVIDENCE_PATH.*runner.temp' "$repo_root/.github/workflows/governance.yml"
grep -q 'ref:.*github.event.pull_request.head.sha' "$repo_root/.github/workflows/governance.yml"
grep -Fq "'/.new-project-standard/' >> .git/info/exclude" "$repo_root/.github/workflows/governance.yml"
if grep -q "Set('\${{ inputs.trusted-reviewers }}'" "$repo_root/.github/workflows/governance.yml"; then
  echo 'trusted-reviewers is interpolated into JavaScript source' >&2
  exit 1
fi
if grep -q "Set('\${{ inputs.trusted-validator-apps }}'" "$repo_root/.github/workflows/governance.yml"; then
  echo 'trusted-validator-apps is interpolated into JavaScript source' >&2
  exit 1
fi

make_fixture() {
  local target="$1"
  mkdir -p "$target/.governance" "$target/project/ticket-001" "$target/project/ticket-002" "$target/src"
  cp "$repo_root/scripts/governance_check.py" "$target/.governance/governance_check.py"
  cp "$repo_root/governance/manifest.default.json" "$target/.governance/manifest.json"
  cp "$repo_root/governance/stack-profiles.json" "$target/.governance/stack-profiles.json"
  touch "$target/README.md" "$target/CHANGELOG.md" "$target/TODO.md" "$target/AGENTS.md"
  touch "$target/Dockerfile" "$target/compose.yml" "$target/project/TICKETS.md"
  touch "$target/project/new-ticket.sh" "$target/project/readme.sh"
  printf '%s\n' '0.1.0' > "$target/VERSION"
  printf '%s\n' '# Ticket 001' '- **Status**: DONE' '- **Workflow state**: DONE' > "$target/project/ticket-001/README.md"
  printf '%s\n' '# Ticket 002' '- **Status**: IN_PROGRESS' '- **Workflow state**: EDIT' > "$target/project/ticket-002/README.md"
  touch "$target/project/ticket-002/preprompt.md" "$target/project/ticket-002/changelog.md"
  touch "$target/project/ticket-002/ai-codex.md" "$target/project/ticket-002/ai-codex-logs.txt"
  cat > "$target/project/ticket-002/intent.json" <<'JSON'
{
  "schema": "new-project.intent/v2",
  "ticket": "ticket-002",
  "summary": "Fixture implementation",
  "workstream": "application",
  "allowedPaths": ["src/**"],
  "forbiddenPaths": ["project/ticket-*/user-*.md"],
  "stacks": ["node", "docker"],
  "dependsOn": [],
  "conflictsWith": [],
  "integrationTicket": null
}
JSON
  printf '%s\n' '{"name":"fixture"}' > "$target/package.json"
  printf '%s\n' 'export const ok = true;' > "$target/src/app.js"
  printf '%s\n' 'OPENROUTER_API_KEY= T2C_NL_MODE=deterministic' > "$target/README.md"
}

add_active_ticket() {
  local target="$1"
  local ticket="$2"
  local workstream="$3"
  local allowed_paths="$4"
  local depends_on="${5:-[]}"
  local conflicts_with="${6:-[]}"
  mkdir -p "$target/project/$ticket"
  printf '%s\n' "# $ticket" '- **Status**: IN_PROGRESS' '- **Workflow state**: EDIT' > "$target/project/$ticket/README.md"
  touch "$target/project/$ticket/preprompt.md" "$target/project/$ticket/changelog.md"
  touch "$target/project/$ticket/ai-codex.md" "$target/project/$ticket/ai-codex-logs.txt"
  cat > "$target/project/$ticket/intent.json" <<JSON
{
  "schema": "new-project.intent/v2",
  "ticket": "$ticket",
  "summary": "Parallel fixture",
  "workstream": "$workstream",
  "allowedPaths": $allowed_paths,
  "forbiddenPaths": ["project/ticket-*/user-*.md"],
  "stacks": ["node", "docker"],
  "dependsOn": $depends_on,
  "conflictsWith": $conflicts_with,
  "integrationTicket": null
}
JSON
}

run_check() {
  local target="$1"
  shift
  python3 "$target/.governance/governance_check.py" \
    --root "$target" --manifest .governance/manifest.json \
    --stack-profiles .governance/stack-profiles.json "$@"
}

expect_code() {
  local expected="$1"
  shift
  set +e
  output="$($@ 2>&1)"
  status=$?
  set -e
  test "$status" -eq 1
  grep -q "$expected" <<<"$output"
}

write_evidence() {
  local path="$1"
  local source="$2"
  local actor_login="$3"
  local actor_type="$4"
  local method="$5"
  local repository="${6:-example/fixture}"
  local pull_request="${7:-13}"
  local head_sha="${8:-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa}"
  local ticket="${9:-ticket-002}"
  local verified="${10:-true}"
  python3 - "$path" "$source" "$actor_login" "$actor_type" "$method" \
    "$repository" "$pull_request" "$head_sha" "$ticket" "$verified" <<'PY'
import json
import pathlib
import sys

verification = {'method': sys.argv[5], 'verified': sys.argv[10] == 'true'}
if sys.argv[2] == 'signed-attestation':
    verification.update({
        'issuer': 'https://token.actions.githubusercontent.com',
        'predicateType': 'https://wellmanifest.dev/attestations/validator/v1',
    })
payload = {
    'schema': 'new-project.approval-evidence/v1',
    'source': sys.argv[2],
    'repository': sys.argv[6],
    'pullRequest': int(sys.argv[7]),
    'headSha': sys.argv[8],
    'ticket': sys.argv[9],
    'actor': {'login': sys.argv[3], 'type': sys.argv[4]},
    'verification': verification,
}
pathlib.Path(sys.argv[1]).write_text(json.dumps(payload), encoding='utf-8')
PY
}

allowed="$fixture/allowed"
make_fixture "$allowed"
python3 - "$allowed" <<'PY'
import hashlib
import json
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
lock = {
  'schema': 'new-project.lock/v1',
  'standard': {
    'id': 'wellmanifest/new-project',
    'version': '0.9.0',
    'sourceRepository': 'wellmanifest/new-project',
    'sourceRevision': 'a' * 40,
    'publicationStatus': 'published',
  },
  'managedFiles': {
    'README.md': hashlib.sha256((root / 'README.md').read_bytes()).hexdigest(),
  },
}
(root / '.governance/manifest.lock.json').write_text(json.dumps(lock), encoding='utf-8')
PY
run_check "$allowed" --changed-file src/app.js --enforce-approval \
  --approval-source github-review --approved-ticket ticket-002 > "$fixture/pass.out"
grep -q '^GOV-PASS:' "$fixture/pass.out"
resolved_ticket="$fixture/resolved-ticket.txt"
run_check "$allowed" --changed-file src/app.js --resolved-ticket-output "$resolved_ticket" \
  > "$fixture/resolved-ticket.out"
grep -qx 'ticket-002' "$resolved_ticket"
expect_code GOV-PATH-001 run_check "$allowed" --changed-file src/app.js \
  --resolved-ticket-output "$allowed/.governance/resolved-ticket.txt"
run_check "$allowed" --changed-file src/app.js --lock .governance/manifest.lock.json > "$fixture/published-lock.out"
grep -q '^GOV-PASS:' "$fixture/published-lock.out"
sed -i 's/"published"/"uncommitted"/' "$allowed/.governance/manifest.lock.json"
expect_code GOV-SYNC-001 run_check "$allowed" --changed-file src/app.js --lock .governance/manifest.lock.json
dot_path="$fixture/dot-path"
make_fixture "$dot_path"
sed -i 's/"workstream": "application"/"workstream": "governance"/' "$dot_path/project/ticket-002/intent.json"
sed -i 's#"allowedPaths": \["src/\*\*"\]#"allowedPaths": [".governance/**"]#' "$dot_path/project/ticket-002/intent.json"
run_check "$dot_path" --changed-file .governance/manifest.json > "$fixture/dot-path.out"
grep -q '^GOV-PASS:' "$fixture/dot-path.out"

expect_code GOV-APPROVAL-001 run_check "$allowed" --changed-file src/app.js \
  --enforce-approval --approved-ticket ticket-002
expect_code GOV-APPROVAL-002 run_check "$allowed" --changed-file src/app.js \
  --enforce-approval --approval-source github-review --approved-ticket ticket-999
expect_code GOV-APPROVAL-003 run_check "$allowed" --changed-file src/app.js \
  --enforce-approval --approval-source github-app-review --approved-ticket ticket-002

app_evidence="$fixture/app-evidence.json"
write_evidence "$app_evidence" github-app-review 'validator-agent[bot]' Bot github-api-allowlist
run_check "$allowed" --changed-file src/app.js --enforce-approval \
  --approval-evidence "$app_evidence" --expected-repository example/fixture \
  --expected-pull-request 13 --expected-head aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa \
  > "$fixture/app-approval.out"
grep -q '^GOV-PASS:' "$fixture/app-approval.out"

inside_evidence="$allowed/.governance/approval-evidence.json"
write_evidence "$inside_evidence" github-app-review 'validator-agent[bot]' Bot github-api-allowlist
expect_code GOV-APPROVAL-003 run_check "$allowed" --changed-file src/app.js --enforce-approval \
  --approval-evidence "$inside_evidence" --expected-repository example/fixture \
  --expected-pull-request 13 --expected-head aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa

stale_evidence="$fixture/stale-evidence.json"
write_evidence "$stale_evidence" github-app-review 'validator-agent[bot]' Bot github-api-allowlist \
  example/fixture 13 bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
expect_code GOV-APPROVAL-004 run_check "$allowed" --changed-file src/app.js --enforce-approval \
  --approval-evidence "$stale_evidence" --expected-repository example/fixture \
  --expected-pull-request 13 --expected-head aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa

wrong_target_evidence="$fixture/wrong-target-evidence.json"
write_evidence "$wrong_target_evidence" github-app-review 'validator-agent[bot]' Bot \
  github-api-allowlist other/repository 99
expect_code GOV-APPROVAL-004 run_check "$allowed" --changed-file src/app.js --enforce-approval \
  --approval-evidence "$wrong_target_evidence" --expected-repository example/fixture \
  --expected-pull-request 13 --expected-head aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa

arbitrary_bot="$fixture/arbitrary-bot.json"
write_evidence "$arbitrary_bot" github-app-review arbitrary-bot Bot github-api-allowlist
expect_code GOV-APPROVAL-005 run_check "$allowed" --changed-file src/app.js --enforce-approval \
  --approval-evidence "$arbitrary_bot" --expected-repository example/fixture \
  --expected-pull-request 13 --expected-head aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa

wrong_type="$fixture/wrong-type.json"
write_evidence "$wrong_type" github-app-review 'validator-agent[bot]' User github-api-allowlist
expect_code GOV-APPROVAL-005 run_check "$allowed" --changed-file src/app.js --enforce-approval \
  --approval-evidence "$wrong_type" --expected-repository example/fixture \
  --expected-pull-request 13 --expected-head aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa

signed_evidence="$fixture/signed-evidence.json"
write_evidence "$signed_evidence" signed-attestation validator-workflow Workflow sigstore
run_check "$allowed" --changed-file src/app.js --enforce-approval \
  --approval-evidence "$signed_evidence" --expected-repository example/fixture \
  --expected-pull-request 13 --expected-head aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa \
  > "$fixture/signed-approval.out"
grep -q '^GOV-PASS:' "$fixture/signed-approval.out"

unverified_evidence="$fixture/unverified-evidence.json"
write_evidence "$unverified_evidence" signed-attestation validator-workflow Workflow sigstore \
  example/fixture 13 aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa ticket-002 false
expect_code GOV-APPROVAL-003 run_check "$allowed" --changed-file src/app.js --enforce-approval \
  --approval-evidence "$unverified_evidence" --expected-repository example/fixture \
  --expected-pull-request 13 --expected-head aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
expect_code GOV-SCOPE-001 run_check "$allowed" --changed-file docs/outside.md

single_segment_glob="$fixture/single-segment-glob"
make_fixture "$single_segment_glob"
sed -i 's#"allowedPaths": \["src/\*\*"\]#"allowedPaths": ["src/*"]#' "$single_segment_glob/project/ticket-002/intent.json"
expect_code GOV-SCOPE-001 run_check "$single_segment_glob" --changed-file src/nested/app.js

expect_code GOV-DIFF-001 run_check "$allowed" --base definitely-not-a-commit
expect_code GOV-SYNC-001 run_check "$allowed" --changed-file TODO.md --lock ../outside.lock

invalid_manifest="$fixture/invalid-manifest"
make_fixture "$invalid_manifest"
sed -i 's/"requiredFiles": \[/"requiredFiles": "not-an-array", "ignored": [/' "$invalid_manifest/.governance/manifest.json"
expect_code GOV-MANIFEST-001 run_check "$invalid_manifest" --changed-file TODO.md

invalid_intent_path="$fixture/invalid-intent-path"
make_fixture "$invalid_intent_path"
sed -i 's#"allowedPaths": \["src/\*\*"\]#"allowedPaths": ["../outside/**"]#' "$invalid_intent_path/project/ticket-002/intent.json"
expect_code GOV-INTENT-002 run_check "$invalid_intent_path" --changed-file TODO.md

unknown_status="$fixture/unknown-status"
make_fixture "$unknown_status"
sed -i 's/Status\*\*: IN_PROGRESS/Status**: BACKLGO/' "$unknown_status/project/ticket-002/README.md"
expect_code GOV-STATUS-001 run_check "$unknown_status" --changed-file TODO.md

plan="$fixture/plan"
make_fixture "$plan"
sed -i 's/Workflow state\*\*: EDIT/Workflow state**: WAIT_FOR_APPROVAL/' "$plan/project/ticket-002/README.md"
expect_code GOV-INTENT-001 run_check "$plan" --changed-file src/app.js

owner="$fixture/owner"
make_fixture "$owner"
touch "$owner/project/ticket-002/user-alice.md"
expect_code GOV-OWNER-001 run_check "$owner" --changed-file project/ticket-002/user-alice.md --actor agent

executable="$fixture/executable"
make_fixture "$executable"
touch "$executable/project/ticket-002/research.py"
expect_code GOV-TICKET-004 run_check "$executable" --changed-file project/ticket-002/research.py

missing="$fixture/missing"
make_fixture "$missing"
sed -i 's/Status\*\*: IN_PROGRESS/Status**: DONE/' "$missing/project/ticket-002/README.md"
expect_code GOV-TICKET-001 run_check "$missing" --changed-file src/app.js

parallel="$fixture/parallel"
make_fixture "$parallel"
mkdir -p "$parallel/sdk"
printf '%s\n' 'export const client = true;' > "$parallel/sdk/client.js"
add_active_ticket "$parallel" ticket-003 interfaces '["sdk/**"]'
run_check "$parallel" --changed-file src/app.js > "$fixture/parallel.out"
grep -q '^GOV-PASS:' "$fixture/parallel.out"
parallel_resolved="$fixture/parallel-resolved.txt"
run_check "$parallel" --changed-file src/app.js --resolved-ticket-output "$parallel_resolved" \
  > "$fixture/parallel-resolved.out"
grep -qx 'ticket-002' "$parallel_resolved"

backlog_release="$fixture/backlog-release"
make_fixture "$backlog_release"
sed -i 's/Status\*\*: IN_PROGRESS/Status**: BACKLOG/' "$backlog_release/project/ticket-002/README.md"
add_active_ticket "$backlog_release" ticket-003 application '["src/**"]'
run_check "$backlog_release" --changed-file src/app.js > "$fixture/backlog-release.out"
grep -q '^GOV-PASS:' "$fixture/backlog-release.out"

blocked_release="$fixture/blocked-release"
make_fixture "$blocked_release"
sed -i 's/Status\*\*: IN_PROGRESS/Status**: BLOCKED/' "$blocked_release/project/ticket-002/README.md"
add_active_ticket "$blocked_release" ticket-003 application '["src/**"]'
run_check "$blocked_release" --changed-file src/app.js > "$fixture/blocked-release.out"
grep -q '^GOV-PASS:' "$fixture/blocked-release.out"

same_workstream="$fixture/same-workstream"
make_fixture "$same_workstream"
mkdir -p "$same_workstream/sdk"
printf '%s\n' 'export const client = true;' > "$same_workstream/sdk/client.js"
add_active_ticket "$same_workstream" ticket-003 application '["sdk/**"]'
expect_code GOV-WORKSTREAM-002 run_check "$same_workstream" --changed-file TODO.md

overlap="$fixture/overlap"
make_fixture "$overlap"
printf '%s\n' 'export const shared = true;' > "$overlap/src/shared.js"
add_active_ticket "$overlap" ticket-003 interfaces '["src/shared.*"]'
expect_code GOV-WORKSTREAM-004 run_check "$overlap" --changed-file TODO.md
expect_code GOV-TICKET-005 run_check "$overlap" --changed-file src/shared.js

planned_overlap="$fixture/planned-overlap"
make_fixture "$planned_overlap"
sed -i 's#"allowedPaths": \["src/\*\*"\]#"allowedPaths": ["future/**"]#' "$planned_overlap/project/ticket-002/intent.json"
sed -i 's/"workstream": "application"/"workstream": "integration"/' "$planned_overlap/project/ticket-002/intent.json"
add_active_ticket "$planned_overlap" ticket-003 interfaces '["future/*.js"]'
expect_code GOV-WORKSTREAM-004 run_check "$planned_overlap" --changed-file TODO.md

planned_unowned="$fixture/planned-unowned"
make_fixture "$planned_unowned"
sed -i 's#"allowedPaths": \["src/\*\*"\]#"allowedPaths": ["sdk/**"]#' "$planned_unowned/project/ticket-002/intent.json"
expect_code GOV-WORKSTREAM-003 run_check "$planned_unowned" --changed-file TODO.md

dependency_cycle="$fixture/dependency-cycle"
make_fixture "$dependency_cycle"
sed -i 's/"dependsOn": \[\]/"dependsOn": ["ticket-003"]/' "$dependency_cycle/project/ticket-002/intent.json"
add_active_ticket "$dependency_cycle" ticket-003 interfaces '["sdk/**"]' '["ticket-002"]'
expect_code GOV-DEPENDENCY-001 run_check "$dependency_cycle" --changed-file TODO.md

dependency_missing="$fixture/dependency-missing"
make_fixture "$dependency_missing"
sed -i 's/"dependsOn": \[\]/"dependsOn": ["ticket-999"]/' "$dependency_missing/project/ticket-002/intent.json"
expect_code GOV-DEPENDENCY-002 run_check "$dependency_missing" --changed-file TODO.md

conflict="$fixture/conflict"
make_fixture "$conflict"
sed -i 's/"conflictsWith": \[\]/"conflictsWith": ["ticket-003"]/' "$conflict/project/ticket-002/intent.json"
add_active_ticket "$conflict" ticket-003 interfaces '["sdk/**"]'
expect_code GOV-CONFLICT-001 run_check "$conflict" --changed-file TODO.md

integration="$fixture/integration"
make_fixture "$integration"
sed -i 's#"allowedPaths": \["src/\*\*"\]#"allowedPaths": ["src/**", "package.json"]#' "$integration/project/ticket-002/intent.json"
expect_code GOV-INTEGRATION-001 run_check "$integration" --changed-file package.json

invalid_integration_ref="$fixture/invalid-integration-ref"
make_fixture "$invalid_integration_ref"
sed -i 's/"integrationTicket": null/"integrationTicket": "ticket-999"/' "$invalid_integration_ref/project/ticket-002/intent.json"
expect_code GOV-INTEGRATION-001 run_check "$invalid_integration_ref" --changed-file TODO.md

direct_shared_change="$fixture/direct-shared-change"
make_fixture "$direct_shared_change"
sed -i 's#"allowedPaths": \["src/\*\*"\]#"allowedPaths": ["src/**", "package.json"]#' "$direct_shared_change/project/ticket-002/intent.json"
sed -i 's/"integrationTicket": null/"integrationTicket": "ticket-003"/' "$direct_shared_change/project/ticket-002/intent.json"
add_active_ticket "$direct_shared_change" ticket-003 integration '["package.json"]'
sed -i 's/Status\*\*: IN_PROGRESS/Status**: DONE/' "$direct_shared_change/project/ticket-003/README.md"
sed -i 's/Workflow state\*\*: EDIT/Workflow state**: DONE/' "$direct_shared_change/project/ticket-003/README.md"
expect_code GOV-INTEGRATION-001 run_check "$direct_shared_change" --changed-file package.json

integration_owned="$fixture/integration-owned"
make_fixture "$integration_owned"
add_active_ticket "$integration_owned" ticket-003 integration '["package.json"]'
run_check "$integration_owned" --changed-file package.json > "$fixture/integration-owned.out"
grep -q '^GOV-PASS:' "$fixture/integration-owned.out"

run_check "$allowed" --changed-file src/app.js --format json > "$fixture/report.json"
run_check "$allowed" --changed-file src/app.js --format sarif > "$fixture/report.sarif"
python3 - "$fixture/report.json" "$fixture/report.sarif" <<'PY'
import json
import sys
report = json.load(open(sys.argv[1], encoding='utf-8'))
sarif = json.load(open(sys.argv[2], encoding='utf-8'))
assert report['schema'] == 'new-project.governance-report/v1'
assert report['status'] == 'passed'
assert sarif['version'] == '2.1.0'
PY

history_good="$fixture/history-good"
make_fixture "$history_good"
(
  cd "$history_good"
  git init -q
  git config user.email governance@example.invalid
  git config user.name governance-fixture
  git add .
  git commit -qm 'plan exists'
  base="$(git rev-parse HEAD)"
  printf '%s\n' 'export const ok = 2;' > src/app.js
  git add src/app.js
  git commit -qm 'implementation after plan'
  run_check "$history_good" --base "$base" > "$fixture/history-good.out"
)
grep -q '^GOV-PASS:' "$fixture/history-good.out"

history_bad="$fixture/history-bad"
make_fixture "$history_bad"
cp -R "$history_bad/project/ticket-002" "$fixture/ticket-002.saved"
rm -rf "$history_bad/project/ticket-002"
rm -f "$history_bad/src/app.js"
(
  cd "$history_bad"
  git init -q
  git config user.email governance@example.invalid
  git config user.name governance-fixture
  git add .
  git commit -qm 'baseline without ticket'
  base="$(git rev-parse HEAD)"
  cp -R "$fixture/ticket-002.saved" project/ticket-002
  printf '%s\n' 'export const late = true;' > src/app.js
  git add .
  git commit -qm 'ticket and implementation together'
  expect_code GOV-INTENT-003 run_check "$history_bad" --base "$base"
)

echo 'governance validator: PASS'
