# Ticket 371: Terminal receipts verify across a regenerated ticket index (issue 524)

- **ID**: ticket-371
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-10-22

## Cel i Zakres
Issue #524: receipt PR-a zsquashowanego lub zrebase'owanego na nowszą bazę był
odrzucany (GOV-TICKET-ACTIVITY-001), bo wygenerowany `project/TICKETS.md` miał
już wiersze dodane przez siostrzany ticket, więc hunk indeksu znikał. Ticket
zostawał IN_PROGRESS i trzymał zakres oraz slot WIP (dockuri ticket-071..073).

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: fixture: dwa tickety z jednej bazy; squash i rebase drugiego na nowszy cel bez hunka indeksu → receipt zapisany; zmieniona treść autorska i dodatkowa ścieżka nadal odrzucone. Bez poprawki oba pozytywne przypadki padają. Istniejące testy aktywności przechodzą.
- [x] AC-02: test w CI, wersja 0.20.118.

## Ryzyka i Uwagi
- Wykluczony jest tylko indeks generowany przez `project/readme.sh`; każda inna ścieżka musi się zgadzać dokładnie.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-371/`.
