#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
fixture="$(mktemp -d "${TMPDIR:-/tmp}/new-project-validator-test.XXXXXX")"
cleanup() {
  rm -rf "$fixture"
}
trap cleanup EXIT INT TERM

python3 - "$repo_root" <<'PY'
import json
import pathlib
import sys

from jsonschema import Draft202012Validator

root = pathlib.Path(sys.argv[1])
policy = (root / 'POLICY.md').read_text(encoding='utf-8')
agents = (root / 'AGENTS.md').read_text(encoding='utf-8')
agent_template = (root / 'template/files/AGENTS.template.md').read_text(encoding='utf-8')
enforcement = (root / 'docs/GOVERNANCE_ENFORCEMENT.md').read_text(encoding='utf-8')
for rule in ('P-BRANCH-001', 'P-BRANCH-002', 'P-BRANCH-003'):
    assert f'RULE {rule} TYPE REQUIRED' in policy
assert 'delete_branch_on_merge = true' in policy
assert 'AUTOMATIC_DELETE_UNMERGED_HEAD_BRANCH' in policy
assert 'REMOTE_BRANCHES = [DEFAULT_BRANCH]' in policy
for instructions in (agents, agent_template):
    assert 'delete_branch_on_merge=true' in instructions
    assert 'closed without merge' in instructions.lower()
assert 'open pull requests = 0' in enforcement
assert 'remote branches = [default branch]' in enforcement
assert 'Sam walidator jest read-only i nie usuwa branchy.' in enforcement
schemas = {
    name: json.load(open(root / 'governance' / name, encoding='utf-8'))
    for name in (
        'approval-evidence.schema.json',
        'diagnostics.schema.json',
        'intent.schema.json',
        'lock.schema.json',
        'manifest.schema.json',
        'work-classification.schema.json',
    )
}
for schema in schemas.values():
    Draft202012Validator.check_schema(schema)

Draft202012Validator(schemas['diagnostics.schema.json']).validate(
    json.load(open(root / 'governance/diagnostics.json', encoding='utf-8'))
)

Draft202012Validator(schemas['manifest.schema.json']).validate(
    json.load(open(root / 'governance/manifest.default.json', encoding='utf-8'))
)
hub_manifest = json.load(open(
    root / 'governance/manifest.hub.json', encoding='utf-8'
))
Draft202012Validator(schemas['manifest.schema.json']).validate(hub_manifest)
assert hub_manifest['standard']['version'] == '0.17.0'
assert hub_manifest['coordination']['workstreams'] == {
    'governance': {'ownedPaths': ['**']},
}
assert hub_manifest['coordination']['integration'] == {
    'workstream': 'governance',
    'requiredForPaths': [],
}
assert hub_manifest['delivery']['maxImplementationFiles'] == 9

goal = json.load(open(root / 'goal.yaml', encoding='utf-8'))
assert goal['project'] == {
    'name': 'new-project',
    'type': 'generic',
    'description': 'Governance and onboarding standard source hub',
}
assert goal['versioning']['files'] == ['VERSION']
assert goal['git']['commit']['scope'] == 'new-project'
assert goal['git']['commit']['require_ticket'] is True
assert goal['publishing']['enabled'] is False
assert goal['publishing']['registries'] == []
assert goal['publishing']['fallback']['github_release'] == {
    'enabled': True,
    'owner': 'wellmanifest',
    'repo': 'new-project',
    'token_env': 'GITHUB_TOKEN',
    'create_on_tag': True,
    'asset_glob': 'dist/*',
}
assert 'strategies' not in goal
assert 'registries' not in goal
assert goal['governance']['delivery'] == {
    'require_goal_a': True,
    'default_mode': 'pull-request',
    'allowed_modes': ['pull-request', 'direct-main'],
    'remote': 'origin',
    'base_branch': 'main',
    'require_clean_governance': True,
}
intent_validator = Draft202012Validator(schemas['intent.schema.json'])
for intent_path in sorted((root / 'project').glob('ticket-*/intent.json')):
    intent_validator.validate(json.load(open(intent_path, encoding='utf-8')))
adoption_intent = json.load(open(
    root / 'project/ticket-038/intent.json', encoding='utf-8'
))
adoption_intent['delivery']['standardAdoption'] = {
    'sourceRepository': 'wellmanifest/new-project',
    'fromRevision': 'a' * 40,
    'toRevision': 'b' * 40,
}
intent_validator.validate(adoption_intent)
bootstrap_intent = json.loads(json.dumps(adoption_intent))
bootstrap_intent['delivery']['standardAdoption']['fromRevision'] = None
intent_validator.validate(bootstrap_intent)
for field, invalid in (
    ('sourceRepository', 'other/project'),
    ('fromRevision', 'main'),
    ('toRevision', 'v0.13.2'),
):
    candidate = json.loads(json.dumps(adoption_intent))
    candidate['delivery']['standardAdoption'][field] = invalid
    assert not intent_validator.is_valid(candidate), (field, invalid)
Draft202012Validator(schemas['lock.schema.json']).validate({
    'schema': 'new-project.lock/v1',
    'standard': {
        'id': 'wellmanifest/new-project',
        'version': '0.17.0',
        'sourceRepository': 'wellmanifest/new-project',
        'sourceRevision': '0' * 40,
        'publicationStatus': 'published',
    },
    'managedFiles': {'AGENTS.md': '0' * 64},
})
candidate_lock = {
    'schema': 'new-project.lock/v1',
    'standard': {
        'id': 'wellmanifest/new-project',
        'version': '0.17.0',
        'sourceRepository': 'wellmanifest/new-project',
        'sourceRevision': '0' * 40,
        'publicationStatus': 'unpublished-test',
    },
    'managedFiles': {'AGENTS.md': '0' * 64},
}
Draft202012Validator(schemas['lock.schema.json']).validate(candidate_lock)
Draft202012Validator(schemas['approval-evidence.schema.json']).validate({
    'schema': 'new-project.approval-evidence/v1',
    'source': 'github-app-review',
    'repository': 'wellmanifest/new-project',
    'pullRequest': 1,
    'headSha': '0' * 40,
    'ticket': 'ticket-010',
    'actor': {'login': 'validator[bot]', 'type': 'Bot'},
    'verification': {'method': 'github-api-allowlist', 'verified': True},
})

classification = json.load(open(
    root / 'governance/work-classification.dsl.json', encoding='utf-8'
))
classification_validator = Draft202012Validator(
    schemas['work-classification.schema.json']
)
classification_validator.validate(classification)
assert classification['dimensions'] == {
    'kind': ['BUG', 'FEATURE', 'SERVICE'],
    'priority': ['P0', 'P1', 'P2', 'P3'],
    'origin': ['regression', 'requested', 'health'],
}
assert classification['ordering']['precedence'] == [
    'dependencies', 'kind', 'priority', 'stableId',
]
assert classification['priorityDerivation']['impact'] == {
    'critical': 'P0', 'high': 'P1', 'medium': 'P2', 'low': 'P3',
}
assert classification['priorityDerivation']['serviceDefault'] == 'P2'
rules = {rule['id']: rule for rule in classification['rules']}
assert len(rules) == len(classification['rules'])
assert rules['W-CLASS-002']['assign'] == {
    'kind': 'BUG', 'origin': 'regression',
}
assert rules['W-CLASS-003']['when']['threshold'] == 'crossed'
assert rules['W-CLASS-004']['assign'] == {
    'kind': 'SERVICE', 'origin': 'health',
}

def rejected(mutator):
    candidate = json.loads(json.dumps(classification))
    mutator(candidate)
    assert not classification_validator.is_valid(candidate)

