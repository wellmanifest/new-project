# Ticket 244: register nl-dsl-llm and code-dsl in standard packs catalog

- **ID**: ticket-244
- **Owner**: agent
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Utworzono**: 2026-09-18

## Cel i Zakres
Formalna rejestracja pakietów standardów `wellmanifest/nl-dsl-llm` oraz `wellmanifest/code-dsl` w katalogu standardów `governance/standard-packs.json` oraz dokumentacji `docs/STANDARD_PACK_BOUNDARIES.md`.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: Rejestracja `wellmanifest/code-dsl` i `wellmanifest/nl-dsl-llm` w `governance/standard-packs.json`.
- [x] AC-02: Aktualizacja tabeli granic i odpowiedzialności w `docs/STANDARD_PACK_BOUNDARIES.md`.
- [x] AC-03: Walidacja zgodności JSON i testów konformacji pakietów (`GOV-PASS`).

## Ryzyka i Uwagi
- Risk 1: Niezgodność schematu `standard-packs.json`.
  Mitygacja: Weryfikacja parserem JSON oraz suite'em testów walidatora ładu.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-244/`.
