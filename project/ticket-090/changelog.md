# Ticket Changelog (ticket-090)

## [0.3.0] - 2026-08-19

- Closed ticket-090 (`DONE / DONE`) from integrated `main` after
  `64017fe8bd3c06dfd7c5f972cf2b6ad9376cb021` (PR #141).
- Post-merge evidence: `GEMINI.md`, `CLAUDE.md`, the Cursor rule, the
  fail-closed hook and `scripts/install-agent-hosts.sh` are on the default
  branch. No implementation files in this closure.
- The ticket stayed `IN_PROGRESS` on `main` after the merge, which made every
  later hub ticket inherit it and fail `GOV-WORKSTREAM-002` and
  `GOV-CONFLICT-001`.

## [0.2.2] - 2026-08-19

- Wire `tests/agent-hosts.test.sh` into hub `ci.yml` so the suite-list gate passes.

## [0.2.1] - 2026-08-19

- Repository-relative paths in `agent-report.json` so `GOV-PATH-001` stays closed.

## [0.2.0] - 2026-08-18

- Added GEMINI.md, CLAUDE.md, Cursor alwaysApply rule, and fail-closed pre-commit hook.
- Added `scripts/install-agent-hosts.sh` for clone and user-level host install.
- Leftover ticket-089 marked DONE after PR #140; `--force-new` recorded.

## [0.1.0] - 2026-08-18

- Initial governance scaffold created.
- No human participant identity or content was generated.
