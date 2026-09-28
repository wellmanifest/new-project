# ticket-278: Verify unchanged snapshot imports without granting repair ownership

- **ID**: ticket-278
- **Owner**: agent:codex
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT

## Scope and authorization

SESSION_EXECUTION_AUTHORIZATION: user authorized the missing recovery mechanism
and independent review in New-project, Validator and OneDev on 2026-09-28.
This bounded slice owns import/repair accounting and its published projection.
Allocator reservation/materialization and immutable release are dependent slices;
their owned prototype is preserved outside this delivery, without authority.

## Acceptance criteria

- AC-01: Only paths validated as unchanged against an externally pinned exact
  snapshot grant count as historical context. Changed imports and new repairs
  retain ordinary scope, ownership, budget and chronology checks.
- AC-02: Import-only delivery still selects its current migration ticket and
  requires the normal independent exact-subject approval. Ordinary candidates
  without a valid migration proof gain no exception. Real Git regressions and
  the full governance suite pass.

## Boundary

No grant issuance, consumption, allocator effects, runtime deployment or history
rewrite in this slice. The standard gate required partitioning the original large
plan into dependent XS/S deliveries; no policy limit is expanded.
