---
participant-id: agent:claude
participant: claude
role: agent
ticket: ticket-030
---
# Participant: claude (AI agent)

## Understanding

Rozjazd jest już faktem, nie zagrożeniem: ruleset wymaga `test` i
`windows-governance`, a `DIRECT_PR_REQUIRED_CHECKS` w `validator-agent` zna
tylko `test`. Walidator z taką konfiguracją potrafi wystawić zatwierdzenie
opierając się na jednym checku, podczas gdy branch protection pilnuje dwóch.
Zatwierdzenie zaświadcza wtedy o czymś, czego nie sprawdziło — i to jest realna
szkoda, nawet jeśli merge i tak się nie uda.

Podpowiedź z historii repozytorium: tickety 018, 021 i 025 to ten sam wzorzec —
ręczna lista zakresu, która przestała nadążać. Za każdym razem naprawą było
odczytanie rzeczywistości zamiast trzymania jej drugiej kopii, i tu powinno być
tak samo.

Nieoczywista trudność: ruleset mieszka w konfiguracji GitHuba, poza
repozytorium. Bramka w CI nie odczyta go bez uprawnień administracyjnych, więc
„jedno źródło" realnie oznacza deklarację w repozytorium plus osobny krok
sprawdzający, czy ruleset jest z nią zgodny.

## Execution plan

1. Wybrać źródło prawdy w repozytorium i uzasadnić wybór wobec ograniczenia
   dostępu do rulesetu.
2. Dodać bramkę porównującą źródło z jobami publikowanymi przez `ci.yml`,
   failującą z nazwą brakującego checku.
3. Dowieść mutacją: usunięcie joba jest wykrywane, przywrócenie zieleni wynik.
4. Opisać w `docs/GOVERNANCE_ENFORCEMENT.md`, skąd konsument zewnętrzny ma
   czytać ten zestaw, i zgłosić poprawkę `DIRECT_PR_REQUIRED_CHECKS`
   w `validator-agent`.

## Actual changes

- None; waiting for approval.

## Blockers

- Human approval is required before implementation.
