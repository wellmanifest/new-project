# Unambiguous Git branch-name boundaries

- **Status**: IN_PROGRESS
- **Workflow state**: EDIT

## Goal and scope
Reject branch names Git cannot use, consistently in the intent schema, runtime and existing installed bundle. Preserve valid Unicode and punctuation; reserve standalone @ because its unqualified revision meaning is HEAD even when refs/heads/@ names a different literal branch. No runtime Git subprocess or new dependency.

## Acceptance criteria
- AC-01: Source, bundle and schema acceptance match actual read-only Git branch validation on explicit valid/invalid names; malformed scalars are rejected. Standalone @ is a separate explicit policy restriction, not a fabricated Git syntax rejection.
- AC-02: Existing branch lifecycle, native, wheel/parity, validator integration and exact-head Linux/Windows/OneDev checks pass.
- AC-03: Independent protected merge and standard v0.20.74 publication are verified.

## Bounds
S / 15 minutes; nine material files, three components, one existing branch-name contract, zero dependencies. No branch allocation/effect authority, physical change/catalog/workflow parser changes or foreign/frozen target mutations.
