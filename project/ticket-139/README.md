# Ticket 139: Allow Docker stage aliases under digest enforcement

- **ID**: ticket-139
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **GitHub issue**: #236
- **Workflow state**: EDIT
- **Utworzono**: 2026-08-28

## Cel i Zakres
Keep immutable digest enforcement for external images while recognizing prior
Docker multi-stage aliases as local build graph references.

## Kryteria Odbioru (Acceptance Criteria)
- [ ] AC-01: A pinned external base followed by internal stage aliases passes.
- [ ] AC-02: Unknown aliases and mutable external images still fail.
- [ ] AC-03: Full governance hub contract passes.

## Ryzyka i Uwagi
- Alias recognition is ordered and exact; undeclared names remain fail-closed.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-139/`.
