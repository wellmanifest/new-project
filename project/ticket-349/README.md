# Ticket 349: Resolve AST performance audit findings across hub scripts

- **ID**: ticket-349
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Created**: 2026-10-17

## Goal and scope

SESSION_EXECUTION_AUTHORIZATION: On 2026-10-17 user authorized fixing PERF-AUDIT findings and aligning `.governance/standard-adoption.json` across wellmanifest repositories.
Resolve all 9 AST performance audit findings (`PERF-AUDIT-KWARG-001`, `PERF-AUDIT-SQLITE-001`, `PERF-AUDIT-SUBPROC-001`) across `scripts/generate_required_checks.py`, `subprojects/worktrees/conformance.py`, `scripts/ticket_input.py`, `scripts/create_adoption_lock.py`, and `scripts/governance_check.py`, synchronize bundled copies in `packages/wellman`, and populate `.governance/standard-adoption.json`.

## Acceptance criteria

- [x] AC-01: Wire optional parameters in `declaration_for` and `_git_output`, hoist SQLite query execution outside the loop in `database_rows`, and extract subprocess helpers outside loops in `create_adoption_lock.py` and `governance_check.py`.
- [x] AC-02: Synchronize `packages/wellman` bundled scripts, update `governance/worktrees.lock.json`, populate `.governance/standard-adoption.json`, and pass governance and test checks.

## Tracking boundary

This directory contains the minimal reviewed intent. Optional participant prose
and raw command logs are not required delivery output.
