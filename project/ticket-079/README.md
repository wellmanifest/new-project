# Ticket 079: Release HOME versus ADOPT placement as new-project 0.18.0

- **ID**: ticket-079
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: VALIDATION
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
- [ ] AC-04: PR otrzymuje trusted exact-head Validator approval i jest scalony
  bez zmiany zatwierdzonego drzewa.
- [ ] AC-05: czysty merge `main` przechodzi retest, a annotowany tag i finalny
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

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-079/`.
