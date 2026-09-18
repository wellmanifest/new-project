# Ticket 241: Workspace audit rejects empty inventory and includes target repository

- **ID**: ticket-241
- **Owner**: agent:antigravity
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-09-18

## Cel i Zakres
Zgodnie z Issue #367, audyt przestrzeni roboczej (`scripts/workspace_lifecycle_check.py`) musi odrzucać pusty inwentarz repozytoriów, chyba że flaga `--allow-empty` została jawnie podana. Ponadto dodana zostaje obsługa `--target-repository` (`--target-root`, `--target`), aby zagwarantować, że repozytorium docelowe jest faktycznie objęte inwentarzem i nie dochodzi do fałszywych sukcesów (vacuous PASS) po usunięciu linked worktree.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: Jawne pokrycie repozytorium docelowego (`--target-repository`) jest weryfikowane; brak repozytorium docelowego w inwentarzu powoduje błąd `GOV-WORKSPACE-LIFECYCLE-003`.
- [x] AC-02: Pusty inwentarz repozytoriów jest odrzucany z błędem, chyba że podano flagę `--allow-empty`.
- [x] AC-03: Testy w `tests/workspace-lifecycle.test.sh` pokrywają 5 przypadków: target root, parent root, unrelated root, linked worktree (przed i po usunięciu), empty directory.
- [x] AC-04: Walidacja `./project/governance-check.sh` zwraca `GOV-PASS`.

## Ryzyka i Uwagi
- Brak ryzyka dla środowiska wykonawczego — zmiana dotyczy terminalnego audytu przestrzeni roboczej.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-241/`.
