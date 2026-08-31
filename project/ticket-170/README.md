# Ticket 170: Keep all local required checks in adoption projection

- **ID**: ticket-170
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-08-31

## Cel i Zakres
Generator ma deklarować wszystkie joby lokalnego workflow; metadane circular
nie mogą usuwać ich z lokalnego źródła prawdy.

## Kryteria Odbioru (Acceptance Criteria)
- [ ] AC-01: Deklaracja zawiera każdy opublikowany job.
- [ ] AC-02: Circular metadata pozostaje dostępna dla zewnętrznego walidatora.

## Ryzyka i Uwagi
- Risk: lokalna bramka i deklaracja nie mogą się rozjechać.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-170/`.
