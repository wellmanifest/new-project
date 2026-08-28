# Ticket 140: Release new-project 0.19.4

- **ID**: ticket-140
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **GitHub issue**: #238
- **Workflow state**: EDIT
- **Utworzono**: 2026-08-28

## Cel i Zakres
Publish the reviewed Docker stage-alias correction as immutable version 0.19.4.

## Kryteria Odbioru (Acceptance Criteria)
- [ ] AC-01: Version metadata consistently declares 0.19.4.
- [ ] AC-02: Full hub contract passes.
- [ ] AC-03: Clean reviewed main publishes immutable v0.19.4.

## Ryzyka i Uwagi
- Existing tags remain immutable; corrections require a later version.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-140/`.
