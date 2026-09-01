# Ticket 178: Adopt Worktrees v4 repository-local relative layout

- **ID**: ticket-178
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-09-01

## Cel i Zakres

Adoptować opublikowany kontrakt `wellmanifest/worktrees` v0.4.0 z dokładnego
SHA `73f9b99227bfbad6ce02834324d053279fb48611` i wydać go jako łamiący standard
`wellmanifest/new-project` 0.20.0. Jedynym publikowalnym układem ma być
`<primaryCheckout>/worktrees/<ticket>--<slug>` z relatywnymi metadanymi Git,
a lease ma należeć do
`<primaryCheckout>/.subactor/leases/<ticket>--<slug>.json`.

Zmiana obejmuje normatywne instrukcje i host templates, dokładnie przypięte
projekcje Worktrees v4, konfigurację guard, klasyfikację read-only w lifecycle
i overlap oraz testy adopcyjne. Starsze układy v1/v2/v3, ścieżki `/tmp`,
duplikaty i przypadki nieznane są wyłącznie raportowane do recovery; standard
nie przesuwa, nie usuwa, nie prune'uje ani nie czyści istniejących checkoutów.

## Kryteria Odbioru (Acceptance Criteria)

- [x] AC-01: lock i zarządzane projekcje wskazują dokładnie Worktrees v0.4.0,
      źródłowy SHA i zweryfikowane hashe schema/conformance v4.
- [x] AC-02: polityka i host templates wymagają repo-local `worktrees/`,
      `linkMode=relative`, Git 2.51 feature probe, lease w `.subactor/leases`
      oraz zakotwiczonych wpisów ignore `/worktrees/` i `/.subactor/`.
- [x] AC-03: lifecycle i overlap klasyfikują v1/v2/v3, `/tmp`, v4,
      duplicate i unknown bez automatycznego move/delete/prune/clean; tylko
      kanoniczny v4 jest publikowalny.
- [x] AC-04: testy POSIX, Windows, lock, lifecycle, overlap i pełna suita
      deterministyczna przechodzą, a exact governance akceptuje HEAD.
- [x] AC-05: release projections zgadzają się na 0.20.0, a PR wiąże i zamyka
      zewnętrzne `wellmanifest/new-project#284` bez samodzielnego merge.

## Ryzyka i Uwagi

- Git przechowuje tryb względnych linków jako wspólny efekt metadanych clone.
  Polecenie `git worktree repair --relative-paths
  <primaryCheckout>/worktrees/ticket-178--adopt-worktrees-v4`
  naprawiło rejestracje linked worktree tego clone. Ich treść i położenie nie
  są zmieniane; dostępność jest sprawdzana read-only przed oddaniem PR.
- Główny checkout zawiera należący do użytkownika nieśledzony plik
  `template/files/tests/conftest-worktree-bootstrap.template.py`. Praca odbywa
  się wyłącznie w tym dedykowanym worktree; plik i primary checkout pozostają
  nietknięte.
- Wymaganie Git 2.51 jest sprawdzane przez feature probe. Środowisko bez
  obsługi `--relative-paths` ma zakończyć alokację bez częściowego efektu.

## Walidacja

- 15/15 `tests/*.test.sh`: PASS.
- 7/7 `python3 tests/worktrees-adoption.test.py`: PASS, w tym planner POSIX i
  Windows, inventory v1/v2/v3/v4/system-temp/unknown/duplicate oraz scratch
  repo z rename i dokładnym `git worktree repair --relative-paths` (gdy feature
  probe środowiska potwierdza obsługę).
- `bash tests/adoption-lock.test.sh`, `bash tests/governance-validator.test.sh`,
  lifecycle i overlap: PASS.
- Lokalny host nie ma `pwsh`; Windows entrypoint pozostaje obowiązkowym checkiem
  CI `windows-governance` i nie jest deklarowany jako lokalnie wykonany.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-178/`.
