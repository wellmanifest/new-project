# Ticket 274: Re-pin local CI publication references to merged revision and release

- **ID**: ticket-274
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-09-24

## Cel i Zakres
Ticket-270 shipped the unrestricted local OneDev + Validator default in merge
`d4dab328fbea876eadd3f4ad4e2349d520a2b15a`, but the authored document and the
adopter reference copy still pin the superseded 0.20.10 revision `d5f77d8`.
Re-pin both to the merged revision, advance the managed-copy digest and release
projections atomically, and publish the result as standard `0.20.53`.

## Kryteria Odbioru (Acceptance Criteria)
- [ ] AC-01: `docs/information/local-ci-publication.md` declares `source_revision` `d4dab328fbea876eadd3f4ad4e2349d520a2b15a` and the adopter template references `new-project 0.20.53` at that revision with the current document digest.
- [ ] AC-02: `governance/managed-copies.json` matches the updated template; local-ci-publication and Wellman package regressions plus the managed governance gate pass.
- [ ] AC-03: Protected exact-head CI and independent Validator pass, the protected controller merges, clean merged-SHA retests pass, and Goal publishes immutable `v0.20.53`.

## Ryzyka i Uwagi
- Pinning the not-yet-tagged revision is intentional: the release tag lands on
  this ticket's merge commit, while `d4dab328` already contains the shipped v3
  document content the reference describes.
- SESSION_EXECUTION_AUTHORIZATION: the user requested continued implementation,
  testing, protected merge and publication. No review or CI gate is waived.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-274/`.
