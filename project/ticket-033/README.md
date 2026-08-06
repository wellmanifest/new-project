# Ticket 033: Load DIRECT_PR required checks from target governance/required-checks.json

- **ID**: ticket-033
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Utworzono**: 2026-08-06

## Cel

Ticket-030 wprowadził jedno źródło w hubie. Validator nadal mógł używać tylko
env `DIRECT_PR_REQUIRED_CHECKS`. Ten ticket: **preferuj plik z head PR**.

## Acceptance criteria

- [x] AC-01: Gdy `governance/required-checks.json` istnieje na head, używane są `requiredCheckNames`.
- [x] AC-02: Gdy pliku brak, fallback do env/request (bez regresji).
- [x] AC-03: Test mutacyjny / unit: plik z `test`+`windows-governance` wygrywa z requestem tylko `test`.

## Deliverable

PR `subactor/validator-agent#13` (wspólny z 032).
