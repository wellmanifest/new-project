---
participant-id: agent:codex
participant: codex
role: agent
ticket: ticket-084
---
# Participant: codex (AI agent)

## Understanding

Ticket-083 is integrated and closed on
`main@1a715c92a28bde7810dabced4f71a96fbdc00314`, but the latest immutable
package remains `v0.18.0`. A target therefore cannot adopt the scanner fix from
a trusted release. This ticket publishes that already-integrated,
backward-compatible behavior as patch release `0.18.1`; it introduces no new
scanner semantics.

## Execution plan

1. Bind the release to integrated ticket-083 and exactly six release carriers.
2. Commit this governance plan before changing any version carrier.
3. Mechanically synchronize 0.18.0 to 0.18.1 and add release notes.
4. Run focused and complete validation, Ruff and the exact scope gate.
5. Publish through exact-head Validator review and protected merge.
6. Retest clean integrated `main`, publish the immutable tag/release through
   Goal, verify the peeled SHA, then close governance-only.

## Actual changes

- Initialized the bounded ticket and recorded `SESSION_EXECUTION_AUTHORIZATION`
  from the request to execute this work.
- Bound release preparation to integrated ticket-083 and six mechanical
  carriers; implementation is not yet present.
- Synchronized the six carriers from 0.18.0 to 0.18.1 and moved the integrated
  generated-placeholder notes into a dated patch-release section without
  editing scanner semantics.
- Passed all nine Linux suites, required-check parity, JSON/schema checks,
  secret scanning, whitespace validation and canonical Ruff 0.15.21.
- Verified that neither tag nor release `v0.18.1` exists and entered protected
  publication with the ticket still `IN_PROGRESS / PUBLICATION`.
- Committed the mechanical release candidate as
  `08752b1c0eb5ac2a81e42337094980719b2ba92f`; its exact-head source-hub gate
  reports `GOV-PASS`.
- Goal opened PR #132 at exact head
  `301ec3682e12397a509452761dd7ae4eb398f9f3`; hosted Linux/Windows and
  Validator App approved it before merge
  `16f7aea148a7f979e5c5abdfd4bc112224904d36`.
- Verified identical candidate/merge trees, reran 9/9 suites and Ruff 0.15.21
  on clean `main`, and confirmed green post-merge CI.
- Goal direct-main publication created final release `v0.18.1`; annotated tag
  `64f16ef13acfcd8a141654d88ebcd1160785491c` peels exactly to the merge and
  tag-triggered CI passed.
- Created this governance-only closure from the published default branch.

## Blockers

- None; immutable new-project 0.18.1 is published and verified.
- New authority is still required for destructive action, secret access, new
  external coordination or material objective expansion. Protected delivery
  may be invoked without another prompt when publication is in scope; its
  exact-head trusted approval remains independent evidence.
