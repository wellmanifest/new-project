# Ticket 016: Deterministyczne egzekwowanie klasyfikacji pracy

- **ID**: ticket-016
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
- **Utworzono**: 2026-08-05

## Cel i zakres

Połączyć opublikowany kontrakt `BUG > FEATURE > SERVICE` z aktywną bramką
governance. Nowe aktywne tickety mają używać `intent/v3` i jawnie deklarować
niezależne pola `kind`, `priority` oraz `origin`; historyczne zamknięte intencje
v1/v2 pozostają czytelne.

## Kryteria odbioru

- [x] AC-01: `intent/v3` wymaga poprawnej klasyfikacji pracy.
- [x] AC-02: Aktywny ticket v1/v2 jest odrzucany przed implementacją.
- [x] AC-03: Validator ładuje i sprawdza zarządzany kontrakt DSL.
- [x] AC-04: Historyczne nieaktywne tickety v1/v2 pozostają zgodne.
- [x] AC-05: Testy odrzucają brak klasyfikacji, nieznane wartości i dryf DSL.

## Zatwierdzenie interaktywne

Użytkownik zatwierdził wykonanie ticketu 016 2026-08-05. Zgoda pozwala przejść
do implementacji po zapisaniu plan-only commita, ale nie zastępuje zaufanego
exact-head merge approval.

## Walidacja

- `bash tests/governance-validator.test.sh` - PASS
- `bash tests/governance-scripts.test.sh` - PASS
- `bash tests/adoption-lock.test.sh` - PASS
- Dziewięć mutacji normatywnych sekcji DSL jest odrzucanych fail-closed.

## Zapobieganie regresjom

Każda nowa właściwość normatywna kontraktu wymaga pozytywnej asercji i
negatywnej mutacji. Plan, implementacja, approval, release i adopcja pozostają
osobnymi, kolejno zależnymi etapami.

## Dowody zamknięcia

- PR #17 (`feat(governance): enforce classified active intents`) scalony do `main`
  jako `c02962b`.
- `intent/v3` z wymaganym obiektem `classification` jest w
  `governance/intent.schema.json`; kontrakt wymiarów w
  `governance/work-classification.dsl.json` (`kind` BUG/FEATURE/SERVICE,
  `priority` P0-P3, `origin` regression/requested/health) i jego schemat
  `governance/work-classification.schema.json`.
- Wszystkie pięć kryteriów odbioru było odhaczonych przed merge; zamknięcie
  uzupełnia wyłącznie status i artefakty, nie zmienia zakresu.
