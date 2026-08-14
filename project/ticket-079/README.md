# Ticket 079: Release HOME versus ADOPT placement as new-project 0.18.0

- **ID**: ticket-079
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
- **Utworzono**: 2026-08-14

## Cel i Zakres

Opublikować zintegrowany kontrakt HOME vs ADOPT z ticketu 078 jako immutable
`new-project 0.18.0`. Wydanie synchronizuje wyłącznie sześć nośników wersji,
aktywne asercje testów i changelog. Nie zmienia schematu, walidatora ani zasad
placement po ich merge.

## Kryteria Odbioru (Acceptance Criteria)

- [x] AC-01: `VERSION`, oba manifesty i aktywne asercje testowe deklarują
  dokładnie `0.18.0`.
- [x] AC-02: changelog opisuje HOME vs ADOPT jako kompatybilne wstecz minor
  release i zachowuje historię `0.17.0`.
- [x] AC-03: pełny kontrakt Linux, Ruff 0.15.21, schema, secret scan i
  governance przechodzą dla dokładnego commita kandydata.
- [x] AC-04: PR otrzymuje trusted exact-head Validator approval i jest scalony
  bez zmiany zatwierdzonego drzewa.
- [x] AC-05: czysty merge `main` przechodzi retest, a annotowany tag i finalny
  GitHub Release `v0.18.0` wskazują dokładnie ten merge SHA.

## Ryzyka i Uwagi

- Tag i finalny release są niemutowalne; powstaną dopiero po trusted merge i
  ponownym teście czystego `main`.
- To minor release, ponieważ publikuje nowy opcjonalny kontrakt placement bez
  łamania istniejących intentów.
- Adopcja w `env-dsl` pozostaje osobnym target-owned ticketem i nie należy do
  write scope tego wydania.

## Dowody przed publikacją

- Diff implementacyjny obejmuje dokładnie sześć zadeklarowanych nośników;
  brama scope raportuje `GOV-PASS` (0 błędów, 0 ostrzeżeń).
- Wszystkie dziewięć zestawów `tests/*.test.sh`, wymagane checki, JSON Schema,
  Ruff 0.15.21 i diff whitespace: PASS.
- `v0.18.0` nie istnieje jako tag ani GitHub Release przed publikacją.
- Post-merge Linux/Windows ticketu 078 i zamknięcia na `main@0479feb`: PASS.
- Commit kandydata `6c57973c3ed94269a4b57d1dfa9e99e753dc738f`
  przeszedł exact-head scope gate: `GOV-PASS`.

## Dowody dostawy

- PR #122: HEAD `e500174d51ec09b1f087dcbb8d8cb88a83d45329`;
  hostowane Linux/Windows: PASS; trusted Validator review `4939013630`:
  APPROVED dla dokładnego HEAD.
- Merge `769183ca27593af1d166acee11bc9e37decf9870` ma identyczne drzewo
  `1899b684999d8fcbd0ddc25d83dc47af795773a8` jak zatwierdzony kandydat.
- Czysty `main` przeszedł dziewięć lokalnych suite'ów, Ruff 0.15.21 oraz
  post-merge run `31816934548` na Linux i Windows.
- Goal 2.1.300 opublikował finalny release
  `https://github.com/wellmanifest/new-project/releases/tag/v0.18.0`.
  Annotowany tag object `2f050edac7f7363f48d69dd0e48ee88108efccb9`
  dereferencjonuje do merge SHA; tag-triggered run `31817259786`: PASS.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-079/`.
