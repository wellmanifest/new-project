# Ticket 147: Release new-project 0.19.7

- **ID**: ticket-147
- **Owner**: human:founder
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-08-30

## Cel i Zakres

Wydać immutable `wellmanifest/new-project` 0.19.7 zawierający zmergowaną
naprawę przypisywania zakresów ticketów do worktree, aby adoptery mogły
zaktualizować zarządzane checkery przez hash-bound lock.

## Kryteria Odbioru (Acceptance Criteria)

- [x] AC-01: Wszystkie projekcje wersji wskazują 0.19.7.
- [x] AC-02: Pełna deterministyczna suita standardu przechodzi.
- [ ] AC-03: Chroniony proces publikuje tag/release wyłącznie po merge.

## Ryzyka i Uwagi

- Istniejący tag nie będzie przesuwany; ewentualna korekta wymaga następnej
  wersji.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-147/`.