rejected(lambda value: value['dimensions']['kind'].__setitem__(0, 'UNKNOWN'))
rejected(lambda value: value['dimensions']['priority'].__setitem__(0, 'PX'))
rejected(lambda value: value['ordering']['kindOrder'].__setitem__(1, 'BUG'))
rejected(lambda value: value['priorityDerivation']['impact'].__setitem__('high', 'P3'))
rejected(lambda value: value['rules'][1]['when'].pop('baseline'))
rejected(lambda value: value['rules'][1].pop('assign'))

package = json.load(open(root / 'governance/package-manifest.json', encoding='utf-8'))
assert package['schema'] == 'new-project.package-manifest/v1'
assert package['files']
assert len({item['target'] for item in package['files']}) == len(package['files'])
assert 'governance/package-manifest.json' in {item['source'] for item in package['files']}
assert 'governance/manifest.hub.json' not in {item['source'] for item in package['files']}
assert {
    'error/README.md',
    'governance/diagnostics.schema.json',
    'governance/work-classification.dsl.json',
    'governance/work-classification.schema.json',
} <= {item['source'] for item in package['files']}
for item in package['files']:
    assert (root / item['source']).is_file(), item['source']
extendable = [item for item in package['files'] if item['strategy'] == 'extendable']
assert extendable == [{
    'source': 'governance/manifest.default.json',
    'target': '.governance/manifest.json',
    'strategy': 'extendable',
    'executable': False,
}]
assert any(
    item['target'] == '.governance/manifest.base.json'
    and item['strategy'] == 'managed'
    for item in package['files']
)
PY

python3 - "$repo_root/governance/manifest.schema.json" "$repo_root/governance/manifest.default.json" \
  "$repo_root/governance/approval-evidence.schema.json" \
  "$repo_root/governance/stack-profiles.json" <<'PY'
import json
import sys

schema = json.load(open(sys.argv[1], encoding='utf-8'))
manifest = json.load(open(sys.argv[2], encoding='utf-8'))
approval_schema = json.load(open(sys.argv[3], encoding='utf-8'))
stack_profiles = json.load(open(sys.argv[4], encoding='utf-8'))
assert schema['additionalProperties'] is False
assert set(manifest) <= set(schema['properties'])
assert set(schema['required']) <= set(manifest)
assert manifest['schema'] == schema['properties']['schema']['const']
assert manifest['standard']['version'] == '0.17.0'
ticket = manifest['ticket']
assert ticket['activeStatuses'] == ['IN_PROGRESS']
assert ticket['nonActiveStatuses'] == ['BACKLOG', 'PLAN', 'BLOCKED']
assert not set(ticket['activeStatuses']) & set(ticket['nonActiveStatuses'])
assert manifest['delivery']['maxActiveMinutes'] == 30
assert manifest['delivery']['checkpointMinutes'] == 25
assert manifest['repository'] == {
    'mode': 'standalone',
    'componentRoots': [],
}
assert manifest['delivery']['allowedComplexityClasses'] == ['XS', 'S', 'M', 'L']
assert manifest['delivery']['maxImplementationFiles'] == 15
assert manifest['delivery']['profiles'] == {
    'XS': {
        'maxImplementationFiles': 2,
        'maxAffectedComponents': 1,
        'maxPublicInterfaceChanges': 0,
        'maxRuntimeDependencies': 0,
    },
    'S': {
        'maxImplementationFiles': 5,
        'maxAffectedComponents': 2,
        'maxPublicInterfaceChanges': 1,
        'maxRuntimeDependencies': 1,
    },
    'M': {
        'maxImplementationFiles': 9,
        'maxAffectedComponents': 3,
        'maxPublicInterfaceChanges': 2,
        'maxRuntimeDependencies': 2,
    },
    'L': {
        'maxImplementationFiles': 15,
        'maxAffectedComponents': 5,
        'maxPublicInterfaceChanges': 3,
        'maxRuntimeDependencies': 3,
    },
}
assert 'Dockerfile' not in manifest['requiredFiles']
assert manifest['docker']['required'] is False
assert manifest['stacks'] == []
assert {'compose.yaml', 'docker-compose.yaml'} <= set(manifest['docker']['composeFiles'])
assert {
    'Dockerfile',
    'Dockerfile.e2e',
    'compose.yml',
    'compose.yaml',
    'docker-compose.yml',
    'docker-compose.yaml',
} <= set(stack_profiles['profiles']['docker']['anyFiles'])
assert 'github-app-review' in manifest['trustedApprovalSources']
assert manifest['approvalEvidence']['schema'] == 'new-project.approval-evidence/v1'
assert approval_schema['properties']['headSha']['pattern'] == '^[0-9a-f]{40}$'
governance_paths = manifest['coordination']['workstreams']['governance']['ownedPaths']
integration_paths = manifest['coordination']['workstreams']['integration']['ownedPaths']
assert 'CHANGELOG.md' in governance_paths
assert '.env.example' in governance_paths
assert 'VERSION' in integration_paths
assert 'VERSION' not in governance_paths
assert 'VERSION' not in manifest['coordination']['workstreams']['application']['ownedPaths']
assert {
    'goal.yaml',
    'project.sh',
    'project.bat',
    'scripts/runtime.sh',
} <= set(governance_paths)
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
assert module.pattern_covered_by('test/cli*.test.ts', 'test/cli*')
assert module.pattern_covered_by('test/cli-smoke.test.ts', 'test/cli*')
assert not module.pattern_covered_by('test/mcp*.test.ts', 'test/cli*')
assert not module.pattern_covered_by('test/cli*.test.ts', 'test/*.spec.ts')
assert module.standard_adoption_error({
    'sourceRepository': 'wellmanifest/new-project',
    'fromRevision': 'a' * 40,
    'toRevision': 'b' * 40,
}) is None
assert module.standard_adoption_error({
    'sourceRepository': 'wellmanifest/new-project',
    'fromRevision': None,
    'toRevision': 'b' * 40,
}) is None
assert module.standard_adoption_error({
    'sourceRepository': 'wellmanifest/new-project',
    'fromRevision': 'a' * 40,
    'toRevision': 'a' * 40,
}) == 'delivery standardAdoption revisions must differ'
PY
python3 "$repo_root/scripts/audit_diagnostics.py" --root "$repo_root"
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
grep -Fq -- '--manifest governance/manifest.hub.json' "$repo_root/.github/workflows/ci.yml"
grep -Fq -- '--work-classification governance/work-classification.dsl.json' "$repo_root/.github/workflows/ci.yml"
grep -Fq -- '--base "$BASE_SHA"' "$repo_root/.github/workflows/ci.yml"
grep -Fq -- '--head "$HEAD_SHA"' "$repo_root/.github/workflows/ci.yml"
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
  python3 - "$target/.governance/manifest.json" <<'PY'
