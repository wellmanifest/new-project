---
participant-id: agent:claude
participant: claude
role: agent
ticket: ticket-028
---
# Participant: claude (AI agent)

## Understanding

Luka nie leży w nazewnictwie gałęzi jako takim — leży w tym, że `P-CORE-015`
wymaga, by zaufane zatwierdzenie identyfikowało aktywny ticket, a nic w tym
repozytorium nie gwarantuje, że pull request taki ticket w ogóle nosi.
Zewnętrzny walidator ma tylko trzy miejsca, w których może go szukać: linię
`Ticket:` w opisie, gałąź `ticket/NNN-*` i tytuł. Trzy z czterech otwartych
PR-ów nie mają żadnego z nich.

Świadomie odrzucone: dopasowywanie ticketu po prozie opisu. PR #34 wspomina
„ticket 020" i „tickets 018 and 021", nie mając własnego — takie dopasowanie
zatwierdziłoby go pod cudzym ticketem, co jest gorsze niż brak atrybucji.

## Execution plan

1. Zapisać konwencję w `CONTRIBUTING.md` wraz z uzasadnieniem przez
   `P-CORE-015`, w tym jawne wykluczenie prozy.
2. Dodać `tests/pr-ticket-attribution.test.sh`, wyprowadzający ticket z nazwy
   gałęzi i z opisu, z przypadkiem negatywnym opartym na treści PR #34.
3. Podpiąć zestaw do `.github/workflows/ci.yml` i dopisać go do mapowania
   wymaganych checków w `docs/GOVERNANCE_ENFORCEMENT.md`.
4. Zebrać dowód AC-04: uruchomienie skanu walidatora przed i po zmianie.

## Actual changes

- None; waiting for approval.

## Blockers

- Human approval is required before implementation.
