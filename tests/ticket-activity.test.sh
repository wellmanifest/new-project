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

# A protected rebase rewrites commit identities. Accept it only when the
# original and terminal ranges are linear, equally long and have the same
# ordered stable patch IDs, while the terminal remains reachable from target.
git init --quiet --initial-branch=main "$fixture/rebase"
git -C "$fixture/rebase" config user.email activity-test@example.invalid
git -C "$fixture/rebase" config user.name activity-test
mkdir -p "$fixture/rebase/governance" "$fixture/rebase/project/ticket-002"
cp "$repo_root/governance/ticket-activity.json" "$fixture/rebase/governance/ticket-activity.json"
printf '%s\n' '# rebase fixture' > "$fixture/rebase/README.md"
printf '%s\n' '- **Status**: IN_PROGRESS' > "$fixture/rebase/project/ticket-002/README.md"
git -C "$fixture/rebase" add .
git -C "$fixture/rebase" commit --quiet -m base
rebase_base="$(git -C "$fixture/rebase" rev-parse HEAD)"

git -C "$fixture/rebase" switch --quiet -c delivery
printf '%s\n' first > "$fixture/rebase/first.txt"
git -C "$fixture/rebase" add first.txt
git -C "$fixture/rebase" commit --quiet -m first
first_sha="$(git -C "$fixture/rebase" rev-parse HEAD)"
printf '%s\n' second > "$fixture/rebase/second.txt"
git -C "$fixture/rebase" add second.txt
git -C "$fixture/rebase" commit --quiet -m second
rebase_head="$(git -C "$fixture/rebase" rev-parse HEAD)"

git -C "$fixture/rebase" switch --quiet main
printf '%s\n' target-advanced > "$fixture/rebase/target.txt"
git -C "$fixture/rebase" add target.txt
git -C "$fixture/rebase" commit --quiet -m target-advanced
rebase_target_base="$(git -C "$fixture/rebase" rev-parse HEAD)"
git -C "$fixture/rebase" cherry-pick --quiet "$first_sha" "$rebase_head"
rebase_terminal="$(git -C "$fixture/rebase" rev-parse HEAD)"
if git -C "$fixture/rebase" merge-base --is-ancestor "$rebase_head" "$rebase_terminal"; then
  echo 'fixture did not rewrite the protected head' >&2
  exit 1
fi

# A reachable terminal with a different last patch is rejected atomically.
printf '%s\n' mismatched > "$fixture/rebase/mismatch.txt"
git -C "$fixture/rebase" add mismatch.txt
git -C "$fixture/rebase" commit --quiet -m mismatched-terminal
mismatched_terminal="$(git -C "$fixture/rebase" rev-parse HEAD)"
cat > "$fixture/rebase-invalid.json" <<JSON
{
  "receiptRef": "receipt:test/rebase-invalid/2",
  "ticket": "ticket-002",
  "outcome": "merged",
  "headSha": "$rebase_head",
  "terminalSha": "$mismatched_terminal",
  "targetBranch": "main",
  "occurredAt": "2026-09-01T20:00:00Z"
}
JSON
rebase_registry="$fixture/rebase/.git/new-project/terminal-receipts.json"
status=0
python3 "$repo_root/scripts/ticket_activity.py" --root "$fixture/rebase" record \
  --receipt "$fixture/rebase-invalid.json" > "$fixture/rebase-invalid.out" \
  2> "$fixture/rebase-invalid.err" || status=$?
test "$status" -eq 2
test ! -e "$rebase_registry"

cat > "$fixture/rebase-valid.json" <<JSON
{
  "receiptRef": "receipt:test/rebase-valid/2",
  "ticket": "ticket-002",
  "outcome": "merged",
  "headSha": "$rebase_head",
  "terminalSha": "$rebase_terminal",
  "targetBranch": "main",
  "occurredAt": "2026-09-01T20:01:00Z"
}
JSON
python3 "$repo_root/scripts/ticket_activity.py" --root "$fixture/rebase" record \
  --receipt "$fixture/rebase-valid.json" > "$fixture/rebase-recorded.json"
