# Ticket 366: Read-only controller editing resource observation in work-start (issue 510)

- **ID**: ticket-366
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-10-22

## Cel i Zakres
Issue #510: `work_start_check.py` raportował rozłączne ścieżki jako kandydata do
nowego ticketu, choć kontroler ma jeden wyłączny zasób edycji na repozytorium i
branch docelowy. `--controller-store DIR --controller-repository OWNER/NAME`
dodaje tylko-do-odczytu obserwację `editingResource`.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: fixture: rozłączny zakres z route `NEW_TICKET_CANDIDATE` i stanem `HELD_BY_OTHER` bez sesji/aktora właściciela i bez zapisu do store; `HELD_BY_TICKET`, `HELD_EXPIRED` (czas i faza), `AVAILABLE`; powody `UNAVAILABLE` (brak store, symlink, niepoprawny stan, zmiana w trakcie odczytu); CLI wymaga obu opcji i poprawnego `OWNER/NAME`; raport zgodny ze schematem.
- [x] AC-02: runbook `GOV-WORK-START` (sekcja o dostępności kontrolera), test w CI, wersja 0.20.113.

## Ryzyka i Uwagi
- Obserwacja nie jest uprawnieniem: wygaśnięcie leasu nie pozwala na przejęcie, a `QUEUED` nie jest przydziałem.
- Klient runtime (transport, pin, polityka) pozostaje poza zakresem; schemat tylko deklaruje te powody.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-366/`.
