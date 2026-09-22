# Ticket 259: Fix stale adoption validation base resolution

- **ID**: ticket-259
- **Owner**: codex
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-09-22

## Cel i Zakres

Zapewnić, że funkcja `resolve_validation_base` w `scripts/governance_check.py` ignoruje historyczne zgłoszenia adopcyjne (`standardAdoption`), których zmiany zostały już zintegrowane (`delivery_landed`) na gałęzi docelowej (`refs/remotes/origin/<targetBranch>`).
Zapobiega to zatruwaniu bazy walidacji (`acceptedBaseSha`) w repozytoriach, w których zakończone zgłoszenia adopcyjne pozostały ze statusem `IN_PROGRESS` z powodu braku lokalnych receiptów.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: `resolve_validation_base` filtruje rekordy adopcji, których dostarczenie jest już obecne na gałęzi docelowej.
- [x] AC-02: Testy jednostkowe w `tests/delivery-post-merge-base.test.py` weryfikują ignorowanie zintegrowanych zgłoszeń adopcyjnych.
- [x] AC-03: Wszystkie testy walidatora i governance przechodzą pomyślnie (`./project/governance-check.sh`).

## Ryzyka i Uwagi
- Risk 1: Fałszywe wykrycie w locie podczas trwającego brancha adopcyjnego — mitygowane przez `delivery_landed`, które sprawdza również obecność niezmergowanych gałęzi tego ticketu (`_unmerged_ticket_branch`).

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-259/`.
