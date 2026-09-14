# Ticket 230: Batch activity reads during worktree inspection

- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Created**: 2026-09-14
- **Workstream**: governance
- **Issue**: https://github.com/wellmanifest/new-project/issues/352

## Outcome and acceptance

- [x] AC-01: Existing activity and overlap fixtures preserve authority decisions.
- [x] AC-02: Batch reads reduce subprocesses and reject changed inputs; later invocations observe new work.
- [ ] AC-03: Publish the material fix with matching release projections through Goal and independent review.

## Plan

Use one checkout-scoped read batch, revalidate its mutable inputs before accepting results, and discard all cached data after the call. Test historical ticket load, independent clones, registry and ref changes, and subsequent invocation freshness. No persistent cache or relaxed gate. Preserve unrelated dirty work and all historical worktrees.

Raw evidence: host audit activity-batch-230-20260914. Canonical findings and reproducible validation belong in docs/information/ticket-activity-batching.md. Planfile PLF-011 records the existing issue intake; it grants no mutation authority.