import json
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
manifest = json.loads(path.read_text(encoding='utf-8'))
manifest['docker']['required'] = True
path.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
PY
  cp "$repo_root/governance/stack-profiles.json" "$target/.governance/stack-profiles.json"
  cp "$repo_root/governance/work-classification.dsl.json" "$target/.governance/work-classification.dsl.json"
  touch "$target/README.md" "$target/CHANGELOG.md" "$target/TODO.md" "$target/AGENTS.md"
  printf '%s\n' 'FROM scratch' > "$target/Dockerfile"
  touch "$target/compose.yml" "$target/project/TICKETS.md"
  touch "$target/project/new-ticket.sh" "$target/project/readme.sh"
  printf '%s\n' '0.1.0' > "$target/VERSION"
  printf '%s\n' '# Ticket 001' '- **Status**: DONE' '- **Workflow state**: DONE' > "$target/project/ticket-001/README.md"
  printf '%s\n' '# Ticket 002' '- **Status**: IN_PROGRESS' '- **Workflow state**: EDIT' > "$target/project/ticket-002/README.md"
  touch "$target/project/ticket-002/preprompt.md" "$target/project/ticket-002/changelog.md"
  touch "$target/project/ticket-002/ai-codex.md" "$target/project/ticket-002/ai-codex-logs.txt"
  cat > "$target/project/ticket-002/intent.json" <<'JSON'
{
  "schema": "new-project.intent/v3",
  "ticket": "ticket-002",
  "summary": "Fixture implementation",
  "workstream": "application",
  "allowedPaths": ["src/**"],
  "forbiddenPaths": ["project/ticket-*/user-*.md"],
  "stacks": ["node", "docker"],
  "dependsOn": [],
  "conflictsWith": [],
  "integrationTicket": null,
  "classification": {"kind": "FEATURE", "priority": "P2", "origin": "requested"},
  "delivery": {
    "acceptedBaseSha": "0000000000000000000000000000000000000000",
    "targetBranch": "main",
    "outcome": "Validate one bounded fixture change",
    "nonGoals": ["No public API or dependency changes"],
    "complexity": "XS",
    "estimatedMinutes": 10,
    "budgets": {
      "maxImplementationFiles": 1,
      "maxAffectedComponents": 1,
      "maxPublicInterfaceChanges": 0,
      "maxRuntimeDependencies": 0
    },
    "architecture": {
      "status": "accepted",
      "decision": "Keep the fixture change inside the application component",
      "components": [{"name": "application", "paths": ["src/**"]}],
      "responsibilityChanges": false,
      "interfaceChanges": [],
      "dataChanges": [],
      "ui": {"impact": "none", "states": [], "evidence": []},
      "rollback": "Revert the fixture file"
    },
    "runtimeDependencies": [],
    "validation": [{
      "criterion": "AC-01",
      "commands": ["governance-check"],
      "evidence": "The fixture gate passes"
    }]
  }
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
  "schema": "new-project.intent/v3",
  "ticket": "$ticket",
  "summary": "Parallel fixture",
  "workstream": "$workstream",
  "allowedPaths": $allowed_paths,
  "forbiddenPaths": ["project/ticket-*/user-*.md"],
  "stacks": ["node", "docker"],
  "dependsOn": $depends_on,
  "conflictsWith": $conflicts_with,
  "integrationTicket": null,
  "classification": {"kind": "SERVICE", "priority": "P2", "origin": "health"},
  "delivery": {
    "acceptedBaseSha": "0000000000000000000000000000000000000000",
    "targetBranch": "main",
    "outcome": "Validate one parallel fixture change",
    "nonGoals": ["No cross-workstream contract changes"],
    "complexity": "XS",
    "estimatedMinutes": 10,
    "budgets": {
      "maxImplementationFiles": 1,
      "maxAffectedComponents": 1,
      "maxPublicInterfaceChanges": 0,
      "maxRuntimeDependencies": 0
    },
    "architecture": {
      "status": "accepted",
      "decision": "Keep the change inside its declared workstream component",
      "components": [{"name": "$workstream", "paths": $allowed_paths}],
      "responsibilityChanges": false,
      "interfaceChanges": [],
      "dataChanges": [],
      "ui": {"impact": "none", "states": [], "evidence": []},
      "rollback": "Revert the fixture file"
    },
    "runtimeDependencies": [],
    "validation": [{
      "criterion": "AC-01",
      "commands": ["governance-check"],
      "evidence": "The parallel fixture gate passes"
    }]
  }
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

configure_version_ticket() {
  local target="$1"
  local workstream="$2"
  python3 - "$target/.governance/manifest.json" \
    "$target/project/ticket-002/intent.json" "$workstream" <<'PY'
import json
import pathlib
import sys

manifest_path = pathlib.Path(sys.argv[1])
intent_path = pathlib.Path(sys.argv[2])
workstream = sys.argv[3]
manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
assert manifest['stacks'] == []
intent = json.loads(intent_path.read_text(encoding='utf-8'))
intent['workstream'] = workstream
intent['allowedPaths'] = ['VERSION']
intent['stacks'] = []
intent['delivery']['architecture']['decision'] = (
    'Keep the version carrier inside its declared workstream'
)
intent['delivery']['architecture']['components'] = [{
    'name': 'version-carrier',
    'paths': ['VERSION'],
}]
intent_path.write_text(json.dumps(intent, indent=2) + '\n', encoding='utf-8')
PY
}

expect_code() {
  local expected="$1"
  shift
  local output status
  if output="$("$@" 2>&1)"; then
    status=0
  else
    status=$?
  fi
  test "$status" -eq 1
  grep -q "$expected" <<<"$output"
}

expect_codes() {
  local expected_a="$1"
  local expected_b="$2"
  shift 2
  local output status
  if output="$("$@" 2>&1)"; then
    status=0
  else
    status=$?
  fi
  test "$status" -eq 1
  grep -q "$expected_a" <<<"$output"
  grep -q "$expected_b" <<<"$output"
}

mutate_delivery() {
  local target="$1"
  local action="$2"
  python3 - "$target/project/ticket-002/intent.json" "$action" <<'PY'
import json
import sys

path, action = sys.argv[1:]
with open(path, encoding='utf-8') as handle:
    intent = json.load(handle)
delivery = intent.get('delivery')
if action == 'missing':
    intent.pop('delivery', None)
elif action == 'thirty-minutes':
    delivery['complexity'] = 'S'
    delivery['estimatedMinutes'] = 30
elif action == 'xs-over-time':
    delivery['estimatedMinutes'] = 11
elif action == 'two-files':
    delivery['budgets']['maxImplementationFiles'] = 1
elif action == 'ambiguous-component':
    delivery['architecture']['components'].append({'name': 'duplicate-owner', 'paths': ['src/**']})
elif action == 'over-policy-budget':
    delivery['budgets']['maxImplementationFiles'] = 6
elif action == 's-profile-overflow':
    delivery['complexity'] = 'S'
    delivery['budgets']['maxImplementationFiles'] = 6
elif action == 'm-profile':
    delivery['complexity'] = 'M'
    delivery['estimatedMinutes'] = 30
    delivery['budgets'] = {
        'maxImplementationFiles': 9,
        'maxAffectedComponents': 3,
        'maxPublicInterfaceChanges': 2,
        'maxRuntimeDependencies': 2,
    }
else:
    raise SystemExit(f'unknown mutation: {action}')
with open(path, 'w', encoding='utf-8') as handle:
    json.dump(intent, handle, indent=2)
    handle.write('\n')
PY
}

set_accepted_base() {
  local target="$1"
  local accepted_base="$2"
  python3 - "$target/project/ticket-002/intent.json" "$accepted_base" <<'PY'
import json
import sys

path, accepted_base = sys.argv[1:]
with open(path, encoding='utf-8') as handle:
    intent = json.load(handle)
intent['delivery']['acceptedBaseSha'] = accepted_base
with open(path, 'w', encoding='utf-8') as handle:
    json.dump(intent, handle, indent=2)
    handle.write('\n')
PY
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

configure_hub_ticket() {
  local target="$1"
  local allowed_paths="$2"
  cp "$repo_root/governance/manifest.hub.json" "$target/.governance/manifest.json"
  python3 - "$target/project/ticket-002/intent.json" "$allowed_paths" <<'PY'
import json
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
intent = json.loads(path.read_text(encoding='utf-8'))
allowed = json.loads(sys.argv[2])
intent['workstream'] = 'governance'
intent['allowedPaths'] = allowed
intent['stacks'] = []
intent['delivery']['budgets'] = {
    'maxImplementationFiles': 2,
    'maxAffectedComponents': 1,
    'maxPublicInterfaceChanges': 2,
    'maxRuntimeDependencies': 0,
}
intent['delivery']['architecture']['components'] = [{
    'name': 'source-hub',
    'paths': ['.github/**', 'goal.yaml'],
}]
intent['delivery']['architecture']['responsibilityChanges'] = False
intent['delivery']['architecture']['interfaceChanges'] = [
    'Source-hub PR diff gate',
    'Goal delivery contract',
]
path.write_text(json.dumps(intent, indent=2) + '\n', encoding='utf-8')
PY
  mkdir -p "$target/.github/workflows"
  printf '%s\n' 'name: fixture' > "$target/.github/workflows/ci.yml"
  cp "$repo_root/goal.yaml" "$target/goal.yaml"
}

hub_scope="$fixture/hub-scope"
make_fixture "$hub_scope"
configure_hub_ticket "$hub_scope" '[".github/**", "goal.yaml"]'
run_check "$hub_scope" --changed-file .github/workflows/ci.yml \
  --changed-file goal.yaml > "$fixture/hub-scope.out"
grep -q '^GOV-PASS:' "$fixture/hub-scope.out"

hub_scope_escape="$fixture/hub-scope-escape"
make_fixture "$hub_scope_escape"
configure_hub_ticket "$hub_scope_escape" '[".github/**"]'
expect_code GOV-SCOPE-001 run_check "$hub_scope_escape" --changed-file goal.yaml

docker_optional="$fixture/docker-optional"
make_fixture "$docker_optional"
python3 - "$docker_optional/.governance/manifest.json" <<'PY'
import json
import sys

path = sys.argv[1]
manifest = json.load(open(path, encoding='utf-8'))
manifest['docker']['required'] = False
open(path, 'w', encoding='utf-8').write(json.dumps(manifest, indent=2) + '\n')
PY
rm "$docker_optional/Dockerfile" "$docker_optional/compose.yml"
run_check "$docker_optional" --changed-file src/app.js > "$fixture/docker-optional.out"
grep -q '^GOV-PASS:' "$fixture/docker-optional.out"

docker_references="$fixture/docker-references"
make_fixture "$docker_references"
printf '%s\n' \
  "FROM --platform=linux/amd64 python@sha256:$(printf 'a%.0s' {1..64}) AS runtime" \
  > "$docker_references/Dockerfile"
cat > "$docker_references/compose.yml" <<YAML
services:
  cache:
    image: "redis@sha256:$(printf 'b%.0s' {1..64})"
  local:
    build: .
YAML
if ! run_check "$docker_references" --changed-file src/app.js \
  > "$fixture/docker-references.out"; then
  cat "$fixture/docker-references.out"
  exit 1
fi
grep -q '^GOV-PASS:' "$fixture/docker-references.out"

compose_root="$fixture/compose-root"
cp -R "$docker_references" "$compose_root"
mkdir -p "$compose_root/services/api"
mv "$compose_root/Dockerfile" "$compose_root/services/api/Dockerfile"
mv "$compose_root/compose.yml" "$compose_root/docker-compose.yml"
python3 - "$compose_root/.governance/manifest.json" <<'PY'
import json
import sys

path = sys.argv[1]
manifest = json.load(open(path, encoding='utf-8'))
manifest['docker']['dockerfiles'] = ['services/api/Dockerfile']
manifest['docker']['composeFiles'] = ['docker-compose.yml']
manifest['stacks'] = ['docker']
open(path, 'w', encoding='utf-8').write(json.dumps(manifest, indent=2) + '\n')
PY
run_check "$compose_root" --changed-file src/app.js \
  > "$fixture/compose-root.out"
grep -q '^GOV-PASS:' "$fixture/compose-root.out"

nested_only="$fixture/nested-only"
cp -R "$compose_root" "$nested_only"
mkdir -p "$nested_only/deploy"
mv "$nested_only/docker-compose.yml" "$nested_only/deploy/stack.yml"
python3 - "$nested_only/.governance/manifest.json" <<'PY'
import json
import sys

path = sys.argv[1]
manifest = json.load(open(path, encoding='utf-8'))
manifest['docker']['composeFiles'] = ['deploy/stack.yml']
open(path, 'w', encoding='utf-8').write(json.dumps(manifest, indent=2) + '\n')
PY
expect_code GOV-STACK-001 run_check "$nested_only" --changed-file src/app.js

docker_tag="$fixture/docker-tag"
cp -R "$docker_references" "$docker_tag"
printf '%s\n' 'FROM python:3.12-slim AS runtime' > "$docker_tag/Dockerfile"
expect_code GOV-DOCKER-002 run_check "$docker_tag" --changed-file src/app.js
run_check "$docker_tag" --changed-file src/app.js > "$fixture/docker-tag.out" || true
grep -Fq 'Dockerfile:1' "$fixture/docker-tag.out"

docker_optional_tag="$fixture/docker-optional-tag"
cp -R "$docker_tag" "$docker_optional_tag"
python3 - "$docker_optional_tag/.governance/manifest.json" <<'PY'
import json
import sys

path = sys.argv[1]
manifest = json.load(open(path, encoding='utf-8'))
manifest['docker']['required'] = False
open(path, 'w', encoding='utf-8').write(json.dumps(manifest, indent=2) + '\n')
PY
expect_code GOV-DOCKER-002 run_check "$docker_optional_tag" --changed-file src/app.js

compose_latest="$fixture/compose-latest"
cp -R "$docker_references" "$compose_latest"
cat > "$compose_latest/compose.yml" <<'YAML'
services:
  cache:
    image: redis:latest
YAML
expect_code GOV-DOCKER-002 run_check "$compose_latest" --changed-file src/app.js
run_check "$compose_latest" --changed-file src/app.js > "$fixture/compose-latest.out" || true
grep -Fq 'compose.yml:3' "$fixture/compose-latest.out"

compose_build_tag="$fixture/compose-build-tag"
cp -R "$docker_references" "$compose_build_tag"
cat > "$compose_build_tag/compose.yml" <<'YAML'
services:
  local:
    image: local/code2logic:latest
    build: .
YAML
expect_code GOV-DOCKER-002 run_check "$compose_build_tag" --changed-file src/app.js
run_check "$compose_build_tag" --changed-file src/app.js \
  > "$fixture/compose-build-tag.out" || true
grep -Fq 'compose.yml:3' "$fixture/compose-build-tag.out"
grep -Fq 'for a local-only Compose build, omit image' \
  "$fixture/compose-build-tag.out"

docker_variable="$fixture/docker-variable"
cp -R "$docker_references" "$docker_variable"
printf '%s\n' 'FROM ${BASE_IMAGE} AS runtime' > "$docker_variable/Dockerfile"
expect_code GOV-DOCKER-002 run_check "$docker_variable" --changed-file src/app.js

compose_bad_digest="$fixture/compose-bad-digest"
cp -R "$docker_references" "$compose_bad_digest"
cat > "$compose_bad_digest/compose.yml" <<'YAML'
services:
  cache:
    image: 'redis@sha256:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
YAML
expect_code GOV-DOCKER-002 run_check "$compose_bad_digest" --changed-file src/app.js

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
    'version': '0.17.0',
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
sed -i 's/"published"/"unpublished-test"/' "$allowed/.governance/manifest.lock.json"
expect_code GOV-SYNC-001 run_check "$allowed" --changed-file src/app.js --lock .governance/manifest.lock.json

extendable_sync="$fixture/extendable-sync"
make_fixture "$extendable_sync"
cp "$repo_root/governance/package-manifest.json" \
  "$extendable_sync/.governance/package-manifest.json"
python3 - "$extendable_sync" "$repo_root/scripts/create_adoption_lock.py" <<'PY'
import hashlib
import importlib.util
import json
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
spec = importlib.util.spec_from_file_location('adoption', sys.argv[2])
adoption = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adoption)
manifest_path = root / '.governance/manifest.json'
manifest = json.load(open(manifest_path, encoding='utf-8'))
manifest['coordination']['workstreams']['application']['ownedPaths'] = [
    'src/**', 'app/**', 'lib/**', 'tests/**',
]
manifest['coordination']['workstreams']['sdk'] = {
    'ownedPaths': ['sdk/**', 'test/sdk*', 'test/python-runtime.test.ts'],
}
manifest_path.write_text(
    json.dumps(manifest, indent=2, sort_keys=True) + '\n', encoding='utf-8'
)
base_path = root / '.governance/manifest.base.json'
base_path.write_bytes(adoption.manifest_projection(manifest_path.read_bytes()))
package_path = root / '.governance/package-manifest.json'
lock = {
    'schema': 'new-project.lock/v1',
    'standard': {
        'id': 'wellmanifest/new-project',
        'version': '0.17.0',
        'sourceRepository': 'wellmanifest/new-project',
        'sourceRevision': 'a' * 40,
        'publicationStatus': 'published',
    },
    'managedFiles': {
        '.governance/manifest.base.json': hashlib.sha256(base_path.read_bytes()).hexdigest(),
        '.governance/package-manifest.json': hashlib.sha256(package_path.read_bytes()).hexdigest(),
    },
}
(root / '.governance/manifest.lock.json').write_text(
    json.dumps(lock, indent=2) + '\n', encoding='utf-8'
)
PY
run_check "$extendable_sync" --changed-file src/app.js \
  --lock .governance/manifest.lock.json > "$fixture/extendable-sync.out"
grep -q '^GOV-PASS:' "$fixture/extendable-sync.out"
python3 - "$extendable_sync/.governance/manifest.json" <<'PY'
import json
import sys

path = sys.argv[1]
manifest = json.load(open(path, encoding='utf-8'))
manifest['delivery']['checkpointMinutes'] = 24
open(path, 'w', encoding='utf-8').write(json.dumps(manifest, indent=2) + '\n')
PY
expect_code GOV-SYNC-001 run_check "$extendable_sync" --changed-file src/app.js \
  --lock .governance/manifest.lock.json

dot_path="$fixture/dot-path"
make_fixture "$dot_path"
sed -i 's/"workstream": "application"/"workstream": "governance"/' "$dot_path/project/ticket-002/intent.json"
sed -i 's#"allowedPaths": \["src/\*\*"\]#"allowedPaths": [".governance/**"]#' "$dot_path/project/ticket-002/intent.json"
sed -i 's#"components": \[{"name": "application", "paths": \["src/\*\*"\]}\]#"components": [{"name": "governance", "paths": [".governance/**"]}]#' "$dot_path/project/ticket-002/intent.json"
if ! run_check "$dot_path" --changed-file .governance/manifest.json > "$fixture/dot-path.out"; then
  cat "$fixture/dot-path.out"
  exit 1
fi
grep -q '^GOV-PASS:' "$fixture/dot-path.out"

initial_adoption="$fixture/initial-adoption"
make_fixture "$initial_adoption"
rm -rf "$initial_adoption/.governance" \
  "$initial_adoption/project/ticket-001" \
  "$initial_adoption/project/ticket-002"
printf '%s\n' 'target-owned agents before adoption' > "$initial_adoption/AGENTS.md"
git -C "$initial_adoption" init -q
git -C "$initial_adoption" config user.email governance@example.invalid
git -C "$initial_adoption" config user.name governance-fixture
git -C "$initial_adoption" add .
git -C "$initial_adoption" commit -qm 'initial adoption base'
initial_base="$(git -C "$initial_adoption" rev-parse HEAD)"
git -C "$initial_adoption" switch -qc ticket-002-initial-adoption
mkdir -p "$initial_adoption/.governance" "$initial_adoption/project/ticket-002"
cp "$repo_root/scripts/governance_check.py" "$initial_adoption/.governance/governance_check.py"
cp "$repo_root/governance/manifest.default.json" "$initial_adoption/.governance/manifest.json"
cp "$repo_root/governance/stack-profiles.json" "$initial_adoption/.governance/stack-profiles.json"
cp "$repo_root/governance/work-classification.dsl.json" \
  "$initial_adoption/.governance/work-classification.dsl.json"
printf '%s\n' 'managed agents after adoption' > "$initial_adoption/AGENTS.md"
touch "$initial_adoption/project/ticket-002/preprompt.md" \
  "$initial_adoption/project/ticket-002/changelog.md" \
  "$initial_adoption/project/ticket-002/ai-codex.md" \
  "$initial_adoption/project/ticket-002/ai-codex-logs.txt"
printf '%s\n' '# Ticket 002' '- **Status**: IN_PROGRESS' \
  '- **Workflow state**: EDIT' > "$initial_adoption/project/ticket-002/README.md"
python3 - "$initial_adoption" "$initial_base" <<'PY'
import hashlib
import json
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
base = sys.argv[2]
package = {
    'schema': 'new-project.package-manifest/v1',
    'files': [
        {'source': 'template/files/AGENTS.template.md', 'target': 'AGENTS.md', 'strategy': 'managed', 'executable': False},
        {'source': 'governance/package-manifest.json', 'target': '.governance/package-manifest.json', 'strategy': 'managed', 'executable': False},
        {'source': 'scripts/governance_check.py', 'target': '.governance/governance_check.py', 'strategy': 'managed', 'executable': False},
        {'source': 'governance/stack-profiles.json', 'target': '.governance/stack-profiles.json', 'strategy': 'managed', 'executable': False},
        {'source': 'governance/work-classification.dsl.json', 'target': '.governance/work-classification.dsl.json', 'strategy': 'managed', 'executable': False},
        {'source': 'governance/manifest.default.json', 'target': '.governance/manifest.json', 'strategy': 'seed', 'executable': False},
    ],
}
package_path = root / '.governance/package-manifest.json'
package_path.write_text(json.dumps(package, indent=2) + '\n', encoding='utf-8')
lock = {
    'schema': 'new-project.lock/v1',
    'standard': {
        'id': 'wellmanifest/new-project',
        'version': '0.17.0',
        'sourceRepository': 'wellmanifest/new-project',
        'sourceRevision': 'b' * 40,
        'publicationStatus': 'published',
    },
    'managedFiles': {
        target: hashlib.sha256((root / target).read_bytes()).hexdigest()
        for target in (
            'AGENTS.md',
            '.governance/package-manifest.json',
            '.governance/governance_check.py',
            '.governance/stack-profiles.json',
            '.governance/work-classification.dsl.json',
        )
    },
}
(root / '.governance/manifest.lock.json').write_text(
    json.dumps(lock, indent=2) + '\n', encoding='utf-8'
)
intent = {
    'schema': 'new-project.intent/v3',
    'ticket': 'ticket-002',
    'summary': 'Initial managed adoption fixture',
    'workstream': 'governance',
    'allowedPaths': [
        'AGENTS.md',
        '.governance/manifest.json',
        '.governance/manifest.lock.json',
    ],
    'forbiddenPaths': ['project/ticket-*/user-*.md'],
    'stacks': ['docker'],
    'dependsOn': [],
    'conflictsWith': [],
    'integrationTicket': None,
    'classification': {'kind': 'SERVICE', 'priority': 'P1', 'origin': 'requested'},
    'delivery': {
        'acceptedBaseSha': base,
        'targetBranch': 'main',
        'outcome': 'Install a verified managed package without hiding replaced target content',
        'nonGoals': ['No application change'],
        'complexity': 'S',
        'estimatedMinutes': 10,
        'standardAdoption': {
            'sourceRepository': 'wellmanifest/new-project',
            'fromRevision': None,
            'toRevision': 'b' * 40,
        },
        'budgets': {
            'maxImplementationFiles': 3,
            'maxAffectedComponents': 1,
            'maxPublicInterfaceChanges': 0,
            'maxRuntimeDependencies': 0,
        },
        'architecture': {
            'status': 'accepted',
            'decision': 'Keep the replaced target file in ordinary governance',
            'components': [{
                'name': 'target-adoption',
                'paths': [
                    'AGENTS.md',
                    '.governance/manifest.json',
                    '.governance/manifest.lock.json',
                ],
            }],
            'responsibilityChanges': False,
            'interfaceChanges': [],
            'dataChanges': [],
            'ui': {'impact': 'none', 'states': [], 'evidence': []},
            'rollback': 'Revert the adoption',
        },
        'runtimeDependencies': [],
        'validation': [{
            'criterion': 'AC-01',
            'commands': ['governance-check'],
            'evidence': 'The initial adoption fixture passes',
        }],
    },
}
(root / 'project/ticket-002/intent.json').write_text(
    json.dumps(intent, indent=2) + '\n', encoding='utf-8'
)
PY
git -C "$initial_adoption" add project/ticket-002
git -C "$initial_adoption" commit -qm 'plan initial managed adoption'
git -C "$initial_adoption" add .
git -C "$initial_adoption" commit -qm 'initial managed adoption'
if ! run_check "$initial_adoption" --base "$initial_base" \
  > "$fixture/initial-adoption.out"; then
  cat "$fixture/initial-adoption.out"
  exit 1
fi
grep -q '^GOV-PASS:' "$fixture/initial-adoption.out"
if ! run_check "$initial_adoption" \
  > "$fixture/initial-adoption-inferred-base.out"; then
  cat "$fixture/initial-adoption-inferred-base.out"
  exit 1
fi
grep -q '^GOV-PASS:' "$fixture/initial-adoption-inferred-base.out"

initial_hidden_target="$fixture/initial-adoption-hidden-target"
cp -R "$initial_adoption" "$initial_hidden_target"
python3 - "$initial_hidden_target/project/ticket-002/intent.json" <<'PY'
import json
import sys

path = sys.argv[1]
intent = json.load(open(path, encoding='utf-8'))
intent['allowedPaths'] = ['.governance/**']
intent['delivery']['architecture']['components'][0]['paths'] = ['.governance/**']
open(path, 'w', encoding='utf-8').write(json.dumps(intent, indent=2) + '\n')
PY
git -C "$initial_hidden_target" add project/ticket-002/intent.json
git -C "$initial_hidden_target" commit -qm 'try to hide replaced target content'
expect_code GOV-SCOPE-001 run_check "$initial_hidden_target" --base "$initial_base"

initial_existing_lock="$fixture/initial-adoption-existing-lock"
cp -R "$initial_adoption" "$initial_existing_lock"
initial_head="$(git -C "$initial_existing_lock" rev-parse HEAD)"
git -C "$initial_existing_lock" switch -q --detach "$initial_base"
mkdir -p "$initial_existing_lock/.governance"
printf '%s\n' '{}' > "$initial_existing_lock/.governance/package-manifest.json"
printf '%s\n' '{}' > "$initial_existing_lock/.governance/manifest.lock.json"
git -C "$initial_existing_lock" add .governance
git -C "$initial_existing_lock" commit -qm 'base already has adoption evidence'
initial_bad_base="$(git -C "$initial_existing_lock" rev-parse HEAD)"
git -C "$initial_existing_lock" switch -q --detach "$initial_head"
expect_code GOV-SYNC-001 run_check "$initial_existing_lock" --base "$initial_bad_base"

atomic_adoption="$fixture/atomic-adoption"
make_fixture "$atomic_adoption"
python3 - "$atomic_adoption" <<'PY'
import hashlib
import json
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
intent_path = root / 'project/ticket-002/intent.json'
intent = json.load(open(intent_path, encoding='utf-8'))
intent['workstream'] = 'governance'
intent['allowedPaths'] = [
    '.governance/manifest.json',
    '.governance/manifest.lock.json',
]
intent['delivery']['budgets']['maxImplementationFiles'] = 2
intent['delivery']['architecture']['components'] = [{
    'name': 'target-adoption',
    'paths': [
        '.governance/manifest.json',
        '.governance/manifest.lock.json',
    ],
}]
intent_path.write_text(json.dumps(intent, indent=2) + '\n', encoding='utf-8')

manifest_path = root / '.governance/manifest.json'
manifest = json.load(open(manifest_path, encoding='utf-8'))
manifest['standard']['version'] = '0.12.0'
manifest_path.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')

package = {
    'schema': 'new-project.package-manifest/v1',
    'files': [
        {'source': 'template/files/AGENTS.template.md', 'target': 'AGENTS.md', 'strategy': 'managed', 'executable': False},
        {'source': 'governance/package-manifest.json', 'target': '.governance/package-manifest.json', 'strategy': 'managed', 'executable': False},
        {'source': 'governance/manifest.default.json', 'target': '.governance/manifest.json', 'strategy': 'seed', 'executable': False},
    ],
}
package_path = root / '.governance/package-manifest.json'
package_path.write_text(json.dumps(package, indent=2) + '\n', encoding='utf-8')

def write_lock(revision, version):
    targets = [item['target'] for item in package['files']]
    lock = {
        'schema': 'new-project.lock/v1',
        'standard': {
            'id': 'wellmanifest/new-project',
            'version': version,
            'sourceRepository': 'wellmanifest/new-project',
            'sourceRevision': revision,
            'publicationStatus': 'published',
        },
        'managedFiles': {
            target: hashlib.sha256((root / target).read_bytes()).hexdigest()
            for target in targets
        },
    }
    (root / '.governance/manifest.lock.json').write_text(
        json.dumps(lock, indent=2) + '\n', encoding='utf-8'
    )

write_lock('a' * 40, '0.12.0')
PY
git -C "$atomic_adoption" init -q
git -C "$atomic_adoption" config user.email governance@example.invalid
git -C "$atomic_adoption" config user.name governance-fixture
git -C "$atomic_adoption" add .
git -C "$atomic_adoption" commit -qm 'atomic adoption base'
atomic_base="$(git -C "$atomic_adoption" rev-parse HEAD)"
git -C "$atomic_adoption" switch -qc ticket-002-adoption
python3 - "$atomic_adoption" "$atomic_base" <<'PY'
import hashlib
import json
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
base = sys.argv[2]
intent_path = root / 'project/ticket-002/intent.json'
intent = json.load(open(intent_path, encoding='utf-8'))
intent['delivery']['acceptedBaseSha'] = base
intent['delivery']['standardAdoption'] = {
    'sourceRepository': 'wellmanifest/new-project',
    'fromRevision': 'a' * 40,
    'toRevision': 'b' * 40,
}
intent_path.write_text(json.dumps(intent, indent=2) + '\n', encoding='utf-8')

manifest_path = root / '.governance/manifest.json'
manifest = json.load(open(manifest_path, encoding='utf-8'))
manifest['standard']['version'] = '0.13.0'
manifest_path.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
(root / 'AGENTS.md').write_text('managed agents v2\n', encoding='utf-8')
(root / 'scripts').mkdir(exist_ok=True)
new_targets = ['scripts/runtime.sh', *[f'src/standard-{index}.js' for index in range(1, 7)]]
for target in new_targets:
    path = root / target
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f'managed {target}\n', encoding='utf-8')

