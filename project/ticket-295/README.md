# Complete local agent source links

- **Status**: IN_PROGRESS
- **Workflow state**: EDIT

## Goal and scope
Require the complete local source set for the selected canonical hub or adopter contract. Missing manifests must not cause layout fallback. Reject missing, omitted, symlinked or escaping applicable source files and preserve complete layouts, inactive-layout optional files and the result shape.

## Acceptance criteria
- AC-01: Hub/adopter completeness and containment regressions reproduce prior acceptance and preserve valid layouts.
- AC-02: Agent-host integration, installed wheel/parity, native gate and required exact-head CI pass.
- AC-03: Independent protected merge and immutable standard 0.20.69 publication are verified.

## Bounds
S / 25 minutes; eight implementation files, three components, one optional helper-context interface, no dependencies. Remote links remain navigation only. No bootstrap copying, effectful controller, remote deployment or foreign/frozen target changes.
