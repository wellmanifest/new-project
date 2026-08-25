---
schema: new-project.agent-participant/v1
agent: codex
ticket: ticket-118
---
# Participant: codex

## Understanding

Ticket-117 is integrated and closed, but its managed worktree guard is not in
the latest immutable release. Platform cannot safely adopt an unpublished SHA.

## Plan

1. Record the bounded release contract before implementation.
2. Bump only canonical release carriers from 0.18.6 to 0.18.7.
3. Run focused overlap, adoption-lock and governance validation.
4. Publish through exact-head Validator review and explicit merge.
5. Create the annotated tag and final GitHub Release only on trusted main.
