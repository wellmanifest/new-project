# ticket-186: Reconcile branch intent before unmerged discard

- **ID**: ticket-186
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION

## Outcome
Require preserved history, complete criterion-level reconciliation and separate owner authorization before discarding unmerged work. Report validity never grants deletion or merge authority.

## Acceptance criteria
- [x] AC-01: Closed report validation binds source/target SHA, intent digest and all expected criteria; missing and stale evidence fail closed.
- [x] AC-02: Agent instructions and managed package ship the procedure and validator without modifying another active ticket.
- [ ] AC-03: Positive and adversarial regressions and managed governance pass; protected publication retains exact-head approval.
