# Ticket Changelog (ticket-114)

## [0.2.0] - 2026-08-23

- Added `scripts/fleet_report.py`, a read-only workspace tool that reports each
  adopter's adopted version, releases behind the published standard, managed
  digest drift, whether CI runs the gate, whether the host contract is present
  and whether the required-checks declaration is truthful.
- Classifies three states, separating "follows the standard without an adoption
  lock" from "outside the standard".
- `--max-releases-behind` turns the report into a gate.

## [0.1.0] - 2026-08-23

- Initial governance scaffold created.
- No human participant identity or content was generated.
