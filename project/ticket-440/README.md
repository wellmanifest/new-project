# Ticket 440: Report adoption-lock failure locations

- **ID**: ticket-440
- **Owner**: agent:codex
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Created**: 2026-11-14

## Goal and authorization

SESSION_EXECUTION_AUTHORIZATION: the request to continue and merge covers the
queued PLF-27170 diagnostic prerequisite. Native admission is free and this
checkout has writer session codex-adoption-failure-locations-20261114-1254, initial fencing1/1.
Implementation stage: 2026-11-14T12:59:23.906641+00:00 to 2026-11-14T13:09:23.906641+00:00, maximum10minutes.

The first slice exposes unexpected fixture failures; the underlying cause of
the earlier hosted discrepancy remains unproven. This ticket does not claim a
repair of that cause. Only tests/adoption-lock.test.sh and this ticket's
carriers are owned. Protected publication remains independent.

## Acceptance criteria

- [x] AC-01: Unexpected top-level and function failures emit a numeric line/status, preserve the original nonzero status and existing cleanup, without printing environment or fixture contents; all existing success-path assertions still pass.
- [ ] AC-02: Native delivery and current-head protected checks pass, followed by independent review and merge.

## Risk and scope

ERR inheritance must retain expected conditional failures and original exit
semantics. Do not remove assertions, increase deadlines, broaden accepted
errors, change production behavior or add dependencies. Raw logs and controlled
fault probes stay in external receipts. No new generation calls are needed.

## Focused validation

Controlled copies injected a top-level failure1 and an internal function
command failure37. Both report the exact failing line, preserve status,
clean the temporary fixture and print no environment or fixture contents.
The complete existing adoption-lock script passes in7.278s with no failure
diagnostic, preserving its expected negative cases. No assertion was removed
or deadline increased. Full native delivery and independent review remain
required. External receipts: forge-polycell-20261113/source-ci-diagnostics.
