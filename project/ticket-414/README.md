# Ticket 414: Reject contradictory remaining-work dispositions

- **ID**: ticket-414
- **Owner**: agent:codex
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Created**: 2026-11-06

## Goal and scope

A missing or partial criterion currently becomes ready for owner review when it
has both a discard decision and a follow-up ticket. Require a single consistent
disposition at the existing reconciliation boundary. Preserve digest-bound
receipts, supported single dispositions and the absence of deletion authority.
This resolves finding 0 under artifacts PLF-022 / canonical NP-039.

## Acceptance criteria

- [x] AC-01: Public reconciliation and CLI reject conflicting missing/partial dispositions; supported single dispositions and existing regressions pass without mutating evidence.
- [ ] AC-02: Full native checks and independent exact-head approval precede protected merge.

## Session execution authorization

The user requested continuation, tests and protected merges. The two-file scope
is disjoint from ticket-413. Its author explicitly released real controller
grants before this ticket acquired current fenced editing grants. The original
allocation deadline remains bounded; no timeout transfers ownership.

This source-only slice does not advance immutable version projections. Release
admission remains owned by STARTER-032. Operational receipts and the earlier
blocked-state snapshot are preserved externally; ticket prose grants no approval.

## Validation

The regression failed four assertions before the fix. After the fix, all27
module tests and the native governance gate pass. The public CLI tests check
exit2 and unchanged evidence; positive controls continue to return no authority.
