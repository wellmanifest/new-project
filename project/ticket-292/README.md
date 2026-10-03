# Canonical scalar lease validation

- **Status**: IN_PROGRESS
- **Workflow state**: EDIT

## Scope
Enforce the existing canonical scalar schema in portable lease, request and receipt validation. Preserve transition reply and trace behavior for a dependent continuation. The original wider prototype and all acceptance work remain externally preserved.

## Acceptance criteria
- AC-01: Scalar reproductions and installed CLI regressions expose the original bugs and pass after correction.
- AC-02: Existing validator integration, parity, native gate and required exact-head CI pass.
- AC-03: Independent protected merge and immutable standard 0.20.66 publication are verified.

## Bounds
S / 25 minutes; thirteen implementation files (including required package and allocator closure), three components, two interfaces (CI and advisory allocation identity), no dependencies. No canonical schema or effectful controller changes.
