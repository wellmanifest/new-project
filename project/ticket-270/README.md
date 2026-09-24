# Ticket 270: Apply local OneDev and Validator publication to every repository by default

- **ID**: ticket-270
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-09-24

## Cel i Zakres
Local OneDev verification plus the independent Validator is the default publication route for every repository; an adopter may only narrow that default through .governance/local-ci-publication.json.

## Kryteria Odbioru (Acceptance Criteria)
- [ ] AC-01: The canonical policy, AGENTS rule 11a and the adopter reference apply to every repository by default; no organization list limits them.
- [ ] AC-02: An optional .governance/local-ci-publication.json with schema new-project.local-ci-publication/v1 can restrict scope; absent file or mode all means unrestricted.
- [ ] AC-03: Existing adoption, pack and governance tests pass; the change is listed under Unreleased in CHANGELOG.

## Ryzyka i Uwagi
- Adopter reference copies still pin revision d5f77d8 until the follow-up re-pin ticket; the reference text itself already states the new default.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-270/`.
