# Ticket 179: Standardize local Subactor continuity

- **ID**: ticket-179
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-09-01

## Cel i Zakres

Wydać `wellmanifest/new-project` 0.20.1 z host-agnostycznym kontraktem
ciągłości lokalnej dla agentów Codex, Claude, Cursor, Grok i shell. Mały
`.subactor/manifest.json` pozostaje śledzony, podczas gdy wyłącznie katalogi
`leases`, `sessions`, `recovery`, `receipts`, `cache` i `snapshots` są
ignorowane. Append-only event stream nie ma limitu rozmiaru polityki, a
atomowo zapisywany indeks checkpointów pozostaje ograniczony.

Checkpoint v2 wiąże dokładny plan, slice, ticket, branch, HEAD, lease,
obserwację remote/account i receipt snapshotu. Brudna praca może przeżyć
granicę procesu wyłącznie jako commit albo content-addressed snapshot po
secret scanie. Pre-commit sprawdza wyłącznie lokalny pin i nie wykonuje
fetchu ani mutacji; świeżość pochodzi z jawnej adopcji/updatera lub bota.

## Kryteria Odbioru (Acceptance Criteria)

- [x] AC-01: pakiet dostarcza śledzony manifest i selektywne managed ignore
      rules bez ignorowania całego `.subactor/`.
- [x] AC-02: runtime i schema v2 zapisują append-only, host-agnostic events,
      atomowy bounded index i kompletne bindings plan/slice/Git/lease/remote.
- [x] AC-03: dirty checkpoint jest możliwy tylko dla commitu albo
      content-addressed secret-scanned snapshotu; proza nie jest authority.
- [x] AC-04: managed pre-commit waliduje lokalny standard pin bez sieci i bez
      mutacji, a jawna adopcja pozostaje jedyną ścieżką freshness.
- [x] AC-05: odzyskany fixture bootstrapu worktree ma zweryfikowane
      pochodzenie, jest przyjęty jako template i objęty testem.
- [x] AC-06: pełne testy, projekcje 0.20.1 i exact governance przechodzą, a PR
      wiąże `Closes #285` bez merge.

## Ryzyka i Uwagi

- Event stream jest celowo nieograniczony przez politykę; bounded index i
  walidacja pojedynczego eventu chronią ścieżkę szybkiego resume.
- Primary checkout zawiera user-owned untracked fixture. Jego hash
  `4abbe5def46a89420610e40025a2a708ceaf489159e303f5bd8bb9966ed137f2`
  odpowiada adaptacji kodu z commitów `autogrammar/hillm` `305361a` i
  `b8a9f8a`; primary nie jest modyfikowane ani nadpisywane.
- `git worktree repair --relative-paths` naprawił wyłącznie wspólne wskaźniki
  linked-worktree. Nie wykonano move/delete/prune/clean istniejących worktrees.

## Walidacja

- `for test_script in tests/*.test.sh; do bash "$test_script"; done`: PASS
  (15/15 testów POSIX).
- `python3 tests/worktrees-adoption.test.py`: PASS (7/7).
- Test hooka z rejestratorem wywołań Git: PASS; brak `fetch`/`pull`, a HEAD i
  status repozytorium pozostały identyczne.
- Exact governance jest wykonywane dla finalnego commitu przed publikacją.
- `pwsh` nie jest zainstalowany na tym hoście; test Windows pozostaje wymaganym
  checkiem CI.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-179/`.
