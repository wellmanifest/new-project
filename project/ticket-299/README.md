# Continuity stream link boundaries

- **Status**: IN_PROGRESS
- **Workflow state**: EDIT

## Goal and scope
Reject linked/non-regular event stream targets before data access. Anchor POSIX traversal to no-follow directory descriptors; hold Windows no-follow handles without delete sharing. Preserve append-only events, replay, absent reads and advisory authority.

## Acceptance criteria
- AC-01: File/parent symlink, hardlink and substitution regressions leave foreign targets unchanged; actual append/read, existing replay/concurrency and capability boundaries pass.
- AC-02: Native, existing continuity/integration/wheel and exact-head Linux/Windows/OneDev checks pass.
- AC-03: Independent protected merge and standard v0.20.73 publication are verified.

## Bounds
S / 25 minutes; seven material files, three components, one existing continuity I/O contract, zero dependencies. No stream/index schema or historical data changes; no new bundled module; no effectful controller or foreign/frozen target changes. This does not claim resistance to arbitrary same-user concurrent mutations beyond the tested descriptor/path boundaries.
