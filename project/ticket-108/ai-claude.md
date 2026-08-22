---
participant-id: agent:claude
participant: claude
role: agent
ticket: ticket-108
---
# Participant: claude (AI agent)

## Understanding

Trzeci slice serii rozpoczętej w `ticket-106`. Kontrakt host-agnostyczny jest
egzekwowalny (106) i rozsyłany (107); brakuje warstwy, która go uruchamia u
adopterów, oraz domknięcia audytów, które przepuściły pierwotny defekt.

## Execution plan

1. Dodać job `governance / enforce` do zarządzanego szablonu workflow.
2. Rozszerzyć `audit_diagnostics.py` o `.githooks` i zarejestrować kody hooka.
3. Rozszerzyć `audit_rule_enforcement.py` o `agent_host_check.py`.
4. Dodać reguły `C-HOST-001..003` i zmapować je na kody deterministyczne.

## Actual changes

- `template/files/new-project-governance.workflow.yml`: job `governance /
  enforce`, pominięty przy `action == closed`, walidujący zakres PR-a przez
  `--base/--head`, a przebieg scheduled/dispatch przez `--changed-file`.
- `scripts/audit_diagnostics.py`: `.githooks` jako powierzchnia runtime bez
  filtra rozszerzeń.
- `scripts/audit_rule_enforcement.py`: `scripts/agent_host_check.py` w
  `VALIDATOR_PATHS`; liczba widzianych kodów 58 → 64.
- `governance/diagnostics.json`: 74 → 77 kodów; `GOV-AGENT-HOST-001..003`.
- `CONTRIBUTING.md`: sekcja KONTRAKT HOST-AGNOSTYCZNY z `C-HOST-001..003`.
- `governance/rule-enforcement.json`: mapowanie trzech reguł na sześć kodów.
- `error/GOV-AGENT-HOST.md`: notatka o braku rejestracji stała się nieaktualna.

Decyzja o zawężeniu: pierwotnie job miał też wołać `check_required_checks.py`.
Sprawdziłem na danych adoptera i kończy się `workflow file not found:
.github/workflows/ci.yml`, bo 25/25 adopterów nosi deklarację huba. Krok
failowałby w 20 repozytoriach z powodu wady, której ten ticket nie naprawia,
więc został usunięty i zapisany jako non-goal.

Dowody: 11/11 zestawów `tests/*.test.sh` PASS, `audit_diagnostics` 77 kodów
bez findings, `audit_rule_enforcement` 178 reguł / 0 unmapped / 0 unclaimed,
brama `GOV-PASS`.

## Blockers

- Wymaganie `governance / enforce` w rulesetach adopterów jest poza
  repozytorium i wymaga decyzji człowieka; ten ticket dostarcza sygnał.
- New authority is still required for destructive action, secret access, new
  external coordination or material objective expansion.
