# Agent host and package gate path boundaries

- **Status**: IN_PROGRESS
- **Workflow state**: EDIT

## Goal and scope
Make the declared repository-relative path constraint reject parent traversal, absolute and drive-qualified paths. Reject package gate paths outside the checkout and gates reached through symbolic links. Preserve valid hub/adopter declarations and the existing finding shape.

## Acceptance criteria
- AC-01: Schema/path regressions reproduce prior acceptance and deny forbidden paths while preserving valid declarations.
- AC-02: Agent-host integration, installed wheel/parity, native gate and required exact-head CI pass.
- AC-03: Independent protected merge and immutable standard 0.20.68 publication are verified.

## Bounds
S / 25 minutes; nine implementation files, three components, one existing schema constraint interface, no dependencies. Source-link completeness and bootstrap copying are separate continuations; no effectful controller, remote deployment or foreign/frozen target changes.
