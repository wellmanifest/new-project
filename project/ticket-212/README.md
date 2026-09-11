# Ticket 212: Publish git-ancestry terminal activity fix as 0.20.23

- **ID**: ticket-212
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-09-11

## Cel i Zakres

Wydać jako `wellmanifest/new-project` `0.20.23` już scalony, opt-in resolver
`git-ancestry` z ticketu 207. Bez opublikowanej wersji `coding-agent` nie może
przyjąć poprawki przez dozwolony, immutable adoption workflow, a hosted
governance nadal widzi scalone tickety jako aktywne, gdy nie ma zewnętrznego
rejestru receiptu.

## Kryteria Odbioru (Acceptance Criteria)
- [ ] AC-01: `bash tests/ticket-activity.test.sh` przechodzi na bazie merge
  commit `c65bdc2`.
- [ ] AC-02: `bash tests/adoption-lock.test.sh` i
  `bash tests/governance-validator.test.sh` przechodzą z projekcjami `0.20.23`.
- [ ] AC-03: po protected merge istnieją zweryfikowane tag `v0.20.23` i finalny
  GitHub Release; downstream adoption pozostaje osobnym krokiem.

## Ryzyka i Uwagi
- Ryzyko: publikacja z nieopublikowanego lub zmienionego HEAD. Mitygacja:
  exact-head Validator, zielony OneDev/CI i weryfikacja taga oraz Release.
- Ryzyko: przypadkowe przyjęcie standardu bez release. Mitygacja: `create_adoption_lock.py`
  ma pozostać fail-closed, a `coding-agent` nie będzie ręcznie kopiowany.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-212/`.
