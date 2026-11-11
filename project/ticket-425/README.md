# Ticket 425: Retry transient Git snapshot invalidations in worktree overlap ticket_scopes

- **ID**: ticket-425
- **Owner**: agent:antigravity
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-11-11

## Cel i Zakres

Wyeliminowanie fałszywych błędów `GOV-TICKET-ACTIVITY-001` (`Git state changed during activity inspection; retry` oraz `ticket inventory changed during activity inspection; retry`) w `scripts/worktree_overlap_check.py` (`ticket_scopes`) podczas równoległych commitów/aktualizacji gałęzi przez sąsiednie worktrees poprzez ograniczony, 3-krotny retry pełnej migawki `ActivityReadBatch` z zachowaniem trybu fail-closed przy trwałym wyścigu lub uszkodzeniu dokumentów aktywności.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: Przejściowa zmiana refów Git lub inwentarza ticketów podczas `ActivityReadBatch` w `ticket_scopes` ponawia pełną spójną migawkę (do 3 prób), natomiast trwały churn oraz uszkodzenie rejestru nadal kończą się błędem fail-closed.
- [x] AC-02: Testy jednostkowe (`python3 -B tests/ticket_activity_batch_test.py`), `./project/governance-check.sh` oraz `wellman check` przechodzą bez błędów.

## Ryzyka i Uwagi
- Risk 1: Zachowanie częściowych danych z unieważnionej próby — mitygowane przez czyszczenie `scopes` i `errors` przed każdą kolejną próbą `ActivityReadBatch`.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-425/`.
