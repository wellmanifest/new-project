# Ticket 234: Lower default ticket WIP cap; log real GOV-WORK-START-001 cause locally

- **ID**: ticket-234
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-09-17

## Cel i Zakres

Znalezione podczas operacyjnego dochodzenia w `semcod/koru`: `project/ticket-155/intent.json`
brakowało w głównym checkoucie (przypadkowe, niescommitowane skasowanie 730
plików `project/**`), co powodowało `FileNotFoundError` w `work_start_check.inspect()`.
`main()` łapie ten i każdy inny wyjątek (`OSError`, `KeyError`, `TypeError`,
`ValueError`, `StopIteration`) i zwraca wyłącznie ogólny komunikat
"Observation incomplete or inconsistent" — celowo, by nie ujawniać
sekretów/URL-i w stdout. W praktyce to zamieniło jednolinijkowy, łatwy do
naprawienia problem w wielorundowe dochodzenie wymagające obejścia CLI i
wywołania `inspect()` bezpośrednio.

Niezależnie zaobserwowano, że własny hub `wellmanifest/new-project` ma
`maxActiveTicketsPerWorkstream: 1`, a realnie ma obecnie kilkanaście
aktywnych worktree'ów — limit sam w sobie nie powstrzymuje rozrostu, gdy
nikt go nie pilnuje, ale niższy domyślny limit dla nowych adopcji (4→3)
ogranicza, jak daleko taki rozrost zdąży zajść, zanim ktoś to zauważy.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: `governance/manifest.default.json` — `maxActiveTicketsPerWorkstream` obniżony z 4 do 3; test walidatora zaktualizowany.
- [x] AC-02: `work_start_check.py` `main()` zapisuje pełny wyjątek + traceback lokalnie do `.governance/.observation-failures.log` (gitignored przez istniejący wzorzec `*.log`) przed wypisaniem sanityzowanego komunikatu na stdout; stdout/stderr bez zmian pod względem nieujawniania treści.
- [x] AC-03: nowy/rozszerzony test (`test_invalid_intent_fails_closed_without_content_disclosure`) potwierdza, że sekret nadal nie przecieka na stdout/stderr, a realna przyczyna trafia do lokalnego logu.

## Ryzyka i Uwagi
- Risk: lokalny plik logu mógłby rosnąć bez ograniczeń przy powtarzających się awariach — zmitygowane przycinaniem do ostatnich 2000 linii w `_record_observation_failure`.
- Risk: obniżenie domyślnego limitu do 3 dotyczy tylko *nowych* adopcji (`manifest.default.json`); już zaadoptowane repozytoria (koru, subactor, prefact, repatch, nxdo, tagi, c2004) wymagają osobnej, świadomej aktualizacji swoich `.governance/manifest.json` — nie zrobiono tego automatycznie w tym tickecie, by nie zmieniać cudzego stanu bez wyraźnej decyzji per-repo.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-234/`.
