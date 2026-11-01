# ticket-396: Preserve adoption workflow and repository bindings

- **ID**: ticket-396
- **Owner**: agent:codex
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT

SESSION_EXECUTION_AUTHORIZATION: the user requested execution, testing, fixes
and protected merge. Native allocation explicitly names this actor/session;
no foreign work is taken over. Session prose is not trusted review evidence.

## Goal and scope

The current workflow generator confuses sibling event activity types and raw
comment text with the pull_request trigger. Registered allocation also merges
distinct SSH principals and server ports into one repository reference. Fix
these two reproduced input-binding errors with bounded literal parsing and
authority-preserving normalization; join material patch0.20.126.

## Acceptance criteria

- [ ] AC-01: Workflow checks bind only the actual PR trigger and its types;
  source/runtime parity, common forms and closed-only exclusion are tested.
- [ ] AC-02: Distinct SSH users and ports stay distinct, ordinary aliases stay
  stable, and ambiguous or credential-bearing origins reject safely.
- [ ] AC-03: Native health, root tests, version parity and exact-head CI pass;
  independent protected approval controls merge and immutable publication.

## Delivery boundary

Ten material files in three components; no new dependency or public signature.
Source work is bounded to30 minutes with checkpoint by25. Preserve393 and all
unknown/foreign work. Raw tests and controller receipts stay outside Git.
Keep IN_PROGRESS / PUBLICATION until the protected terminal receipt.