package_path = root / '.governance/package-manifest.json'
package = json.load(open(package_path, encoding='utf-8'))
for target in new_targets:
    package['files'].append({
        'source': f'published/{target}',
        'target': target,
        'strategy': 'managed',
        'executable': target.endswith('.sh'),
    })
package_path.write_text(json.dumps(package, indent=2) + '\n', encoding='utf-8')
lock = {
    'schema': 'new-project.lock/v1',
    'standard': {
        'id': 'wellmanifest/new-project',
        'version': '0.13.0',
        'sourceRepository': 'wellmanifest/new-project',
        'sourceRevision': 'b' * 40,
        'publicationStatus': 'published',
    },
    'managedFiles': {
        item['target']: hashlib.sha256((root / item['target']).read_bytes()).hexdigest()
        for item in package['files'] if item['strategy'] == 'managed'
    },
}
(root / '.governance/manifest.lock.json').write_text(
    json.dumps(lock, indent=2) + '\n', encoding='utf-8'
)
PY
git -C "$atomic_adoption" add .
git -C "$atomic_adoption" commit -qm 'atomic managed upgrade'
if ! run_check "$atomic_adoption" --base "$atomic_base" > "$fixture/atomic-adoption.out"; then
  cat "$fixture/atomic-adoption.out"
  exit 1
