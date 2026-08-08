---
participant-id: agent:codex
participant: codex
role: agent
ticket: ticket-043
---
# Participant: codex (AI agent)

## Understanding

Ticket-042 repaired a protected acquisition regression and merged as
`main@b01cae0f47bb311d1e795600af49e0ba436e175d`. Its strict validator and
snapshot schema did not change. A patch release is required because downstream
policy accepts only immutable full-SHA standard revisions.

## Execution plan after approval

1. Advance VERSION, default manifest, changelog and exact version assertions to
   0.13.2 without changing ticket-042 behavior.
2. Run the full Linux contract and protected PR checks.
3. Require current-head Validator App approval and merge.
4. Revalidate the clean merge commit, create an annotated tag and GitHub
   Release, and verify both peel to the exact commit.
5. Resume todo2code ticket-050 on that immutable SHA.

## Actual changes

- None; planning only.

## Blockers

- The user's 2026-08-08 approval explicitly covered this separate immutable
  publication step. It will be recorded in a distinct transition before edits.
