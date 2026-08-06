# Ticket 034: Expand rule-enforcement mapping for unmapped POLICY and CONTRIBUTING rules

- **ID**: ticket-034
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: VALIDATION
- **Utworzono**: 2026-08-06

## Cel

Ticket-027 dodał audit i plik mapowania, ale na main było ~146 reguł
niezmapowanych i ~35 kodów bez reguł. Ten ticket uzupełnia
`governance/rule-enforcement.json` tak, że **każda** reguła ma wpis
(deterministyczny lub `manual` z powodem), a **każdy** kod z
`governance_check.py` jest claimowany.

## Acceptance criteria

- [x] AC-01: Każdy kod GOV emitowany przez `governance_check.py` ma regułę
  (zero `codes_no_rule_claims`).
- [x] AC-02: Każda reguła z POLICY/CONTRIBUTING ma wpis (zero unmapped).
- [x] AC-03: Reguły proceduralne mają `enforcement: manual` i niepusty `reason`.
- [x] AC-04: `tests/rule-enforcement.test.sh` wymusza `--require-complete` i
  przechodzi.

## Wynik

```text
rule-enforcement: 148 rules, 37 codes, 0 unmapped, 0 codes unclaimed
```

Około 31 reguł `manual` (procedura agenta / human plan) — kandydaci na
przyszłe GOV-*.

## Depends on

ticket-027 (DONE, PR #37).
