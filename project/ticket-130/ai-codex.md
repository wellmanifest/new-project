---
participant-id: agent:codex
participant: codex
role: agent
ticket: ticket-130
---
# Participant: codex (AI agent)

## Understanding

The false drift has two layers: the managed wrapper should not create Python
bytecode, and the overlap checker must treat reproducible nested bytecode as
noise when another direct Python invocation creates it.

## Execution plan

1. Disable bytecode writes in both managed wrapper branches.
2. Extend the exact cache ignore set to nested `__pycache__` paths.
3. Add a fixture proving equal nested cache paths in two worktrees do not
   become an overlap finding, then run the standard gates.

## Actual changes

- Prefixed both managed governance-checker entry points with
  `PYTHONDONTWRITEBYTECODE=1`, so the wrapper cannot dirty an adopter worktree.
- Extended the overlap checker's runtime-noise allowlist to nested
  `__pycache__` directories and added a two-worktree regression fixture.
- Passed the complete Linux shell test matrix, the no-bytecode probe,
  governance validation, adoption-lock validation and `git diff --check`.
- The external Platform artifact inventory still reports its two pre-existing
  catalog/schema findings; none of this ticket's paths are managed entries and
  the build wrote no registry change.

## Blockers

- None inside the recorded intent; proceed without a second confirmation.
- New authority is still required for destructive action, secret access, new
  external coordination or material objective expansion. Protected delivery
  may be invoked without another prompt when publication is in scope; its
  exact-head trusted approval remains independent evidence.
