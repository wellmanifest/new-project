# Ticket 194: Reliable publication guards

- **Owner**: codex
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION

SESSION_EXECUTION_AUTHORIZATION: user requests continuation, implementation, deployment, tests and GitHub publication of the diagnosed publication safeguards.

## Acceptance criteria

- [x] AC-01: Pending imports identical to current origin/main do not create false overlap; local edits, unresolved paths and untrusted merge heads remain guarded.
- [ ] AC-02: Managed commits validate the immutable local pin without invoking the latest-release updater; corrupted pins remain blocked. Publish version 0.20.12 with passing governance and package tests.

## Risks

Git read failures retain conservative overlap behavior. Explicit adoption remains available and protected review is required for publication.

Validation: all seven targeted suites and full Goal source-hub health passed (37 JSON documents, 16 shell suites). Legacy-worktree reconciliation is preserved in the clone-external ticket-194 recovery receipts.
