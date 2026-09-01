# Ticket 180: Support protected rewritten merges in terminal receipt verification

- **ID**: ticket-180
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Utworzono**: 2026-09-01

## Cel i Zakres

Naprawić terminalny resolver aktywności tak, aby poprawnie rozliczał chronione
GitHub rebase i squash merges. Obecna polityka wymaga, by zamrożony `headSha`
PR był przodkiem terminalnego SHA. Obie metody zachowują zmiany, ale tworzą
nowe commity, więc poprawny receipt PR `wellmanifest/dsl#17` jest odrzucany i
scalony ticket pozostaje fałszywie aktywny.

Bezpieczny fallback ma nadal wymagać terminalnego SHA osiągalnego z targetu,
liniowej oryginalnej serii. Rebase wymaga identycznej uporządkowanej serii
stabilnych patch-id, a squash identycznego agregatu zakresu i pojedynczego
terminalnego commita. Format receiptu pozostaje bez zmian, a poprawka wraz z
projekcją wersji `0.20.2` jest jednym materialnym zakresem.

## Kryteria Odbioru (Acceptance Criteria)

- [x] AC-01: Zwykły merge ancestry oraz poprawne wielocommitowe rebase i squash
      przechodzą, a zmieniona lub nieliniowa seria jest odrzucana bez
      nadpisania rejestru.
- [x] AC-02: Polityka, schema, runtime, runbook, pakiet i testy opisują jeden
      fail-closed kontrakt `git-ancestry-or-rewritten-patch-series`.
- [x] AC-03: Pełna suita i projekcje `0.20.2` przechodzą; exact-range
      governance jest wykonywane na atomowym HEAD przed publikacją.
- [ ] AC-04: PR wiąże `Closes #288`, przechodzi niezależny Validator, a release
      `v0.20.2` wskazuje dokładny terminalny commit.

## Ryzyka i Uwagi

- Patch-id sam nie jest authority. Resolver wymaga także istniejącego
  oryginalnego head, liniowej i równolicznej serii oraz terminalnego SHA
  osiągalnego z target branch.
- Brak dowolnego dowodu, merge commit w oryginalnej serii albo różnica choć
  jednego patch-id pozostawia ticket aktywny.
- Platformowy rejestr artefaktów nie ma wpisów dla tego repozytorium; jego
  `artifacts:build/check` nie ma tu zastosowania.

## Walidacja

- 15/15 skryptów `tests/*.test.sh`: PASS.
- `python3 tests/worktrees-adoption.test.py`: 7/7 PASS.
- `ruff check scripts/ticket_activity.py`: PASS; istniejący plik jako całość
  pozostaje poza formatowaniem, bo jego bazowy styl nie jest formatem Ruff.
- Rzeczywiste SHA `wellmanifest/dsl#17`: ancestry=false,
  rebase-patch-series=true, terminal-on-target=true.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-180/`.
