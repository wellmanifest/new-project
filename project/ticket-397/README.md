# ticket-397: Reject ambiguous governance import inputs

- **ID**: ticket-397
- **Owner**: agent:codex
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT

SESSION_EXECUTION_AUTHORIZATION: the user requested execution, testing, fixes
and protected merge. Native allocation explicitly names this actor/session;
no foreign checkout is taken over. Chat prose is not trusted review evidence.

## Goal and scope

Snapshot inventory currently overwrites a duplicate Git path in its map.
Host bootstrap also accepts source/target traversal and destination symlinks.
Both were reproduced using synthetic data in newly created private fixtures.
Reject ambiguous inventory and contain bootstrap paths before copy effects;
preserve normal behavior and join material patch0.20.127.

## Acceptance criteria

- [ ] AC-01: Duplicate or unreadable inventory paths reject with typed errors
  in source and bundle; valid migration proofs remain accepted.
- [ ] AC-02: Unsafe host-package paths reject before destination/config writes;
  valid bootstrap, additional hooks, read-only checks and hardlink preservation
  are covered by real isolated fixtures.
- [ ] AC-03: Native health, root tests, version parity and exact-head CI pass;
  independent protected approval controls merge and immutable publication.

## Delivery boundary

Ten material files in three components; no new runtime dependency or public
signature. Source work is bounded to30 minutes with checkpoint by25. Preserve
foreign393 and unknown work. Raw traces and controller receipts stay external.
Keep IN_PROGRESS / PUBLICATION until the protected terminal receipt.
