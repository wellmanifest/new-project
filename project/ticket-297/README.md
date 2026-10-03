# Scope glob directory boundaries

- **Status**: IN_PROGRESS
- **Workflow state**: EDIT

## Goal and scope
Align repository-policy and remediation scope globs with the existing canonical governance segment matcher. A single star/question mark stays within a directory segment; whole-segment recursive stars accept zero or more directories. Preserve standalone module loading, staged snapshot selection, character classes and advisory authority.

## Acceptance criteria
- AC-01: Explicit scope, staged adapter, action-path and canonical conformance regressions deny nested single-star escapes and preserve recursive matches.
- AC-02: Installed wheel/parity, native gate, existing integration and exact-head required CI pass.
- AC-03: Independent protected merge and immutable standard 0.20.71 publication are verified.

## Bounds
S / 25 minutes; ten implementation files, three components, two existing matcher contracts, no dependencies. No new loader, effectful controller, canonical core/Registry/JS matcher changes or foreign/frozen target updates.

Repository-policy has an existing bundled copy. Remediation remains a standalone managed module; no bundled module is introduced.
