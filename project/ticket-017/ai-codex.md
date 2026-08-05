---
participant-id: agent:codex
participant: codex
role: agent
ticket: ticket-017
---
# Participant: codex (AI agent)

## Understanding

Użytkownik chce, aby branch ticketowy był zasobem tymczasowym, a nie trwałym
archiwum. Zmiana zachowuje obowiązkową izolację pracy i review, lecz domyka
cykl po merge. Nie wolno automatycznie usuwać niezmergowanego brancha po samym
zamknięciu PR-a, bo mogłoby to zniszczyć jedyną referencję do pracy.

## Execution plan

1. Dodać stabilne reguły lifecycle do `POLICY.md`.
2. Ujednolicić skrót operacyjny w źródłowym `AGENTS.md` i adoptowanym
   `template/files/AGENTS.template.md`.
3. Opisać wymagane ustawienie GitHub, zachowanie po merge/close i stan
   spoczynku w `docs/GOVERNANCE_ENFORCEMENT.md`.
4. Dodać deterministyczne asercje regresyjne do
   `tests/governance-validator.test.sh`.
5. Uruchomić trzy istniejące zestawy testów governance.

## Actual changes

- Dodano trzy normatywne reguły: cleanup po merge, ochrona pracy po close bez
  merge oraz jednoznaczny stan spoczynku repozytorium.
- Zsynchronizowano źródłowy i adoptowany `AGENTS.md` oraz runbook GitHub.
- Dodano deterministyczne asercje chroniące regułę przed dryfem dokumentacji.
- Wszystkie trzy zestawy regresyjne huba przeszły.

## Blockers

- Brak; ticket 016 został formalnie zamknięty jako `ed7b725`, a użytkownik
  zatwierdził zakres ticketu 017.

## Architecture before implementation

- Komponent `normative-policy`: `POLICY.md` i źródłowe `AGENTS.md` definiują
  wymagane zachowanie oraz bezpieczną granicę usuwania.
- Komponent `adoption-and-evidence`: szablon AGENTS, runbook oraz test dbają,
  aby reguła trafiła do adopterów i nie zniknęła przy kolejnej zmianie.
- Brak zmian runtime, zależności, UI i publicznego API aplikacji.

## Existing-runtime investigation

- `scripts/governance_check.py` nie enumeruje GitHub branchy ani PR-ów.
- `todo2code` ma `workspace-preflight` oraz `branch-portfolio`, lecz wymagają
  lokalnych/dostarczonych refów i nie sprawdzają `delete_branch_on_merge`.
- `subactor/onedev-agent` sprawdza default branch, ale nie lifecycle PR/branch.
- Brakujący required runtime został wydzielony do zależnego ticketu 018.
