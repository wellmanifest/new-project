# Ticket 197: Managed github-script v9

- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Owner**: codex

SESSION_EXECUTION_AUTHORIZATION: User requested continuation and implementation of the remaining managed workflow dependency update. Publish this standard-owned change before adopters receive it.

## Acceptance criteria
- [ ] AC-01: Managed adopter workflow and hub workflows use verified github-script v9 commit 3a2844b7e9c422d3c10d287c895573f7108da1b3, preserving existing script semantics and permissions.
- [ ] AC-02: Version 0.20.13 and fixtures agree; adoption and governance tests plus Linux/Windows CI pass before independent protected publication.

Local verification: adoption-lock, agent-hosts and governance-validator suites passed. Existing script usage remains compatible with v9; no @actions/github CommonJS imports occur. The manifest counts the already-declared hub CI workflow as one public-interface path; the delivery budget records that classification.
