# Ticket 245: reconcile git and ticket lifecycle contracts under vendored copy lock

- **ID**: ticket-245
- **Owner**: agent
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-09-18

## Cel i Zakres

Uzgodnienie rozbieżności pomiędzy kontraktami `git-lifecycle` i `ticket-lifecycle`
znajdującymi się w podprojektach huba `subprojects/*` a ich samodzielnymi repozytoriami HOME
(`wellmanifest/git-lifecycle` i `wellmanifest/ticket-lifecycle`) pod lockiem SHA-256 na wzór
wzorca `worktrees` (`wellmanifest/ssot` rodzaj `vendored_copy`), zamykając Issue #347:

1. Uznanie samodzielnych repozytoriów `wellmanifest/git-lifecycle` (`24cfe7c`) i `wellmanifest/ticket-lifecycle` (`ad363ef`) za kanoniczne HOME kontraktów.
2. Związanie podprojektów `subprojects/git-lifecycle` i `subprojects/ticket-lifecycle` lockami `governance/git-lifecycle.lock.json` oraz `governance/ticket-lifecycle.lock.json` ze skrótami SHA-256 każdego pliku.
3. Uzgodnienie projekcji egzekwowalnej w `subprojects/git-lifecycle/README.md` i `ticket-lifecycle/README.md` (w tym akcji `checkpoint` i dowodów ciągłości).
4. Utworzenie testu parity i reguł adopcji `tests/lifecycle-adoption.test.py` (6/6 PASS).
5. Zapisanie formalnej decyzji architektonicznej w `governance/lifecycle-vendored-copy.ssot.json` wg schematu `wellmanifest.ssot/decision/v1`.

## Kryteria Odbioru (Acceptance Criteria)

- [x] AC-01: `python3 tests/lifecycle-adoption.test.py` przechodzi pomyślnie (6/6 testów OK).
- [x] AC-02: `python3 tests/worktrees-adoption.test.py` przechodzi pomyślnie (11/11 testów OK).
- [x] AC-03: `governance/git-lifecycle.lock.json` i `governance/ticket-lifecycle.lock.json` wiążą dokładne skróty SHA-256 artefaktów z HEAD repozytoriów standalone.
- [x] AC-04: `governance/lifecycle-vendored-copy.ssot.json` jest poprawnym dokumentem `wellmanifest.ssot/decision/v1` z zerem findings w walidatorze SSOT.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-245/`.
