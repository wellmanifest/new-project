---
participant-id: agent:codex
participant: codex
role: agent
ticket: ticket-063
---
# Participant: codex

## Understanding

Obecna polityka poprawnie opisuje zdalny stan spoczynkowy, ale pomija lokalne
workspace. Reusable workflow zawiera live snapshot GitHuba, lecz nie jest
elementem pakietu adopcyjnego, więc większość targetów go nie uruchamia.
Pilotażowe linked worktree i niezależne klony nie są widoczne dla CI.

## Execution plan

1. Zapisać terminalny kontrakt cleanup i ochronę unikalnych danych w DSL.
2. Dodać read-only checker lokalnych worktree i zduplikowanych klonów.
3. Dostarczyć checker i autonomiczny remote-lifecycle workflow w pakiecie.
4. Dodać regresje dla lokalnego oraz zdalnego enforcementu.
5. Uruchomić pełny kontrakt i zastosować checker do całego `semcod`.

## Actual changes

- Potwierdzono brak reguł lokalnego cleanup oraz brak workflow adopcyjnego w
  pakiecie; tylko `todo2code` wywoływał reusable governance workflow.
- Zweryfikowano 26 pilotów: commity dotyczyły wyłącznie governance, a dirty
  pliki były wygenerowaną analizą. Usunięto 19 linked worktree i przeniesiono
  7 czystych niezależnych klonów do kosza.

## Blockers

- Brak w zakresie implementacji standardu.
- Unikalne, nieopublikowane branche Goal i aktywne PR-y innych repozytoriów
  wymagają osobnego audytu przed cleanupem.

