# Remediation input validation

- **Status**: IN_PROGRESS
- **Workflow state**: EDIT

## Goal and scope
Reject malformed collection/source shapes with structured diagnostics, require full timestamps with explicit zones, preserve raw input and existing advisory authority.

## Acceptance criteria
- AC-01: Reproduced malformed-input failures and timestamp acceptance become structured rejections; valid plans, zones, exact digest and original raw scope are preserved.
- AC-02: Native, existing integration/wheel/parity and exact-head Linux/Windows/OneDev checks pass.
- AC-03: Independent protected merge and immutable standard 0.20.72 publication are verified.

## Bounds
S / 20 minutes; seven material files, three components, one existing validation contract, no dependencies. Remediation is a standalone managed module and is not newly bundled. No execution authority, frozen-target or foreign work mutations.
