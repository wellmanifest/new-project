# Ticket 222: Bounded allocator scope and SQLite admission

- **ID**: ticket-222
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Created**: 2026-09-13
- **GitHub Issue**: https://github.com/wellmanifest/new-project/issues/330 (AC-03 slice)

SESSION_EXECUTION_AUTHORIZATION: The owner requested continuation of repairs and protected publication, and explicitly accepted the one-shot allocator copy forwarding the exact five repair paths without disabling admission, WIP, conflict or ID locking checks. Ticket-220 is independently merged via PR333; fresh admission permits this new slice. No handoff or editing of that completed ticket is needed.

## Goal and scope

Accept repeatable explicit implementation paths at allocation. Validate them against the declared workstream before reserving an ID, pass them to the live work-start checker, and retain them in file and SQLite intent. Preserve conservative no-path behavior and every existing effect boundary.

## Acceptance criteria

- AC-01: Disjoint inactive work permits a scoped allocation; overlap, WIP saturation, malformed/unowned/tracking-only paths and missing scope runtime fail without allocating. File and SQLite intents retain admitted paths.
- AC-02: Real Registry interop and file-mode tests pass, including unique IDs across linked worktrees after explicit release of prior reservations. Managed governance and independent exact-head publication pass.

## Risks and limits

A narrow query must never become authority for broader implementation. Source ownership uses the canonical coverage predicate, not a duplicated permissive matcher. Omitted scope remains conservative. No release or unrelated registration-validator fix belongs to this slice.

## Validation

The new disjoint-scope regression failed before implementation with `Unknown option: --path`. After the change, the work-start suite passed 27 tests and the independently pinned real Registry interop suite passed all 8 tests (no integration skip). The governance-scripts and governance-validator suites passed, as did shell syntax, diff whitespace and the managed agent governance check. Required remote checks and independent exact-head approval remain publication boundaries; these local results grant neither merge nor execution authority.
