# Ticket 442: Clarify runtime_service placement refusal diagnostic and release 0.20.151

- **ID**: ticket-442
- **Owner**: agent:antigravity
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Authorization**: SESSION_EXECUTION_AUTHORIZATION + GOV-IDLE-TAKEOVER (`receipt://change-lease/allocation-ticket-442-project-job-d583966e/idle-takeover-release-2026-11-15T16:22:04Z`) — user explicitly authorized Scope 2 (`wellmanifest/new-project` release) on 2026-11-15. Task consent only, never review evidence.
- **Created**: 2026-11-15

## Goal and scope

Fixes #555 by updating `placement_error` in `scripts/governance_check.py` and its bundled `wellman` copy so `{"home": "wellmanifest", "shape": "runtime_service"}` directs operators to `HOME` in a product organization and `ADOPT` `wellmanifest` packs (consistent with `PLACEMENT_ADOPT` schema validation and `AGENTS.md`), updates the regression assertion in `tests/governance-validator.test.sh`, and ships material fixes `ticket-441` and `ticket-442` as `0.20.151` per `AGENTS.md` §23.

## Acceptance criteria

- [x] AC-01: `placement_error` returns `runtime_service must not HOME wellmanifest; HOME in a product organization and ADOPT wellmanifest packs` in both source and bundled checkers (`bash tests/governance-validator.test.sh`).
- [x] AC-02: `sync_bundled.py --check`, `version-parity.test.sh`, `wellman-package.test.sh` and `project/governance-check.sh` pass for `0.20.151`.
- [ ] AC-03: Protected Linux, Windows and OneDev checks pass and independent Validator approves and merges.

## Tracking boundary

This directory contains the minimal reviewed intent. Optional participant prose
and raw command logs are not required delivery output.
