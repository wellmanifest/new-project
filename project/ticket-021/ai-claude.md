---
participant-id: agent:claude
participant: claude
role: agent
ticket: ticket-021
---
# Participant: claude (AI agent)

## Understanding

The scaffolder used an incomplete view of ticket allocation and did not prevent
multiple writers from sharing one worktree. Preserve foreign work, serialize
allocation across linked worktrees and keep generated intent aligned with v3.

## Execution plan

1. Emit and validate intent/v3 classification.
2. Scan local and fetched remote refs before allocating a number.
3. Reserve numbers under a clone-wide lock and shared high-water mark.
4. Exclude untracked foreign tickets from the generated index.
5. Add governance rules and regression coverage for concurrent writers.

## Actual changes

- Implemented the v3 scaffolder and contract-driven classification validation.
- Added clone-wide allocation serialization and persistent local reservations.
- Added single-writer worktree rules and regression coverage.

## Blockers

- Independent clones still require fresh remote refs; local state cannot provide
  a distributed lock across machines.
