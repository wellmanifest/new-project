# Ticket Changelog (ticket-110)

## [0.2.0] - 2026-08-23

- Composed ticket lifecycle success with the repository worktree guard.
- Made the hook runtime an explicit, schema-validated part of the host contract
  and its atomic bootstrap.
- Added deterministic coverage for both success paths, guard rejection and
  missing-runtime failure; all ten shell suites pass fail-fast.

## [0.1.0] - 2026-08-22

- Initial governance scaffold created.
- No human participant identity or content was generated.
- Recorded the plan, bounded two implementation files, and captured the
  managed-hook composition regression before changing executable code.
- Expanded the plan before implementation after the first fixture proved that
  host bootstrap copied the hook without the runtime it now needs.
- Corrected the estimate to the schema ceiling and made the full-suite command
  fail-fast after observing that a plain shell loop can mask an earlier test
  failure with the last test's success.
- Split the planned managed payload from the hub's live hook after the new
  guard correctly exposed old dirty worktrees that cannot be removed without
  their owner's decision.
