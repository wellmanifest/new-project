# Ticket 314: Reusable CI host audit

- **ID**: ticket-314
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: VALIDATION

SESSION_EXECUTION_AUTHORIZATION: fix pending issues, test, independently publish and merge. A valid pinned reusable contract currently passes required-checks but fails the duplicated host parser. Use the same managed resolver, keep invalid cases fail-closed.

- [x] AC-01: Managed and bundled valid/invalid reusable regressions pass.
- [x] AC-02: Host contract and native gates pass.
- [ ] AC-03: Protected review, merge and published immutable release are observed.

Validation: 25 reusable-check tests passed; agent-hosts.test.sh passed, including managed/bundled path and host boundaries; native governance gate passed. Release projections declare 0.20.87. AC-03 remains pending independent exact-head approval and release.
