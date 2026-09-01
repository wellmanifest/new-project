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

git init --quiet --initial-branch=main "$fixture/repo"
git -C "$fixture/repo" config user.email continuity-test@example.invalid
git -C "$fixture/repo" config user.name continuity-test
git -C "$fixture/repo" remote add origin https://user:secret-marker@github.com/example/continuity-fixture.git
mkdir -p "$fixture/repo/project/ticket-001" "$fixture/repo/.subactor"
cp "$repo_root/.subactor/manifest.json" "$fixture/repo/.subactor/manifest.json"
cp "$repo_root/.subactor/.gitignore" "$fixture/repo/.subactor/.gitignore"
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

plan_sha="$(printf plan | sha256sum | cut -d' ' -f1)"
slice_sha="$(printf slice | sha256sum | cut -d' ' -f1)"
capture=(
  python3 "$runtime" capture
  --root "$fixture/repo"
  --ticket ticket-001
  --session-id session-001
  --worktree-id ticket-001--continuity
  --authorization-ref authorization:session/ticket-001
  --plan-ref artifact:plan/ticket-001/v1
  --plan-sha256 "$plan_sha"
  --slice-ref artifact:slice/ticket-001/1
  --slice-sha256 "$slice_sha"
  --slice-ordinal 1
  --slice-total 1
  --remote-name origin
  --remote-account-ref account:github/example
  --remote-observation-receipt receipt:remote-observation/ticket-001/1
)

"${capture[@]}" \
  --phase edit \
  --remaining AC-01 \
  --next-action edit \
  --next-criterion AC-01 > "$fixture/event-1.json"

event_stream="$fixture/repo/.subactor/sessions/work-continuity.jsonl"
checkpoint_index="$fixture/repo/.subactor/recovery/checkpoint-index.json"
test -f "$event_stream"
test -f "$checkpoint_index"
test "$(wc -l < "$event_stream")" -eq 1
cp "$event_stream" "$fixture/event-stream-prefix.jsonl"

python3 - "$fixture/event-1.json" "$checkpoint_index" "$repo_root/.subactor/manifest.json" <<'PY'
import json
import sys

event = json.load(open(sys.argv[1], encoding="utf-8"))
index = json.load(open(sys.argv[2], encoding="utf-8"))
manifest = json.load(open(sys.argv[3], encoding="utf-8"))
checkpoint = event["checkpoint"]
assert event["schema"] == "new-project.work-continuity-event/v2"
assert event["sessionId"] == "session-001"
assert checkpoint["schema"] == "new-project.work-continuity/v2"
assert checkpoint["authority"] == "advisory-projection"
assert checkpoint["plan"]["ref"] == "artifact:plan/ticket-001/v1"
assert checkpoint["slice"]["ordinal"] == checkpoint["slice"]["total"] == 1
assert checkpoint["branchRef"] == "ticket/001-continuity"
assert checkpoint["remoteObservation"]["accountRef"] == "account:github/example"
assert checkpoint["workspace"]["resumeSource"] == "commit"
assert index["schema"] == "new-project.work-continuity-index/v2"
assert index["maxEntries"] == 128 and len(index["entries"]) == 1
continuity = manifest["continuity"]
assert continuity["eventStreamPolicyMaxBytes"] is None
assert continuity["checkpointIndexMaxBytes"] == 262144
PY

python3 - "$fixture/event-1.json" "$fixture/checkpoint-1.json" <<'PY'
import json
import sys
event = json.load(open(sys.argv[1], encoding="utf-8"))
open(sys.argv[2], "w", encoding="utf-8").write(json.dumps(event["checkpoint"], indent=2) + "\n")
PY
python3 "$runtime" validate "$fixture/event-1.json" > "$fixture/valid-event.json"
python3 "$runtime" validate "$fixture/checkpoint-1.json" > "$fixture/valid-checkpoint.json"
python3 "$runtime" validate "$checkpoint_index" > "$fixture/valid-index.json"
python3 "$runtime" verify --root "$fixture/repo" --checkpoint "$fixture/checkpoint-1.json" \
  > "$fixture/verified-1.json"
grep -q '"authorityVerified": false' "$fixture/verified-1.json"
grep -q '"remoteAccountMustBeReobserved": true' "$fixture/verified-1.json"
if grep -q 'secret-marker' "$fixture/event-1.json"; then
  printf '%s\n' 'repository credentials leaked into continuity event' >&2
  exit 1
fi

# Dirty prose, stash or an untracked file is not a resumable boundary. A failed
# capture must append neither the event stream nor the atomic index.
printf '%s\n' 'unfinished material work' > "$fixture/repo/work.txt"
cp "$event_stream" "$fixture/events-before-dirty.jsonl"
cp "$checkpoint_index" "$fixture/index-before-dirty.json"
status=0
"${capture[@]}" \
  --phase edit \
  --remaining AC-01 \
  --next-action edit \
  --next-criterion AC-01 > "$fixture/dirty.out" 2> "$fixture/dirty.err" || status=$?
