# Ticket 242: controlled-change-streaming v7 standard specification

- **ID**: ticket-242
- **Owner**: agent:antigravity
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-09-18

## Cel i Zakres
Aktualizacja specyfikacji standardu `docs/information/controlled-change-streaming.md` do wersji 7 (zgodnie z Issue #355). Wprowadzenie tabeli dowodowej z incydentów blokad, zamkniętego słownika tras (`AUTO`, `RECIPE`, `DECISION`, `ESCALATE`), nowych receptur dla typowych sytuacji zatorów oraz zasad deeskalacji (związanie zakresu blokady z zakresem zmiany, TTL dla dzierżaw i rezerwacji, SLO publikacji, wersjonowanie bramek).

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: `docs/information/controlled-change-streaming.md` podniesiony do wersji 7 z pełną specyfikacją tras i deeskalacji.
- [x] AC-02: Walidacja `./project/governance-check.sh` zwraca `GOV-PASS`.

## Ryzyka i Uwagi
- Zmiana dotyczy dokumentacji standardu procesowego i informacji architektonicznej.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-242/`.
