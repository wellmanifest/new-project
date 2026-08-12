# Ticket Changelog (ticket-073)

## [0.1.0] - 2026-08-12

- Initial governance scaffold created.
- No human participant identity or content was generated.
- Recorded the real todo2code projection and repository-wide correlation
  regressions, bounded architecture, acceptance criteria and validation plan.
- Corrected the allocator-supplied workstream to the current hub manifest's
  `governance` integration boundary before any implementation commit.
- Serialized the independently published ticket 069, closed superseded PR #109
  without losing local work, and refreshed the approved base to the integrated
  governance-only closure `5b7ce13` before replaying implementation.
- Added the todo2code graph digest and projection record IDs to the bounded
  advisory data contract before implementation.
- Implemented atomic one-record-per-action projections, declared-path writes,
  byte verification and graph-record-scoped todo2code analysis.
- Added `GOV-REMEDIATION-004`, `C-REMEDIATION-005`, adopted agent guidance,
  runbook instructions and regression coverage.
- Verified the full shell contract, Ruff and a real todo2code 0.5.1 run against
  `goal/ticket-055`; unrelated repository history no longer enters the overlay.
- Closed the lifecycle after PR #111 passed required checks, received trusted
  exact-head Validator App approval and merged as `b50b581`; its tree matched
  the approved payload, post-merge CI passed and the remote branch was deleted.
