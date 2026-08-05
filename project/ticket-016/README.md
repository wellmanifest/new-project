# Ticket 016: Deterministyczne egzekwowanie klasyfikacji pracy

- **ID**: ticket-016
- **Owner**: unresolved:human
- **Status**: PLAN
- **Workflow state**: WAIT_FOR_APPROVAL
- **Utworzono**: 2026-08-05

## Cel i zakres

Połączyć opublikowany kontrakt `BUG > FEATURE > SERVICE` z aktywną bramką
governance. Nowe aktywne tickety mają używać `intent/v3` i jawnie deklarować
niezależne pola `kind`, `priority` oraz `origin`; historyczne zamknięte intencje
v1/v2 pozostają czytelne.

## Kryteria odbioru

- [ ] AC-01: `intent/v3` wymaga poprawnej klasyfikacji pracy.
- [ ] AC-02: Aktywny ticket v1/v2 jest odrzucany przed implementacją.
- [ ] AC-03: Validator ładuje i sprawdza zarządzany kontrakt DSL.
- [ ] AC-04: Historyczne nieaktywne tickety v1/v2 pozostają zgodne.
- [ ] AC-05: Testy odrzucają brak klasyfikacji, nieznane wartości i dryf DSL.

## Zatwierdzenie interaktywne

Użytkownik zatwierdził wykonanie ticketu 016 2026-08-05. Zgoda pozwala przejść
do implementacji po zapisaniu plan-only commita, ale nie zastępuje zaufanego
exact-head merge approval.
