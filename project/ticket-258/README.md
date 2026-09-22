# Ticket 258: Support Windows batch gate in pytest governance plugin

- **ID**: ticket-258
- **Owner**: codex
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-09-22

## Cel i Zakres
Zapewnić pełne wsparcie cross-platform dla środowiska Windows w szablonie `template/files/wellmanifest_governance.py`.
Podczas uruchamiania testów `pytest` na Windows plugin powinien używać `project/governance-check.bat` lub `bash`, zapobiegając błędowi `[WinError 193] %1 is not a valid Win32 application`.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: `template/files/wellmanifest_governance.py` poprawnie wybiera `governance-check.bat` lub `bash` na platformie Win32.
- [x] AC-02: Testy w `tests/pytest-plugin.test.sh` weryfikują wywołanie na Windows i przechodzą w 100%.
- [x] AC-03: `scripts/governance_check.py` oraz zestaw testów przechodzą pomyślnie.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-258/`.
