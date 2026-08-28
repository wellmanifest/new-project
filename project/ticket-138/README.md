# Ticket 138: Release new-project 0.19.3

- **ID**: ticket-138
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **GitHub issue**: #234
- **Workflow state**: EDIT
- **Utworzono**: 2026-08-28

## Cel i Zakres
Publish the merged monorepo ownership correction as immutable version 0.19.3.

## Kryteria Odbioru (Acceptance Criteria)
- [ ] AC-01: Version metadata and manifests consistently declare 0.19.3.
- [ ] AC-02: The full governance hub contract passes.
- [ ] AC-03: The reviewed merge is published as immutable tag v0.19.3.

## Ryzyka i Uwagi
- Existing tags are immutable; a failed publication requires a later version.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-138/`.
