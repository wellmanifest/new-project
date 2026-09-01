# Ticket 176: Adopt collision-proof worktrees v0.3.0

- **ID**: ticket-176
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-09-01

## Cel i Zakres

Zastąpić wadliwą projekcję Worktrees v2 wersją v3, która rezerwuje katalog
`.worktrees/.branches` i odrzuca przejście przez symlink. Publikacja 0.19.22
należy do tego samego materialnego PR.

## Kryteria Odbioru (Acceptance Criteria)

- [ ] AC-01: Vendored schema i checker są bajtowo zgodne z Worktrees v0.3.0.
- [ ] AC-02: Instrukcje i testy wskazują `.worktrees/.branches/<repo>`.
- [ ] AC-03: Pełna macierz i chroniony merge przechodzą na dokładnym headzie.

## Ryzyka i Uwagi

- Istniejące v1/v2 worktrees pozostają na miejscu do osobnego audytu
  procesów, IDE, lease, PR, dirty state i reachability.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-176/`.
