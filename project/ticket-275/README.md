# Ticket 275: Fail propagation explicitly when the org token is missing or no adopter is found

- **ID**: ticket-275
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-09-24

## Cel i Zakres
The org-wide standard propagation reports a missing or insufficient ORG_GOVERNANCE_TOKEN as an explicit failure and does not start an empty upgrade matrix.

## Kryteria Odbioru (Acceptance Criteria)
- [ ] AC-01: An unset token or an unlistable organization fails discovery with an explicit error; an empty adopter list skips the upgrade job.

## Ryzyka i Uwagi
- Release runs will now fail visibly until the owner configures ORG_GOVERNANCE_TOKEN.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-275/`.
