# Ticket 035: Gate decision logs with GOV-DECISION codes

- **ID**: ticket-035
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
- **Utworzono**: 2026-08-06

## Cel

Kody `GOV-DECISION-001`–`004` były w `diagnostics.json` i w
`decision_record.py`, ale `governance_check.py` ich nie emitował przy zmianie
`project/ticket-*/decisions.md`. Ten ticket podłącza walidację.

## Acceptance criteria

- [x] AC-01: Zmiana `decisions.md` z nieparsowalnym/ADVISORY/rozjazdowym
  rekordem failuje kodem GOV-DECISION-*.
- [x] AC-02: Mapowanie C-DECISION-001..004 → GOV-DECISION-001..004 w
  rule-enforcement.
- [x] AC-03: `tests/governance-validator.test.sh` i rule-enforcement PASS.
