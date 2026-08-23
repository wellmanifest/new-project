# Ticket Changelog (ticket-112)

## [0.2.0] - 2026-08-23

- Added `scripts/generate_required_checks.py`, distributed to adopters as
  `.governance/generate_required_checks.py`, which derives the required-checks
  declaration from the job names a repository's own workflows publish.
- Reports by default; `--write` refuses a repository whose names cannot be
  fully derived, which is the case wherever a job calls a reusable workflow.
- `tests/required-checks.test.sh` covers trigger keys, callers, the write
  refusal and circular exclusions.

## [0.1.0] - 2026-08-23

- Initial governance scaffold created.
- No human participant identity or content was generated.