fi
grep -q '^GOV-PASS:' "$fixture/atomic-adoption.out"

atomic_bad_hash="$fixture/atomic-adoption-bad-hash"
cp -R "$atomic_adoption" "$atomic_bad_hash"
printf '%s\n' 'tampered managed payload' > "$atomic_bad_hash/AGENTS.md"
git -C "$atomic_bad_hash" add AGENTS.md
git -C "$atomic_bad_hash" commit -qm 'tamper managed payload'
expect_code GOV-SYNC-001 run_check "$atomic_bad_hash" --base "$atomic_base"

atomic_wrong_revision="$fixture/atomic-adoption-wrong-revision"
cp -R "$atomic_adoption" "$atomic_wrong_revision"
sed -i "s/\"toRevision\": \"b\{40\}\"/\"toRevision\": \"c$(printf 'c%.0s' {1..39})\"/" \
  "$atomic_wrong_revision/project/ticket-002/intent.json"
git -C "$atomic_wrong_revision" add project/ticket-002/intent.json
git -C "$atomic_wrong_revision" commit -qm 'bind wrong target revision'
expect_code GOV-SYNC-001 run_check "$atomic_wrong_revision" --base "$atomic_base"

atomic_seed_budget="$fixture/atomic-adoption-seed-budget"
cp -R "$atomic_adoption" "$atomic_seed_budget"
sed -i 's/"maxImplementationFiles": 2/"maxImplementationFiles": 1/' \
  "$atomic_seed_budget/project/ticket-002/intent.json"
