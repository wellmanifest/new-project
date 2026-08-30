#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
fixture="$(mktemp -d "${TMPDIR:-/tmp}/new-project-ticket-activity.XXXXXX")"
cleanup() { rm -rf "$fixture"; }
trap cleanup EXIT INT TERM

git init --quiet --initial-branch=main "$fixture/repo"
git -C "$fixture/repo" config user.email activity-test@example.invalid
git -C "$fixture/repo" config user.name activity-test
mkdir -p "$fixture/repo/governance" "$fixture/repo/project/ticket-001"
cp "$repo_root/governance/ticket-activity.json" "$fixture/repo/governance/ticket-activity.json"
printf '%s\n' '# sample' > "$fixture/repo/README.md"
printf '%s\n' '- **Status**: IN_PROGRESS' > "$fixture/repo/project/ticket-001/README.md"
git -C "$fixture/repo" add .
git -C "$fixture/repo" commit --quiet -m initial-ticket
head_sha="$(git -C "$fixture/repo" rev-parse HEAD)"

# Missing optional registry is conservative and does not block ordinary work.
python3 "$repo_root/scripts/ticket_activity.py" --root "$fixture/repo" resolve \
  --ticket-dir "$fixture/repo/project/ticket-001" --active-status IN_PROGRESS \
  > "$fixture/absent.json"
grep -q '"active": true' "$fixture/absent.json"
grep -q 'registry-absent' "$fixture/absent.json"

git -C "$fixture/repo" switch --quiet -c delivery
printf '%s\n' integrated >> "$fixture/repo/README.md"
git -C "$fixture/repo" add README.md
git -C "$fixture/repo" commit --quiet -m terminal
terminal_sha="$(git -C "$fixture/repo" rev-parse HEAD)"
git -C "$fixture/repo" branch -f main "$terminal_sha"
repository_ref="$(python3 - "$repo_root/scripts" "$fixture/repo" <<'PY'
import sys
sys.path.insert(0, sys.argv[1])
from pathlib import Path
from ticket_activity import repository_ref
print(repository_ref(Path(sys.argv[2])))
PY
)"
cat > "$fixture/receipt.json" <<JSON
{
  "receiptRef": "receipt:test/merged/1",
  "ticket": "ticket-001",
  "outcome": "merged",
  "headSha": "$head_sha",
  "terminalSha": "$terminal_sha",
  "targetBranch": "main",
  "occurredAt": "2026-08-30T12:00:00Z"
}
JSON
python3 "$repo_root/scripts/ticket_activity.py" --root "$fixture/repo" record \
  --receipt "$fixture/receipt.json" > "$fixture/recorded.json"

status=0
python3 "$repo_root/scripts/ticket_activity.py" --root "$fixture/repo" resolve \
  --ticket-dir "$fixture/repo/project/ticket-001" --active-status IN_PROGRESS \
  > "$fixture/released.json" || status=$?
test "$status" -eq 1
grep -q '"authority": "terminal-receipt"' "$fixture/released.json"

# New work on the ticket branch after the receipt reopens the reservation.
git -C "$fixture/repo" switch --quiet -c ticket/001 "$head_sha"
printf '%s\n' reopened > "$fixture/repo/reopened.txt"
git -C "$fixture/repo" add reopened.txt
git -C "$fixture/repo" commit --quiet -m reopened
python3 "$repo_root/scripts/ticket_activity.py" --root "$fixture/repo" resolve \
  --ticket-dir "$fixture/repo/project/ticket-001" --active-status IN_PROGRESS \
  > "$fixture/reopened.json"
grep -q '"active": true' "$fixture/reopened.json"

# A malformed cache fails closed with a stable diagnostic and can be recovered
# without rewriting repository history.
registry="$fixture/repo/.git/new-project/terminal-receipts.json"
mv "$registry" "$fixture/valid-registry.json"
printf '%s\n' '{broken' > "$registry"
status=0
python3 "$repo_root/scripts/ticket_activity.py" --root "$fixture/repo" validate \
  > "$fixture/invalid.out" 2> "$fixture/invalid.err" || status=$?
test "$status" -eq 2
grep -q 'GOV-TICKET-ACTIVITY-001' "$fixture/invalid.err"
mv "$fixture/valid-registry.json" "$registry"
python3 "$repo_root/scripts/ticket_activity.py" --root "$fixture/repo" validate \
  > "$fixture/recovered.json"
grep -q '"status": "valid"' "$fixture/recovered.json"

# A stale receipt cannot overwrite the last known-valid registry.
cp "$registry" "$fixture/registry-before-reject.json"
status=0
python3 "$repo_root/scripts/ticket_activity.py" --root "$fixture/repo" record \
  --receipt "$fixture/receipt.json" > "$fixture/reject.out" 2> "$fixture/reject.err" || status=$?
test "$status" -eq 2
cmp "$registry" "$fixture/registry-before-reject.json"

# A receipt reference is idempotent but append-only: it cannot be rebound.
python3 - "$fixture/receipt.json" <<'PY'
import json, sys
path = sys.argv[1]
value = json.load(open(path, encoding="utf-8"))
value["terminalSha"] = "0" * 40
open(path, "w", encoding="utf-8").write(json.dumps(value) + "\n")
PY
status=0
python3 "$repo_root/scripts/ticket_activity.py" --root "$fixture/repo" record \
  --receipt "$fixture/receipt.json" > "$fixture/rebind.out" 2> "$fixture/rebind.err" || status=$?
test "$status" -eq 2
grep -q 'append-only' "$fixture/rebind.err"
cmp "$registry" "$fixture/registry-before-reject.json"

printf '%s\n' 'ticket activity tests passed'
