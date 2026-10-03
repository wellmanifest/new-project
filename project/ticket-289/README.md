# Canonical URLs for captured Registry runtime

- **Status**: IN_PROGRESS
- **Workflow state**: EDIT

## Goal and scope
Use Node canonical file URLs consistently for captured sources and the entry while preserving independent digest pins, closed module loading, stdin and argv. This dependent ticket completes ticket-288's explicitly deferred Registry Windows correctness and CI wiring.

## Acceptance criteria
- AC-01: Real Node integrity regressions, including a tilde/Unicode/percent/hash root, pass; the new path case fails on the original runtime.
- AC-02: Native governance and required Linux, Windows and OneDev checks pass for the exact head.
- AC-03: Independent protected merge and immutable standard v0.20.63 release are verified through managed Goal.

## Risks and limits
S / 25 minutes, eight implementation files, three components, one workflow interface path and no new runtime dependencies. Captured source bytes remain independently pinned. No unverified module source is reopened by pathname. Raw test streams and controller receipts remain external.
