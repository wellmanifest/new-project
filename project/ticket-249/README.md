# Ticket 249: Align Wellman package release projection

- **ID**: ticket-249
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-09-19

## Cel i Zakres

Uzgodnić deklarację wersji dystrybuowanego pakietu `wellman` z wydanym
standardem `0.20.33`. Poprzedni merge poprawki collect-only podniósł VERSION i
manifesty, ale pozostawił metadane pakietu na `0.20.32`, przez co Goal odmówił
utworzenia niezmiennego wydania.

## Kryteria Odbioru (Acceptance Criteria)
- [ ] AC-01: `packages/wellman/pyproject.toml` deklaruje `0.20.33`.
- [ ] AC-02: Goal rozpoznaje jednolitą wersję wydania i może opublikować tag
  oraz finalny Release z zatwierdzonego merge SHA.

## Ryzyka i Uwagi
- Nie zmieniamy istniejącego merge SHA ani wcześniejszych tagów; korekta jest
  publikowana przez chroniony proces z nowego, zatwierdzonego PR-a.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-249/`.
