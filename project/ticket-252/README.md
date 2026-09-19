# Ticket 252: Allow legacy base locks during standard upgrade verification

- **ID**: ticket-252
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Created**: 2026-09-19

## Goal and scope

SESSION_EXECUTION_AUTHORIZATION: user requested continuous improvement of Wellmanifest standards and adoption pilots across legacy repos.

Support standard upgrade verification from repositories whose base revision contains legacy subset locks (e.g., standard 0.14 where not all package-manifest entries were locked into manifest.lock.json).

## Acceptance criteria

- [x] AC-01: Update `scripts/governance_check.py` to allow `set(base_hashes) <= set(base_strategies)` during standard upgrade verification.
- [x] AC-02: Check membership in `base_hashes` within `verify_managed_base` so absent legacy targets without lock entries are recognized as clean additions rather than unrecorded restorations.
- [x] AC-03: Pass complete test suite and governance check with `GOV-PASS`.
