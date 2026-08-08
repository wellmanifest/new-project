---
participant-id: agent:codex
participant: codex
role: agent
ticket: ticket-037
---
# Participant: codex (AI agent)

## Understanding

Ticket-036 is complete on protected `main`, but its new default ownership rules
are not part of immutable `v0.11.0`. Consumers need a new release whose version,
manifest, changelog, tests, tag, GitHub Release and full source SHA agree.

## Execution plan

1. After explicit approval, transition to `IN_PROGRESS / EDIT`.
2. Change only the five approved release metadata and assertion files.
3. Run the full Linux CI contract and publish a ticket-scoped PR.
4. Require protected Linux/Windows checks and exact-head Validator approval.
5. Merge, then test the exact merge SHA in a clean detached checkout.
6. Confirm `v0.12.0` and its Release are absent.
7. Create a new annotated tag and GitHub Release for that exact SHA.
8. Verify the peeled tag commit, Release target and remote branch cleanup.

## Actual changes

- User approved implementation and publication on 2026-08-08; ticket moved to
  `IN_PROGRESS / EDIT` before release-file changes.
- Updated the five approved release files from 0.11.0 to 0.12.0.
- Closed the release changelog with the root ownership and adoption behavior.
- Focused version/adoption tests and the complete Linux CI contract pass.
- Ticket moved to `VALIDATION`; protected Windows, review, merge checkout and
  publication evidence remain pending.

## Blockers

- Downstream adoption remains in todo2code ticket-050.
- Protected PR validation, clean merge-SHA validation and publication remain.
