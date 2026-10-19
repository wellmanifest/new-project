# Ticket 353: Sync vendored git-lifecycle, ticket-lifecycle, and policy-dsl locks

- **ID**: ticket-353
- **Owner**: antigravity
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-10-19

## Cel i Zakres
Synchronizacja zvendoryzowanych kopii `wellmanifest/git-lifecycle` (`2f0018b879439015a456caf4c6280c8020ac1f70`), `wellmanifest/ticket-lifecycle` (`59b2ef08f164c14ec68ee3e95056e20c6ed916ad`) oraz `wellmanifest/policy-dsl` (`7855f21bb9586fe332c5ed32ef424009a67d47d5`) w `subprojects/` i `scripts/` wraz z aktualizacją plików `governance/*.lock.json` i testów parzystości `tests/lifecycle-adoption.test.py`.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: Zaktualizowano `subprojects/git-lifecycle`, `subprojects/ticket-lifecycle` oraz `scripts/policy_dsl_check.py` do najnowszych rewizji `main` wraz z sumami SHA-256 w `governance/*.lock.json`.
- [x] AC-02: Testy adopcji i parzystości `python3 tests/lifecycle-adoption.test.py` oraz `python3 tests/worktrees-adoption.test.py` przechodzą bez błędów.

## Ryzyka i Uwagi
- Risk 1: Rozbieżność sum kontrolnych SHA-256 pomiędzy `governance/*.lock.json` a `subprojects/` — mitygowane przez automatyczną weryfikację w `tests/lifecycle-adoption.test.py`.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-353/`.
