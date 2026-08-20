---
participant-id: agent:codex
participant: codex
role: agent
ticket: ticket-096
---
# Participant: codex (AI agent)

## Understanding

During an adoption in `subactor/core`, the authoritative full pre-commit hook
ended with `exit 0`. The worktree installer appended its fragment after that
line, so the new guard could never run. Existing tests cover only a repository
without a pre-commit hook and therefore did not exercise composition with the
standard's own full hook.

## Execution plan

1. Commit the bounded accepted-base plan before implementation.
2. Add a regression fixture with an existing terminal-success hook and prove
   the current installer accepts a conflicting commit.
3. Update the installer to insert immediately before only a final effective
   `exit 0`; preserve append-last behavior for every other existing hook.
4. Run the focused suite, full governance contract and exact-base gate, then
   publish through exact-head Validator review.

## Actual changes

- Initialized the bounded ticket and recorded `SESSION_EXECUTION_AUTHORIZATION`
  from the request to execute this work.
- Bound the repair to integrated base
  `358f7b40d51bb205ffe4cc93e25c3d07cc9e0682` and the reproduced Core
  composition failure.
- Added a terminal-success regression to the existing real-commit fixture; it
  failed before the repair and now proves a conflicting commit is rejected.
- The installer finds only the final effective command `exit 0` and inserts
  the chain immediately before it. Other hooks keep append-last behavior;
  repeated installation remains idempotent.
- Bash syntax, exact-base governance, the focused fixture and all eleven Linux
  shell suites pass. Publication now waits for hosted Linux/Windows and the
  independent exact-head Validator boundary.

## Blockers

- None inside the recorded intent; protected publication is in progress.
- New authority is still required for destructive action, secret access, new
  external coordination or material objective expansion. Protected delivery
  may be invoked without another prompt when publication is in scope; its
  exact-head trusted approval remains independent evidence.
