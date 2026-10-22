# Ticket 365: Governed restoration of an already reserved ticket (issue 509)

- **ID**: ticket-365
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-10-22

## Cel i Zakres
Issue #509: odtworzenie już zarezerwowanego ticketu, którego kanoniczny checkout,
branch lub niezacommitowane metadane zniknęły, bez nowego numeru i bez ręcznej
rekonstrukcji. `new-ticket.sh --restore-request` uruchamia `scripts/ticket_restoration.py`.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: fixture: utrata checkoutu, branch+metadane (przez allocator), związany osiągalny HEAD z zacommitowanymi metadanymi, przerwane odtworzenie, niezgodna rezerwacja, zmieniony/terminalny snapshot, obcy/wygasły właściciel, kolizje, symlink i SQLite; high-water bez zmian, brak nadpisań.
- [x] AC-02: helper w package manifest, runbook `GOV-TICKET-ALLOCATION` krok 7, test w CI, wersja 0.20.112.

## Ryzyka i Uwagi
- Przekazanie właściciela nie jest obsługiwane: rekord rezerwacji musi wskazywać aktualnego właściciela leasu kontrolera.
- Odtworzenie nie daje prawa edycji; dalej obowiązuje `work_start_check.py --ticket`.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-365/`.
