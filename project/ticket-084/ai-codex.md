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

## Blockers

- None inside the recorded intent; proceed without a second confirmation.
- New authority is still required for destructive action, secret access, new
  external coordination or material objective expansion. Protected delivery
  may be invoked without another prompt when publication is in scope; its
  exact-head trusted approval remains independent evidence.
