# ticket-395: Fence integrated-worktree branch cleanup

- **ID**: ticket-395
- **Owner**: agent:codex
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION

SESSION_EXECUTION_AUTHORIZATION: the user requested execution, fixes, tests and
protected merge. This new native allocation explicitly names agent:codex and
this session; no foreign checkout is taken over. Session prose grants no
trusted review or merge approval.

## Goal and scope

The legacy cleanup helper forces branch deletion after any ordinary deletion
failure and relies on an earlier branch snapshot. Preserve declined operations
and concurrent ref changes, check live integration state, and remove only the
exact observed branch tip. Keep target checkouts, ignored data and unrelated
worktree metadata intact. Join material patch0.20.125.

## Acceptance criteria

- [x] AC-01: Normal integrated cleanup succeeds; failed/ref-changed branch
  cleanup retains the current branch and never invokes forced deletion.
- [x] AC-02: Target checkout, dirty/ignored data and unrelated registrations
  remain intact; all destructive regression effects stay in disposable repos.
- [ ] AC-03: Version projections, full native health, root tests and exact-head
  CI pass; independent protected approval governs merge and immutable release.

## Delivery boundary

Seven material files in two components; no new dependency or public interface.
Implementation is bounded to30 minutes with a checkpoint by25. Preserve the
separate393 scope. Raw logs, Git race probes, snapshots and controller receipts
stay outside Git. Keep IN_PROGRESS / PUBLICATION until the protected terminal
receipt; use native Goal and C-PUBLISH-007 for the resulting immutable release.

Validation: five controlled regressions failed against the original helper.
All eight tests now pass, including before/after-removal ref changes, target
changes, rejected deletion, ignored data and unrelated registration retention.
The exact-ref Git transaction was also proved in a separate disposable repo.
A further controlled red/green case proves that a symbolic-ref race cannot
redirect deletion to an unrelated ref; the transaction disables dereferencing.
Native health, root tests, protected CI/review and publication remain pending.

Refinement: a changed symbolic alias with the same commit OID is now retained
along with its unrelated referent. The transaction prepares both locks, verifies
direct reference types under those locks, and commits only the unchanged refs.
The strengthened case failed on3a988336 and all eight regressions now pass.
