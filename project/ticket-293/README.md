# Transition input and rejected trace safety

- **Status**: IN_PROGRESS
- **Workflow state**: EDIT

## Goal and scope
Reject malformed transition documents with stable diagnostics and no fabricated receipt. A rejected receipt preserves its own revision, fence and phase and remains anchored to the preceding accepted lease identity/state. Only accepted transitions advance that trace anchor. Reuse the canonical scalar validation and installed package closure from ticket-292.

## Acceptance criteria
- AC-01: Current malformed input and rejected trace reproductions expose the bugs, then portable safety regressions pass.
- AC-02: Existing validator integration, installed wheel/parity, native gate and required exact-head CI pass.
- AC-03: Independent protected merge and immutable standard 0.20.67 publication are verified.

## Bounds and risks
S / 25 minutes; nine implementation files, three components, one malformed-input CLI interface, no new dependencies. No canonical schema, allocated identity or effectful Subactor controller changes. Raw logs and controller receipts stay external.
