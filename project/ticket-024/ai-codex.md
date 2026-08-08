---
participant-id: agent:codex
participant: codex
role: agent
ticket: ticket-024
---
# Participant: codex (AI agent)

## Understanding

The target governance manifest is seeded but currently included in the
adoption lock as if its entire content were managed. A target therefore cannot
add truthful local ownership without either breaking `GOV-SYNC-001` or editing
the protected lock. The existing ticket-024 is the correct owner for a bounded
`extendable` package strategy.

## Execution plan

1. Add an `extendable` JSON entry for the target manifest and a separately
   managed standard base to the package manifest.
2. Implement one deterministic structural extension/three-way merge algorithm
   in the adoption tool, preserving target-only object keys and array items.
3. Make governance synchronization verify both the base hash and recursive
   preservation of every base requirement in the target manifest.
4. Add positive adoption/upgrade fixtures and negative altered/removed-base
   fixtures, including a todo2code-shaped target ownership case.
5. Run the two declared suites, the full Linux governance contract, and leave
   target migration and release publication to dependent tickets.

## Actual changes

- Planning and delivery contract only.
- No implementation change before explicit ticket-024 approval.

## Blockers

- Explicit approval of this expanded ticket-024 plan is required before EDIT.
