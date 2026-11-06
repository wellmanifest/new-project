# Ticket 413: Validate in-place host activation paths

- **ID**: ticket-413
- **Owner**: agent:codex-maskservice-np032
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Created**: 2026-11-06

## Goal and scope

Deliver NP-041, the first bounded slice of NP-032. Reuse the canonical bootstrap
validator to reject unsafe in-place host/hook/runtime declarations and directory
mismatches before any activation effect. Preserve valid hub/adopter activation,
additional hooks and all independent publication boundaries. Material version
0.20.142 accompanies the fix. NP-042 separately owns continuity transactions.

## Acceptance criteria

- [x] AC-01: Seven malformed path/alias/mismatch fixtures reject before chmod/config changes; valid controls and existing host tests pass.
- [ ] AC-02: Native source tests and governance pass; genuine Goal publication and independent exact-head review precede merge/release.

## Session execution authorization

The user requested autonomous continuation, fixes, tests and protected merges.
Existing NP-032 explicitly permits bounded splitting. Source412/PR585 was
independently merged and its actual controller grants released before allocation.
No foreign checkout is changed. Raw proofs and fencing remain in the external
continuation checkpoint; no agent-authored prose grants approval authority.

## Validation

Eight original unsafe cases were reproduced before the fix. All11in-place
positive/negative fixtures now pass, followed by the complete existing host
suite. Source changes reuse canonical bootstrap path validation; no runtime
dependency, publication policy or consumer copy was changed. Independent
current-head review remains required for AC-02.
