# Ticket Changelog (ticket-074)

## [0.1.0] - 2026-08-12

- Initial governance scaffold created.
- No human participant identity or content was generated.
- Recorded bounded scope for repository modes, opt-in Docker, delivery profiles
  and workflow-state correction.
- Added backward-compatible standalone/monorepo manifest semantics and
  deterministic monorepo component-root enforcement.
- Added closed XS/S/M/L delivery profiles with exact-profile budget selection.
- Made Docker bootstrap/runtime conditional while preserving immutable checks
  for Docker configuration that already exists.
- Updated normative and agent projections and corrected the workflow-state
  transition from `BLOCKED` to `EDIT`.
- Passed manifest/intent metaschemas, all Linux test suites, rule traceability,
  diff checks and the source-hub governance gate.
