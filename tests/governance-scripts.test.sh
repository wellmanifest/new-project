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

set +e
(
  cd "$fixture"
  bash project/new-ticket.sh --title 'Missing workstream' > missing-workstream.out 2> missing-workstream.err
)
status=$?
set -e
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

set +e
(
  cd "$fixture"
  bash project/new-ticket.sh --title 'Must reuse active ticket' --agent codex --workstream application \
    > second.out 2> second.err
)
status=$?
set -e
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

set +e
(
  cd "$fixture"
  T2C_TICKET_INDEX_FILE='../outside.md' bash project/readme.sh > /dev/null 2> traversal.err
)
status=$?
set -e
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
  set +e
  (
    cd "$fixture"
    # shellcheck disable=SC2086
    bash project/new-ticket.sh --title 'Rejected classification' --workstream interfaces $mutation \
      > mutation.out 2> mutation.err
  )
  status=$?
  set -e
  test "$status" -eq 1
  grep -q 'GOV-CLASS-001' "$fixture/mutation.err"
  test "$(count_tickets)" -eq "$tickets_before"
done

# Without the contract there is nothing to validate against, and guessing would
# defeat the point; the scaffolder must say so rather than emit an unchecked value.
mv "$fixture/.governance/work-classification.dsl.json" "$fixture/work-classification.dsl.json.bak"
set +e
(
  cd "$fixture"
  bash project/new-ticket.sh --title 'No contract' --workstream interfaces \
    > nocontract.out 2> nocontract.err
)
status=$?
set -e
test "$status" -eq 1
grep -q 'GOV-CLASS-000' "$fixture/nocontract.err"
test "$(count_tickets)" -eq "$tickets_before"
mv "$fixture/work-classification.dsl.json.bak" "$fixture/.governance/work-classification.dsl.json"

echo 'governance scripts: PASS'
