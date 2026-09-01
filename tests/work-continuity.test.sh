#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
runtime="$repo_root/scripts/work_continuity.py"
fixture="$(mktemp -d "${TMPDIR:-/tmp}/new-project-continuity.XXXXXX")"
cleanup() { rm -rf "$fixture"; }
trap cleanup EXIT INT TERM

python3 - "$repo_root/governance/work-continuity.schema.json" <<'PY'
import json
import sys
from jsonschema import Draft202012Validator

schema = json.load(open(sys.argv[1], encoding="utf-8"))
Draft202012Validator.check_schema(schema)
PY

python3 - "$repo_root/subprojects/ticket-lifecycle/ticket-lifecycle.schema.json" \
  "$repo_root/subprojects/ticket-lifecycle/ticket-lifecycle.v1.gbnf" <<'PY'
import copy
import json
import sys
from jsonschema import Draft202012Validator

schema = json.load(open(sys.argv[1], encoding="utf-8"))
validator = Draft202012Validator(schema)
Draft202012Validator.check_schema(schema)
request = {
    "schema": "wellmanifest.ticket-lifecycle/v1",
    "kind": "transition-request",
    "requestId": "request:continuity_001",
    "repositoryRef": "repository:continuity_fixture",
    "workstreamRef": "workstream:application",
    "action": "checkpoint",
    "ticket": "ticket-001",
    "expectedState": "editing",
    "targetState": "editing",
    "intentRef": "artifact:intent_ticket_001",
    "authorizationRef": "authorization:session_ticket_001",
    "evidenceRefs": ["receipt:continuity.ticket-001.1.abc"],
    "idempotencyKey": "idempotency:continuity_001",
}
validator.validate(request)
invalid = copy.deepcopy(request)
invalid["targetState"] = "validating"
assert not validator.is_valid(invalid)
invalid = copy.deepcopy(request)
invalid["evidenceRefs"] = ["receipt:other.abc"]
assert not validator.is_valid(invalid)
grammar = open(sys.argv[2], encoding="utf-8").read()
assert 'checkpoint-editing' in grammar
assert 'receipt:continuity.' in grammar
PY

git init --quiet --initial-branch=main "$fixture/repo"
git -C "$fixture/repo" config user.email continuity-test@example.invalid
git -C "$fixture/repo" config user.name continuity-test
git -C "$fixture/repo" remote add origin https://user:secret-marker@github.com/example/continuity-fixture.git
mkdir -p "$fixture/repo/project/ticket-001"
printf '%s\n' '# continuity fixture' > "$fixture/repo/README.md"
printf '%s\n' '- **Status**: IN_PROGRESS' > "$fixture/repo/project/ticket-001/README.md"
python3 - "$fixture/repo/project/ticket-001/intent.json" <<'PY'
import json
import sys

value = {
    "schema": "new-project.intent/v3",
    "ticket": "ticket-001",
    "summary": "continuity fixture",
    "workstream": "application",
    "classification": {"kind": "FEATURE", "priority": "P1", "origin": "requested"},
    "allowedPaths": ["project/ticket-001/**", "src/**"],
    "forbiddenPaths": ["project/ticket-*/user-*.md"],
    "stacks": [],
    "dependsOn": [],
    "conflictsWith": [],
    "integrationTicket": None,
    "delivery": {
        "acceptedBaseSha": "0" * 40,
        "targetBranch": "main",
        "outcome": "prove continuity",
        "nonGoals": ["no authority from checkpoint"],
    },
}
open(sys.argv[1], "w", encoding="utf-8").write(json.dumps(value, indent=2) + "\n")
PY
git -C "$fixture/repo" add .
git -C "$fixture/repo" commit --quiet -m baseline
git -C "$fixture/repo" switch --quiet -c ticket/001-continuity

registry="$fixture/registry.json"
python3 "$runtime" capture \
  --root "$fixture/repo" \
  --registry "$registry" \
  --ticket ticket-001 \
  --phase edit \
  --worktree-id continuity-fixture \
  --authorization-ref authorization:session/ticket-001 \
  --remaining AC-01 \
  --next-action edit \
  --next-criterion AC-01 > "$fixture/checkpoint-1.json"

python3 "$runtime" validate "$fixture/checkpoint-1.json" > "$fixture/valid-1.json"
grep -q '"status": "valid"' "$fixture/valid-1.json"
grep -q '"repositoryRef": "repository:github.com/example/continuity-fixture"' "$fixture/checkpoint-1.json"
if grep -q 'secret-marker' "$fixture/checkpoint-1.json"; then
  printf '%s\n' 'repository credentials leaked into checkpoint' >&2
  exit 1
fi
python3 "$runtime" verify \
  --root "$fixture/repo" \
  --checkpoint "$fixture/checkpoint-1.json" > "$fixture/verified-1.json"
grep -q '"authorityVerified": false' "$fixture/verified-1.json"
grep -q '"status": "matches-observed-state"' "$fixture/verified-1.json"

# A dirty workspace cannot be represented by conversation prose or a local
# stash. It needs an already-created external, secret-scanned snapshot.
printf '%s\n' 'unfinished material work' > "$fixture/repo/work.txt"
cp "$registry" "$fixture/registry-before-dirty.json"
status=0
python3 "$runtime" capture \
  --root "$fixture/repo" \
  --registry "$registry" \
  --ticket ticket-001 \
  --phase edit \
  --worktree-id continuity-fixture \
  --authorization-ref authorization:session/ticket-001 \
  --remaining AC-01 \
  --next-action edit \
  --next-criterion AC-01 > "$fixture/dirty.out" 2> "$fixture/dirty.err" || status=$?
