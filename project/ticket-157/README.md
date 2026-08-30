# Ticket 157: Release new-project 0.19.11

- **ID**: ticket-157
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Utworzono**: 2026-08-30

## Cel i Zakres

Wydać immutable `wellmanifest/new-project` 0.19.11 zawierający zarządzany
resolver aktywności terminalnych receiptów i odzyskiwalną politykę governance.

## Kryteria Odbioru (Acceptance Criteria)

- [x] AC-01: wszystkie projekcje wersji wskazują 0.19.11.
- [x] AC-02: deterministyczne testy release i governance przechodzą.
- [ ] AC-03: chroniony proces publikuje tag i release dopiero po exact-head merge.

## Ryzyka i Uwagi

- Istniejących tagów nie wolno przesuwać; korekta wymaga późniejszej wersji.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-157/`.
