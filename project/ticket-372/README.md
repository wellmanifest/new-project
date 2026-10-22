# Ticket 372: A ticket's own PR carries its own TICKETS.md row (issue 516)

- **ID**: ticket-372
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-10-22

## Cel i Zakres
Issue #516: `project/readme.sh` pomijał każdy nieśledzony katalog ticketu, także
ten właśnie zaalokowany, więc wiersz ticketu dodawał dopiero PR następnego
ticketu (np. #519 dodał wiersz ticket-365). Przy równoległych sesjach wiersze
trafiały do cudzych PR-ów jako „zły id”. Alokator wskazuje teraz własny ticket
przez `T2C_TICKET_INDEX_OWN`.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: po alokacji indeks w checkoucie ticketu zawiera własny wiersz, bez zdalnych roszczeń; obcy nieśledzony ticket w tym samym checkoucie nadal pominięty; zła wartość → exit 2; goły `readme.sh` nadal pomija nieśledzone. Bez poprawki test pada. Testy alokacji, adopcji, restoration i snapshot przechodzą.
- [x] AC-02: wersja 0.20.119; ten PR niesie własny wiersz ticket-372 (oraz zaległy ticket-371).

## Ryzyka i Uwagi
- Punkt 1–3 issue (komunikat i komenda naprawy dla bramki) czeka na wskazanie bramki, która blokowała.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-372/`.
