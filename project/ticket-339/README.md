# Ticket 339: Locked legacy scaffold migration

- **ID**: ticket-339
- **Owner**: agent:codex
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION

## Goal and scope

SESSION_EXECUTION_AUTHORIZATION: the user requested continued repairs, testing and protected publication across Maskservice with Wellmanifest, SSOT and NoHardcode. This maintenance ticket owns only the canonical migration mechanism. Product evidence and target tickets remain outside the hub.

## Acceptance criteria

- [x] AC-01: Explicit migration accepts the exact committed legacy seven-file registration; refuses native locks, changed bytes, extended shape, duplicates and symlinks without writes.
- [ ] AC-02: Existing digest-bound future reusable plans work with scaffold migration, preserving actual workflow bytes and required-check failure until implementation; real first allocation and protected publication succeed.

## Validation

Affected pytest run: 59 tests and 76 subtests passed. The original Testless report rejected JUnit subtest metadata; a fresh scoped scan of four actual integration tests passed and collected valid outcomes. The added prewrite recheck and final tamper/refusal matrix passed separately. Native governance and diff checks pass. Exact-head OneDev and independent Validator approval/merge remain required before immutable publication.
