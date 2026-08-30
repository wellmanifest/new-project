# Ticket 152: Release new-project 0.19.9

- **ID**: ticket-152
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Utworzono**: 2026-08-30

## Cel i Zakres

Wydać immutable `wellmanifest/new-project` 0.19.9 zawierający naprawę, która
przekazuje jeden zweryfikowany rejestr plików `managed` do wszystkich bramek
własności atomowej adopcji.

## Kryteria Odbioru (Acceptance Criteria)

- [x] AC-01: wszystkie projekcje wersji wskazują 0.19.9.
- [x] AC-02: pełna deterministyczna suita standardu przechodzi.
- [ ] AC-03: chroniony proces publikuje tag i release dopiero po exact-head
      merge.

## Ryzyka i Uwagi

- Istniejących tagów nie wolno przesuwać; korekta wymaga późniejszej wersji.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-152/`.
