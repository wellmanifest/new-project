# Ticket 315: Resolve compact routine intent target branch in work continuity

- **ID**: ticket-315
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: VALIDATION
- **Utworzono**: 2026-10-06

## Cel i Zakres
Resolve targetBranch from manifest delivery targetBranches when delivery object is omitted in compact routine intents; fail closed on ambiguous or missing manifests (resolving Issue #442).

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: Compact routine intent, full delivery, ambiguous and missing manifest fixtures pass in continuity storage tests and shell tests.
- [x] AC-02: Native governance gate passes with 0 errors and 0 warnings.
- [ ] AC-03: Pull request independently verified by CI and merged.

## Ryzyka i Uwagi
- Risk 1: Unobserved branches must not be guessed silently; fail closed if manifest targetBranches has != 1 entries.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-315/`.