test "$status" -eq 2
grep -q 'GOV-CONTINUITY-001' "$fixture/dirty.err"
cmp "$registry" "$fixture/registry-before-dirty.json"

snapshot_sha="$(printf '%064d' 0 | tr 0 a)"
python3 "$runtime" capture \
  --root "$fixture/repo" \
  --registry "$registry" \
  --ticket ticket-001 \
  --phase validation \
  --worktree-id continuity-fixture \
  --authorization-ref authorization:session/ticket-001 \
  --lease-ref receipt:lease/ticket-001/2 \
  --lease-revision 2 \
  --fencing-token 7 \
  --snapshot-ref artifact:snapshot/ticket-001/2 \
  --snapshot-sha256 "$snapshot_sha" \
  --snapshot-secret-scan-receipt receipt:secret-scan/ticket-001/2 \
  --completed AC-01 \
  --remaining AC-02 \
  --evidence artifact:test/continuity/1 \
  --pending validation,in-flight,idempotency:continuity-validation,receipt:run/42 \
  --next-action validate \
  --next-criterion AC-02 > "$fixture/checkpoint-2.json"

python3 "$runtime" validate "$registry" > "$fixture/registry-valid.json"
python3 "$runtime" resolve \
  --root "$fixture/repo" \
  --registry "$registry" \
  --ticket ticket-001 > "$fixture/resolved.json"
cmp "$fixture/checkpoint-2.json" "$fixture/resolved.json"
python3 "$runtime" verify \
  --root "$fixture/repo" \
  --registry "$registry" \
  --ticket ticket-001 > "$fixture/verified-2.json"
grep -q '"leaseMustBeRevalidated": true' "$fixture/verified-2.json"

# A restored cache must receive the complete chain, in order. Replay is
# idempotent, while rebinding an existing receipt reference is forbidden.
restored="$fixture/restored.json"
python3 "$runtime" record \
  --root "$fixture/repo" --registry "$restored" \
  --checkpoint "$fixture/checkpoint-1.json" > "$fixture/restored-1.json"
python3 "$runtime" record \
  --root "$fixture/repo" --registry "$restored" \
  --checkpoint "$fixture/checkpoint-2.json" > "$fixture/restored-2.json"
python3 "$runtime" record \
  --root "$fixture/repo" --registry "$restored" \
  --checkpoint "$fixture/checkpoint-2.json" > "$fixture/restored-replay.json"
grep -q '"status": "already-recorded"' "$fixture/restored-replay.json"

python3 - "$fixture/checkpoint-2.json" "$fixture/rebound.json" <<'PY'
import json
import sys

value = json.load(open(sys.argv[1], encoding="utf-8"))
value["headSha"] = "f" * 40
open(sys.argv[2], "w", encoding="utf-8").write(json.dumps(value) + "\n")
PY
cp "$restored" "$fixture/restored-before-rebind.json"
status=0
python3 "$runtime" record \
  --root "$fixture/repo" --registry "$restored" \
  --checkpoint "$fixture/rebound.json" > "$fixture/rebind.out" 2> "$fixture/rebind.err" || status=$?
test "$status" -eq 2
grep -q 'GOV-CONTINUITY-002' "$fixture/rebind.err"
cmp "$restored" "$fixture/restored-before-rebind.json"

# A stale checkpoint can guide reconciliation but cannot resume mutation.
git -C "$fixture/repo" add work.txt
git -C "$fixture/repo" commit --quiet -m advance-after-checkpoint
status=0
python3 "$runtime" verify \
  --root "$fixture/repo" \
  --checkpoint "$fixture/checkpoint-2.json" > "$fixture/stale.out" 2> "$fixture/stale.err" || status=$?
test "$status" -eq 3
grep -q 'GOV-CONTINUITY-003' "$fixture/stale.err"

# Closed objects prevent raw prose, secrets and absolute host paths from being
# smuggled into a continuity receipt.
python3 - "$fixture/checkpoint-1.json" "$fixture/unsafe.json" <<'PY'
import json
import sys

value = json.load(open(sys.argv[1], encoding="utf-8"))
value["rawConversation"] = "sensitive material must not be stored"
value["repositoryRef"] = "/home/example/private-checkout"
open(sys.argv[2], "w", encoding="utf-8").write(json.dumps(value) + "\n")
PY
status=0
python3 "$runtime" validate "$fixture/unsafe.json" > "$fixture/unsafe.out" 2> "$fixture/unsafe.err" || status=$?
test "$status" -eq 2
grep -q 'GOV-CONTINUITY-001' "$fixture/unsafe.err"

python3 - "$repo_root/governance/work-continuity.schema.json" \
  "$fixture/checkpoint-1.json" "$registry" <<'PY'
import json
import sys
from jsonschema import Draft202012Validator

schema = json.load(open(sys.argv[1], encoding="utf-8"))
validator = Draft202012Validator(schema, format_checker=Draft202012Validator.FORMAT_CHECKER)
for path in sys.argv[2:]:
    validator.validate(json.load(open(path, encoding="utf-8")))

unsafe = json.load(open(sys.argv[2], encoding="utf-8"))
unsafe["repositoryRef"] = "/home/example/private-checkout"
assert not validator.is_valid(unsafe)
unsafe = json.load(open(sys.argv[2], encoding="utf-8"))
unsafe["workspace"]["statusSha256"] = "a" * 64
assert not validator.is_valid(unsafe)
PY

printf '%s\n' 'work continuity tests passed'
