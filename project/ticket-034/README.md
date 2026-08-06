# Ticket 034: Expand rule-enforcement mapping for unmapped POLICY and CONTRIBUTING rules

- **ID**: ticket-034
- **Owner**: unresolved:human
- **Status**: PLAN
- **Workflow state**: WAIT_FOR_APPROVAL
- **Utworzono**: 2026-08-06

## Cel

Ticket-027 dodał audit i plik mapowania, ale na main widać ~146 reguł
niezmapowanych i ~35 kodów bez reguł. Ten ticket **nie** zgaduje mapowań:
systematycznie uzupełnia `governance/rule-enforcement.json` i utrzymuje
bramkę `scripts/audit_rule_enforcement.py` w zieleni przy rosnącym pokryciu.

## Acceptance criteria

- [ ] AC-01: Każdy kod `GOV-*-NNN` z `diagnostics.json` ma co najmniej jedną regułę lub jawny `manual` z powodem.
- [ ] AC-02: Mapowanie reguł egzekwowanych w `governance_check.py` jest kompletne (zero `codes_no_rule_claims` poza listą wykluczeń).
- [ ] AC-03: Reguły wyłącznie proceduralne/manual mają `enforcement: manual` i `reason`.
- [ ] AC-04: CI `tests/rule-enforcement.test.sh` pozostaje zielone.

## Depends on

ticket-027 (DONE, PR #37).
