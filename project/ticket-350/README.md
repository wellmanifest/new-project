# Ticket 350: Host pointer: final results go to the owning repo (docs/logs), never only /tmp or chat

- **ID**: ticket-350
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-10-18

## Cel i Zakres
{Jasny opis celu biznesowego i zakresu prac}

## Kryteria Odbioru (Acceptance Criteria)
- [ ] AC-01: {Kryterium 1}
- [ ] AC-02: {Kryterium 2}

## Ryzyka i Uwagi
- Risk 1: {Opis ryzyka i mitygacja}

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-350/`.
