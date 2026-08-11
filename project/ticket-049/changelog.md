# Ticket Changelog (ticket-049)

## [0.1.0] - 2026-08-11

- Initial governance scaffold created.
- No human participant identity or content was generated.
- Bounded a provenance-preserving initial-adoption variant without changing
  existing-target ownership or the published package.
- Added `fromRevision: null` bootstrap semantics, strict base absence checks
  and hash verification for the complete head managed package.
- Kept pre-existing target files in normal scope and added regressions for
  attempted ownership bypass and a contradictory existing base lock.
- Passed the focused validator and complete Linux CI contract.
