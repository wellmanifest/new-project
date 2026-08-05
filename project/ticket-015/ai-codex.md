---
participant-id: agent:codex
participant: codex
role: agent
ticket: ticket-015
---
# Participant: codex (AI agent)

## Understanding

Nowy kontrakt DSL i wersjonowany manifest pakietu są już na `main`, ale tag
`v0.10.0` jest immutable i nie może zacząć oznaczać późniejszych zmian.
Potrzebny jest release 0.11.0, którego pełny SHA stanie się bazą migracji
`semcod/todo2code` i `semcod/goal`.

## Execution plan

1. Ujednolicić wersję 0.11.0 w pięciu zatwierdzonych plikach.
2. Zamknąć bieżące `Unreleased` jako 0.11.0 i opisać manifest pakietu,
   approval evidence oraz DSL klasyfikacji.
3. Uruchomić testy governance, adoption i skryptów.
4. Po exact-head approval scalić PR przygotowujący.
5. Zweryfikować merge SHA w czystym detached checkoutcie.
6. Utworzyć nieprzesuwalny annotowany tag i GitHub Release dla tego SHA.
7. Dopiero potem przygotować tickety adopcyjne w repozytoriach docelowych.

## Acceptance evidence

- `bash tests/governance-scripts.test.sh`
- `bash tests/governance-validator.test.sh`
- `bash tests/adoption-lock.test.sh`
- `git rev-parse v0.11.0^{commit}` i API GitHub Release
- czysty status detached checkoutu przed i po testach

## Actual changes

- Użytkownik zatwierdził kontynuację wcześniej przedstawionego zakresu.
- Ticket przeszedł do `IN_PROGRESS / EDIT`.
- Wersja standardu, manifestu i asercji testowych została podniesiona do
  `0.11.0`; bieżące zmiany przeniesiono do sekcji wydania 0.11.0.
- Dotknięty negatywny scenariusz wersji nie wyłącza już `errexit`;
  oczekiwaną porażkę sprawdza jawna instrukcja warunkowa.
- Trzy wymagane zestawy regresyjne przeszły przed merge.

## Blockers

- Publikacja taga wymaga merge po niezależnym exact-head approval i ponownej
  walidacji merge SHA w czystym checkoutcie.
