---
participant-id: agent:codex
participant: codex
role: agent
ticket: ticket-055
---
# Participant: codex (AI agent)

## Understanding

The `project.sh` wrapper already delegates to `goal governance check`, and Goal
correctly executes the target's pinned validator. The defect is inside that
validator: without `--base` it computes only working-tree paths, but atomic
adoption requires a base and a changed lock. A committed plan followed by a
committed adoption therefore fails even though the accepted base is already
recorded in the active ticket.

## Execution plan

1. Resolve an omitted base from the accepted SHA of exactly one active
   standard-adoption ticket before calculating changed paths.
2. Keep explicit `--base` authoritative and retain fail-closed behavior for
   malformed or multiple active adoption records.
3. Split the adoption fixture into base, plan and payload commits, then verify
   both inferred-base and explicit-base execution.
4. Run the focused and complete Linux contracts, integrate the tested commit
   into the pinned pilot candidate and repeat the isolated `codot` gate.

## Actual changes

- Initialized the bounded ticket and recorded `SESSION_EXECUTION_AUTHORIZATION`
  from the request to execute this work.
- Reproduced the defect in `semcod/codot`: explicit Goal validation passed,
  while no-argument `./project.sh` returned `GOV-SYNC-001` because the committed
  lock was invisible without a base.
- Confirmed the wrappers already use Goal and that the correct repair boundary
  is the pinned `new-project` validator rather than a shell-side JSON parser.

## Blockers

- None inside the recorded intent; proceed without a second confirmation.
- New authority is still required for destructive action, secret access, new
  external coordination, material objective expansion and trusted merge.