git -C "$atomic_seed_budget" add project/ticket-002/intent.json
git -C "$atomic_seed_budget" commit -qm 'understate local adoption budget'
expect_code GOV-BUDGET-001 run_check "$atomic_seed_budget" --base "$atomic_base"

atomic_unlisted="$fixture/atomic-adoption-unlisted"
cp -R "$atomic_adoption" "$atomic_unlisted"
printf '%s\n' 'not in the package contract' > "$atomic_unlisted/scripts/arbitrary.sh"
git -C "$atomic_unlisted" add scripts/arbitrary.sh
git -C "$atomic_unlisted" commit -qm 'add unlisted local path'
expect_code GOV-SCOPE-001 run_check "$atomic_unlisted" --base "$atomic_base"

expect_code GOV-APPROVAL-001 run_check "$atomic_adoption" --base "$atomic_base" \
  --enforce-approval

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

symlink_evidence="$fixture/symlink-evidence.json"
ln -s "$app_evidence" "$symlink_evidence"
expect_code GOV-APPROVAL-003 run_check "$allowed" --changed-file src/app.js --enforce-approval \
  --approval-evidence "$symlink_evidence" --expected-repository example/fixture \
  --expected-pull-request 13 --expected-head aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa

directory_evidence="$fixture/evidence-directory"
mkdir "$directory_evidence"
expect_code GOV-APPROVAL-003 run_check "$allowed" --changed-file src/app.js --enforce-approval \
  --approval-evidence "$directory_evidence" --expected-repository example/fixture \
  --expected-pull-request 13 --expected-head aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa

