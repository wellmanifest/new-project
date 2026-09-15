# Ticket 219: Exclude inherited feature history from worktree contention

- **ID**: ticket-219
- **GitHub Issue**: https://github.com/wellmanifest/new-project/issues/331
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-09-13

## Cel i Zakres
Naprawić przypisywanie wspólnej historii feature branchu jako konkurencyjnej zmiany.
Zakres: checker overlap i jego istniejący zestaw regresji; bez zmiany authority.

## Kryteria Odbioru (Acceptance Criteria)
- [ ] AC-01: Wspólne commity obu HEAD-ów nie blokują jednego rzeczywistego writera.
- [ ] AC-02: Rzeczywiste konflikty oraz konserwatywne sprawdzanie niepełnych danych pozostają wykrywane.

## Ryzyka i Uwagi
- Ryzyko: zbyt szerokie wykluczenie zmian ukryłoby konflikt. Testy obejmują dwa dirty writery, unikalny commit, rename i awarię odczytu Git.
- Użytkownik jawnie zatwierdził jednorazowy przydział przez zarządzany alokator poza wadliwym wrapperem. Prywatna kopia opublikowanego alokatora przekazuje checkerowi dokładne dwa pliki; blokada klonu, high-water i kontrola aktywności pozostają aktywne. Nie dodano trwałego obejścia.
- Wykonanie i chroniona publikacja autoryzowane w sesji; nie jest to zaufane zatwierdzenie merge.
- Rejestracja Planfile/Issue/PR pozostaje osobnym żądaniem: https://github.com/wellmanifest/new-project/issues/330.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-219/`.
