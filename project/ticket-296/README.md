# Deterministic decision replay

- **Status**: IN_PROGRESS
- **Workflow state**: EDIT

## Goal and scope
Replay only the supported check-gate rules. Reject author-supplied results for unimplemented rules and invalid required checks. Derive defaults from local hub/adopter metadata without inventing observed PASS; denied evaluations remain denied. Preserve supported aliases, result codes and the independent publication boundary.

## Acceptance criteria
- AC-01: Regressions reproduce unsupported-rule acceptance and default path defects, preserving valid supported replay and derivation.
- AC-02: Decision-record tests, installed wheel/parity, native gate, existing validator integration and exact-head required CI pass.
- AC-03: Independent protected merge and immutable standard 0.20.70 publication are verified.

## Bounds
S / 25 minutes; eight implementation files, three components, one existing replay contract, no dependencies. No arbitrary policy engines, protected approval/controller changes, historical record rewrites or foreign/frozen target updates. Local records and replay remain advisory.