stale_evidence="$fixture/stale-evidence.json"
write_evidence "$stale_evidence" github-app-review 'validator-agent[bot]' Bot github-api-allowlist \
  example/fixture 13 bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
expect_codes GOV-APPROVAL-004 GOV-APPROVAL-001 run_check "$allowed" --changed-file src/app.js --enforce-approval \
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
expect_codes GOV-APPROVAL-005 GOV-APPROVAL-001 run_check "$allowed" --changed-file src/app.js --enforce-approval \
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

thirty_minutes="$fixture/thirty-minutes"
make_fixture "$thirty_minutes"
mutate_delivery "$thirty_minutes" thirty-minutes
run_check "$thirty_minutes" --changed-file src/app.js > "$fixture/thirty-minutes.out"
grep -q '^GOV-PASS:' "$fixture/thirty-minutes.out"

missing_delivery="$fixture/missing-delivery"
make_fixture "$missing_delivery"
mutate_delivery "$missing_delivery" missing
expect_code GOV-DELIVERY-001 run_check "$missing_delivery" --changed-file src/app.js

over_time="$fixture/over-time"
make_fixture "$over_time"
mutate_delivery "$over_time" xs-over-time
expect_code GOV-DELIVERY-001 run_check "$over_time" --changed-file src/app.js

checkpoint="$fixture/checkpoint"
make_fixture "$checkpoint"
run_check "$checkpoint" --changed-file src/app.js --elapsed-minutes 25 > "$fixture/checkpoint.out"
grep -q 'GOV-DELIVERY-002 WARNING' "$fixture/checkpoint.out"
grep -q '^GOV-PASS:' "$fixture/checkpoint.out"
expect_code GOV-DELIVERY-001 run_check "$checkpoint" --changed-file src/app.js --elapsed-minutes 30

file_budget="$fixture/file-budget"
make_fixture "$file_budget"
printf '%s\n' 'export const extra = true;' > "$file_budget/src/extra.js"
expect_code GOV-BUDGET-001 run_check "$file_budget" --changed-file src/app.js --changed-file src/extra.js

policy_budget="$fixture/policy-budget"
make_fixture "$policy_budget"
mutate_delivery "$policy_budget" over-policy-budget
expect_code GOV-DELIVERY-001 run_check "$policy_budget" --changed-file src/app.js

s_profile_budget="$fixture/s-profile-budget"
make_fixture "$s_profile_budget"
mutate_delivery "$s_profile_budget" s-profile-overflow
expect_code GOV-DELIVERY-001 run_check "$s_profile_budget" --changed-file src/app.js

m_profile="$fixture/m-profile"
make_fixture "$m_profile"
mutate_delivery "$m_profile" m-profile
run_check "$m_profile" --changed-file src/app.js > "$fixture/m-profile.out"
grep -q '^GOV-PASS:' "$fixture/m-profile.out"

invalid_monorepo="$fixture/invalid-monorepo"
make_fixture "$invalid_monorepo"
python3 - "$invalid_monorepo/.governance/manifest.json" <<'PY'
import json
import sys

path = sys.argv[1]
manifest = json.load(open(path, encoding='utf-8'))
manifest['repository'] = {'mode': 'monorepo', 'componentRoots': []}
open(path, 'w', encoding='utf-8').write(json.dumps(manifest, indent=2) + '\n')
PY
expect_code GOV-MANIFEST-001 run_check "$invalid_monorepo" --changed-file src/app.js

incomplete_profiles="$fixture/incomplete-profiles"
make_fixture "$incomplete_profiles"
python3 - "$incomplete_profiles/.governance/manifest.json" <<'PY'
import json
import sys

path = sys.argv[1]
manifest = json.load(open(path, encoding='utf-8'))
manifest['delivery']['profiles'].pop('L')
open(path, 'w', encoding='utf-8').write(json.dumps(manifest, indent=2) + '\n')
PY
expect_code GOV-MANIFEST-001 run_check "$incomplete_profiles" --changed-file src/app.js

monorepo_scope="$fixture/monorepo-scope"
make_fixture "$monorepo_scope"
python3 - "$monorepo_scope/.governance/manifest.json" <<'PY'
import json
import sys

path = sys.argv[1]
manifest = json.load(open(path, encoding='utf-8'))
manifest['repository'] = {'mode': 'monorepo', 'componentRoots': ['services/**']}
open(path, 'w', encoding='utf-8').write(json.dumps(manifest, indent=2) + '\n')
PY
expect_code GOV-SCOPE-001 run_check "$monorepo_scope" --changed-file src/app.js

ambiguous_architecture="$fixture/ambiguous-architecture"
make_fixture "$ambiguous_architecture"
mutate_delivery "$ambiguous_architecture" ambiguous-component
expect_code GOV-ARCHITECTURE-001 run_check "$ambiguous_architecture" --changed-file src/app.js