test "$status" -eq 2
grep -q 'GOV-CONTINUITY-001' "$fixture/dirty.err"
cmp "$event_stream" "$fixture/events-before-dirty.jsonl"
cmp "$checkpoint_index" "$fixture/index-before-dirty.json"

snapshot_sha="$(printf snapshot | sha256sum | cut -d' ' -f1)"
"${capture[@]}" \
  --phase validation \
  --lease-ref receipt:lease/ticket-001/2 \
  --lease-revision 2 \
  --fencing-token 7 \
  --snapshot-ref artifact:snapshot/ticket-001/2 \
  --snapshot-sha256 "$snapshot_sha" \
  --snapshot-receipt receipt:snapshot/ticket-001/2 \
  --snapshot-secret-scan-receipt receipt:secret-scan/ticket-001/2 \
  --completed AC-01 \
  --remaining AC-02 \
  --evidence artifact:test/continuity/1 \
  --pending validation,in-flight,idempotency:continuity-validation,receipt:run/42 \
  --next-action validate \
  --next-criterion AC-02 > "$fixture/event-2.json"

test "$(wc -l < "$event_stream")" -eq 2
head -n 1 "$event_stream" > "$fixture/first-event-after.jsonl"
cmp "$fixture/event-stream-prefix.jsonl" "$fixture/first-event-after.jsonl"
test "$(stat -c '%s' "$checkpoint_index")" -le 262144
test -z "$(find "$fixture/repo/.subactor/recovery" -name 'checkpoint-index.*.json' -print -quit)"

python3 - "$fixture/event-2.json" "$fixture/checkpoint-2.json" "$checkpoint_index" <<'PY'
import json
import sys
event = json.load(open(sys.argv[1], encoding="utf-8"))
checkpoint = event["checkpoint"]
index = json.load(open(sys.argv[3], encoding="utf-8"))
assert event["eventSequence"] == 2
assert event["previousEventRef"] is not None
assert checkpoint["sequence"] == 2
assert checkpoint["previousCheckpointRef"] is not None
assert checkpoint["workspace"]["resumeSource"] == "snapshot"
assert checkpoint["workspace"]["snapshotReceipt"] == "receipt:snapshot/ticket-001/2"
assert index["entries"][0]["checkpointSequence"] == 2
open(sys.argv[2], "w", encoding="utf-8").write(json.dumps(checkpoint, indent=2) + "\n")
PY
python3 "$runtime" resolve --root "$fixture/repo" --ticket ticket-001 > "$fixture/resolved.json"
cmp "$fixture/checkpoint-2.json" "$fixture/resolved.json"
python3 "$runtime" verify --root "$fixture/repo" --ticket ticket-001 > "$fixture/verified-2.json"
grep -q '"leaseMustBeRevalidated": true' "$fixture/verified-2.json"

# The bounded index is derived, not authority: removing it and explicitly
# rebuilding from the unlimited append-only stream reproduces the same latest
# checkpoint binding without changing the stream.
events_sha_before="$(sha256sum "$event_stream" | cut -d' ' -f1)"
rm "$checkpoint_index"
python3 "$runtime" rebuild-index --root "$fixture/repo" > "$fixture/rebuilt.json"
test "$events_sha_before" = "$(sha256sum "$event_stream" | cut -d' ' -f1)"
grep -q '"status": "rebuilt"' "$fixture/rebuilt.json"

# Current observation wins over prose or a stale checkpoint.
git -C "$fixture/repo" add work.txt
git -C "$fixture/repo" commit --quiet -m advance-after-checkpoint
status=0
python3 "$runtime" verify --root "$fixture/repo" --checkpoint "$fixture/checkpoint-2.json" \
  > "$fixture/stale.out" 2> "$fixture/stale.err" || status=$?
test "$status" -eq 3
grep -q 'GOV-CONTINUITY-003' "$fixture/stale.err"

# Closed objects reject raw conversation, secrets and absolute host paths.
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
  "$fixture/checkpoint-1.json" "$fixture/event-2.json" "$checkpoint_index" <<'PY'
import json
import sys
from jsonschema import Draft202012Validator

schema = json.load(open(sys.argv[1], encoding="utf-8"))
validator = Draft202012Validator(schema, format_checker=Draft202012Validator.FORMAT_CHECKER)
for path in sys.argv[2:]:
    validator.validate(json.load(open(path, encoding="utf-8")))
unsafe = json.load(open(sys.argv[2], encoding="utf-8"))
unsafe["workspace"]["resumeSource"] = "snapshot"
assert not validator.is_valid(unsafe)
PY

printf '%s\n' 'work continuity tests passed'
