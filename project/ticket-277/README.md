# Ticket 277: Preserve unrelated dirty primary state during isolated ticket allocation

- **ID**: ticket-277
- **Owner**: agent:codex
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Utworzono**: 2026-09-27

## Cel i Zakres

Allow canonical file-backed allocation from a dirty primary checkout only when
an explicit bounded scope passes the existing work-start admission. Preserve
unrelated worktree and index changes byte-for-byte. Continue rejecting scope
conflicts, missing admission, unsafe placement and unscoped dirty allocation.
This repairs an allocator defect preventing isolated product maintenance.

SESSION_EXECUTION_AUTHORIZATION: the user requested continued source repair,
autonomy pilots and tests on 2026-09-27. This bounded prerequisite fixes the
allocator at its HOME; adopter packages and protected publication are unchanged.

## Kryteria Odbioru (Acceptance Criteria)

- [x] AC-01: Disjoint scoped allocation preserves tracked, staged and untracked
  primary changes and creates the ticket from the committed target revision.
- [x] AC-02: Overlapping or unscoped dirty allocation fails before reservation.
- [x] AC-03: Canonical placement and managed governance checks still pass.

## Ryzyka i Uwagi

The clone allocation lock does not grant ownership of another writer's changes.
Use the mandatory work-start admission and an explicit scope; do not add a force
option or stage, reset, clean or stash the primary checkout.

## Granica katalogu

Bounded intent only. Source and tests live in their canonical directories;
private checkpoint receipts are stored in ignored recovery storage.

## Validation

Six canonical allocation integration tests pass, including disjoint primary
preservation and rejection without reservation. The governance-scripts suite,
55 work-start tests, managed governance and whitespace checks pass locally.
Protected exact-head verification and independent merge remain pending.