single_segment_glob="$fixture/single-segment-glob"
make_fixture "$single_segment_glob"
sed -i 's#"allowedPaths": \["src/\*\*"\]#"allowedPaths": ["src/*"]#' "$single_segment_glob/project/ticket-002/intent.json"
expect_code GOV-SCOPE-001 run_check "$single_segment_glob" --changed-file src/nested/app.js

expect_code GOV-DIFF-001 run_check "$allowed" --base definitely-not-a-commit
expect_code GOV-SYNC-001 run_check "$allowed" --changed-file TODO.md --lock ../outside.lock

stale_base="$fixture/stale-base"
make_fixture "$stale_base"
(
  cd "$stale_base"
  git init -q
  git config user.email governance@example.invalid
  git config user.name governance-fixture
  git add .
  git commit -qm 'fixture baseline'
  expect_code GOV-BASE-001 run_check "$stale_base" --base HEAD --changed-file src/app.js
)

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

plan_release="$fixture/plan-release"
make_fixture "$plan_release"
sed -i 's/Status\*\*: IN_PROGRESS/Status**: PLAN/' "$plan_release/project/ticket-002/README.md"
add_active_ticket "$plan_release" ticket-003 application '["src/**"]'
run_check "$plan_release" --changed-file src/app.js > "$fixture/plan-release.out"
grep -q '^GOV-PASS:' "$fixture/plan-release.out"

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

governance_root_contracts="$fixture/governance-root-contracts"
make_fixture "$governance_root_contracts"
touch "$governance_root_contracts/.env.example"
python3 - "$governance_root_contracts/project/ticket-002/intent.json" <<'PY'
import json
import sys

path = sys.argv[1]
with open(path, encoding='utf-8') as handle:
    intent = json.load(handle)
intent['workstream'] = 'governance'
intent['allowedPaths'] = ['CHANGELOG.md', '.env.example']
intent['delivery']['architecture']['components'] = [{
    'name': 'root-contracts',
    'paths': ['CHANGELOG.md', '.env.example'],
}]
with open(path, 'w', encoding='utf-8') as handle:
    json.dump(intent, handle, indent=2)
    handle.write('\n')
PY
run_check "$governance_root_contracts" --changed-file CHANGELOG.md \
  > "$fixture/governance-changelog.out"
grep -q '^GOV-PASS:' "$fixture/governance-changelog.out"
run_check "$governance_root_contracts" --changed-file .env.example \
  > "$fixture/governance-env-example.out"
grep -q '^GOV-PASS:' "$fixture/governance-env-example.out"

foreign_root_contracts="$fixture/foreign-root-contracts"
make_fixture "$foreign_root_contracts"
touch "$foreign_root_contracts/.env.example"
python3 - "$foreign_root_contracts/project/ticket-002/intent.json" <<'PY'
import json
import sys

path = sys.argv[1]
with open(path, encoding='utf-8') as handle:
    intent = json.load(handle)
intent['allowedPaths'] = ['CHANGELOG.md', '.env.example']
intent['delivery']['architecture']['components'] = [{
    'name': 'invalid-root-contract-claim',
    'paths': ['CHANGELOG.md', '.env.example'],
}]
with open(path, 'w', encoding='utf-8') as handle:
    json.dump(intent, handle, indent=2)
    handle.write('\n')
PY
expect_code GOV-WORKSTREAM-003 run_check "$foreign_root_contracts" \
  --changed-file CHANGELOG.md
expect_code GOV-WORKSTREAM-003 run_check "$foreign_root_contracts" \
  --changed-file .env.example

stackless_version="$fixture/stackless-version"
make_fixture "$stackless_version"
configure_version_ticket "$stackless_version" integration
run_check "$stackless_version" --changed-file VERSION \
  > "$fixture/stackless-version.out"
grep -q '^GOV-PASS:' "$fixture/stackless-version.out"

foreign_version="$fixture/foreign-version"
make_fixture "$foreign_version"
configure_version_ticket "$foreign_version" application
expect_code GOV-WORKSTREAM-003 run_check "$foreign_version" \
  --changed-file VERSION

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
cp -R "$history_good/project/ticket-002" "$fixture/history-good-ticket"
rm -rf "$history_good/project/ticket-002"
(
  cd "$history_good"
  git init -q
  git config user.email governance@example.invalid
  git config user.name governance-fixture
  git add .
  git commit -qm 'baseline without ticket'
  base="$(git rev-parse HEAD)"
  git switch -qc ticket-002-work
  cp -R "$fixture/history-good-ticket" project/ticket-002
  set_accepted_base "$history_good" "$base"
  git add project/ticket-002
  git commit -qm 'plan exists'
  printf '%s\n' 'export const ok = 2;' > src/app.js
  git add src/app.js
  git commit -qm 'implementation after plan'
  if ! run_check "$history_good" --base "$base" > "$fixture/history-good.out"; then
    cat "$fixture/history-good.out"
    exit 1
  fi
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
  git switch -qc ticket-002-work
  cp -R "$fixture/ticket-002.saved" project/ticket-002
  set_accepted_base "$history_bad" "$base"
  printf '%s\n' 'export const late = true;' > src/app.js
  git add .
  git commit -qm 'ticket and implementation together'
  expect_code GOV-INTENT-003 run_check "$history_bad" --base "$base"
)

legacy_active="$fixture/legacy-active"
make_fixture "$legacy_active"
sed -i 's#"schema": "new-project.intent/v3"#"schema": "new-project.intent/v2"#' "$legacy_active/project/ticket-002/intent.json"
sed -i '/"classification":/d' "$legacy_active/project/ticket-002/intent.json"
expect_code GOV-INTENT-002 run_check "$legacy_active" --changed-file src/app.js

invalid_classification="$fixture/invalid-classification"
make_fixture "$invalid_classification"
sed -i 's/"kind": "FEATURE"/"kind": "UNKNOWN"/' "$invalid_classification/project/ticket-002/intent.json"
expect_code GOV-INTENT-002 run_check "$invalid_classification" --changed-file src/app.js

assert_classification_drift() {
  local mutation="$1"
  local target="$fixture/classification-drift-$mutation"
  make_fixture "$target"
  python3 - "$target/.governance/work-classification.dsl.json" "$mutation" <<'PY'
import json
import sys

path, mutation = sys.argv[1:]
value = json.load(open(path, encoding='utf-8'))
if mutation == 'schema-ref':
    value['$schema'] = './other.schema.json'
elif mutation == 'kind-order':
    value['ordering']['kindOrder'] = ['FEATURE', 'BUG', 'SERVICE']
elif mutation == 'priority-order':
    value['ordering']['priorityOrder'] = ['P1', 'P0', 'P2', 'P3']
elif mutation == 'derivation':
    value['priorityDerivation']['impact']['high'] = 'P3'
elif mutation == 'rule-order':
    value['rules'][0], value['rules'][1] = value['rules'][1], value['rules'][0]
elif mutation == 'mixed-condition':
    value['rules'][0]['when']['request'] = 'new-behavior'
elif mutation == 'condition-value':
    value['rules'][0]['when']['impact'] = 'cosmetic'
elif mutation == 'assignment':
    value['rules'][4]['assign'] = {'kind': 'BUG', 'origin': 'regression'}
elif mutation == 'priority-source':
    value['rules'][5]['prioritySource'] = 'declared'
else:
    raise AssertionError(mutation)
open(path, 'w', encoding='utf-8').write(json.dumps(value, indent=2) + '\n')
PY
  expect_code GOV-MANIFEST-001 run_check "$target" --changed-file TODO.md
}

for mutation in schema-ref kind-order priority-order derivation rule-order \
  mixed-condition condition-value assignment priority-source; do
  assert_classification_drift "$mutation"
done

echo 'governance validator: PASS'
