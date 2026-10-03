# Ticket 306: Literal Git paths in overlap observations

- **ID**: ticket-306
- **Owner**: agent:codex
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Created**: 2026-10-03

## Outcome and scope
Detect overlapping actual paths despite differing Git quotePath settings. Parse NUL-separated status/diff records, preserve literal Unicode and whitespace and observe both rename endpoints. The declared installer is tested alongside the source observer; publish standard 0.20.80 after protected merge.

## Acceptance criteria
- [x] AC-01: Actual quotePath CLI and whitespace/rename Git regressions fail before the fix and pass afterwards in source and managed installation.
- [ ] AC-02: Native, integration, installed runtime, parity and current-head Linux/Windows/OneDev checks pass before independent review.
- [ ] AC-03: Independent protected merge and Goal-managed v0.20.80 publication are verified.

## Boundaries and risks
Read-only path identity grants no execution, cleanup, terminal or merge authority. Layout, base selection and ignored-path policy remain outside scope. No dependencies. Intent bounds eight material files and three components; raw receipts remain private. Session authorization covers implementation; publication approval remains independent.
