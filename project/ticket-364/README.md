# Ticket 364: Report an undeclared workstream in work_start_check instead of a generic RECONCILE

- **ID**: ticket-364
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-10-22

## Cel i Zakres
`work_start_check.py --workstream X` dla niezadeklarowanego `X` kończył się
`KeyError` w `inspect()` i generycznym `RECONCILE` „preserve work and
reconcile” z odesłaniem do lokalnego logu. Wywołujący szukał rozbieżnej pracy,
której nie było. Teraz `reason` mówi `GOV-WORKSTREAM-001`, że lokalnie nie ma
nic do uzgodnienia, i podaje listę zadeklarowanych workstreamów. Kształt
raportu nie zmienia się, więc schemat `work-start-report` zostaje bez zmian.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: nieznany workstream daje raport zgodny ze schematem, z `GOV-WORKSTREAM-001` i nazwami zadeklarowanych workstreamów w `reason`; surowy argument nie jest powtarzany.
- [x] AC-02: przypadek nie zapisuje logu obserwacji, a repozytorium pozostaje czyste; pozostałe błędy obserwacji nadal trafiają do logu.
- [x] AC-03: `tests/work_start_test.py` przechodzi (96 testów); test FIFO wywołuje teraz prawdziwy błąd obserwacji.

## Ryzyka i Uwagi
- Pole `route` zostaje `RECONCILE`, bo wymaga tego gałąź błędu schematu. Osobna trasa wymagałaby zmiany schematu poza zakresem tego ticketu.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-364/`.
