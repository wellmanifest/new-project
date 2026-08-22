# Ticket Changelog (ticket-106)

## [1.0.0] - 2026-08-22

- Published through `wellmanifest/new-project#174`, approved by the Validator App
  at the frozen head and merged as `1dff15b`.
- Terminal closure created from the integrated default branch.

## [0.2.0] - 2026-08-22

- Added `governance/agent-hosts.json` and its schema as the single source of
  truth for LLM host files, the fail-closed hook and packaging bindings.
- Added `scripts/agent_host_check.py`; `governance_check.py` now runs it, so
  `./project/governance-check.sh` fails when the hook is not actually active.
- `scripts/audit_diagnostics.py` scans `.githooks`, which surfaced the three
  hook codes that had never been registered.
- Registered `GOV-AGENT-HOST-001..006` and `GOV-PACKAGING-001..003` with the
  runbooks `error/GOV-AGENT-HOST.md` and `error/GOV-PACKAGING.md`.
- Extended `tests/agent-hosts.test.sh` with adopter fixtures for every new code.

## [0.1.0] - 2026-08-22

- Initial governance scaffold created.
- No human participant identity or content was generated.
