# Physical claim boundaries

- **Status**: IN_PROGRESS
- **Workflow state**: EDIT

## Goal and scope
Reject repeated exact contract/property/signal claims and property-none markers mixed with physical changes for the same contract. Preserve distinct identities, raw input and advisory validation. No hardware execution or effects.

## Acceptance criteria
- AC-01: Actual physical gate and source/bundle regression cases reject conflicts in either order and preserve independent claims.
- AC-02: Native Linux/Windows, existing integration and installed wheel/parity tests pass.
- AC-03: Independent protected merge and immutable standard v0.20.75 publication are verified.

## Bounds
S / 15 minutes; ten material files, three components, one existing physical-intent contract, zero dependencies. No identity normalization, hardware binding/schema identity or foreign/frozen target changes.