status=0
python3 "$repo_root/scripts/ticket_activity.py" --root "$fixture/rebase" resolve \
  --ticket-dir "$fixture/rebase/project/ticket-002" --active-status IN_PROGRESS \
  > "$fixture/rebase-released.json" || status=$?
test "$status" -eq 1
grep -q '"authority": "terminal-receipt"' "$fixture/rebase-released.json"

# A protected squash has one rewritten terminal commit. Verify its aggregate
# patch against the complete protected-head range, including an advanced base.
git -C "$fixture/rebase" switch --quiet -c squash-target "$rebase_target_base"
git -C "$fixture/rebase" merge --quiet --squash delivery
git -C "$fixture/rebase" commit --quiet -m squash-terminal
squash_terminal="$(git -C "$fixture/rebase" rev-parse HEAD)"
mkdir -p "$fixture/rebase/project/ticket-004"
printf '%s\n' '- **Status**: IN_PROGRESS' > "$fixture/rebase/project/ticket-004/README.md"
cat > "$fixture/squash-valid.json" <<JSON
{
  "receiptRef": "receipt:test/squash-valid/4",
  "ticket": "ticket-004",
  "outcome": "merged",
  "headSha": "$rebase_head",
  "terminalSha": "$squash_terminal",
  "targetBranch": "squash-target",
  "occurredAt": "2026-09-01T20:02:00Z"
}
JSON
python3 "$repo_root/scripts/ticket_activity.py" --root "$fixture/rebase" record \
  --receipt "$fixture/squash-valid.json" > "$fixture/squash-recorded.json"
status=0
python3 "$repo_root/scripts/ticket_activity.py" --root "$fixture/rebase" resolve \
  --ticket-dir "$fixture/rebase/project/ticket-004" --active-status IN_PROGRESS \
  > "$fixture/squash-released.json" || status=$?
test "$status" -eq 1
grep -q '"authority": "terminal-receipt"' "$fixture/squash-released.json"

# A merge commit in the original range is not a rebase series, even when its
# terminal SHA is otherwise reachable from the declared target.
git -C "$fixture/rebase" switch --quiet -c nonlinear "$rebase_base"
printf '%s\n' linear > "$fixture/rebase/nonlinear.txt"
git -C "$fixture/rebase" add nonlinear.txt
git -C "$fixture/rebase" commit --quiet -m nonlinear-first
git -C "$fixture/rebase" switch --quiet -c nonlinear-side "$rebase_base"
printf '%s\n' side > "$fixture/rebase/side.txt"
git -C "$fixture/rebase" add side.txt
git -C "$fixture/rebase" commit --quiet -m nonlinear-side
git -C "$fixture/rebase" switch --quiet nonlinear
git -C "$fixture/rebase" merge --quiet --no-ff nonlinear-side -m nonlinear-merge
nonlinear_head="$(git -C "$fixture/rebase" rev-parse HEAD)"
cp "$rebase_registry" "$fixture/rebase-registry-before-nonlinear.json"
cat > "$fixture/rebase-nonlinear.json" <<JSON
{
  "receiptRef": "receipt:test/rebase-nonlinear/3",
  "ticket": "ticket-003",
  "outcome": "merged",
  "headSha": "$nonlinear_head",
  "terminalSha": "$mismatched_terminal",
  "targetBranch": "main",
  "occurredAt": "2026-09-01T20:03:00Z"
}
JSON
status=0
python3 "$repo_root/scripts/ticket_activity.py" --root "$fixture/rebase" record \
  --receipt "$fixture/rebase-nonlinear.json" > "$fixture/rebase-nonlinear.out" \
  2> "$fixture/rebase-nonlinear.err" || status=$?
test "$status" -eq 2
cmp "$rebase_registry" "$fixture/rebase-registry-before-nonlinear.json"

printf '%s\n' 'ticket activity tests passed'
