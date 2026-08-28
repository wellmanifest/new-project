# Ticket 134: Release atomic material-delivery governance

- **ID**: ticket-134
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-08-28

## Cel i Zakres

Release the corrective adoption-carrier contract as
`wellmanifest/new-project` 0.19.1. Synchronize only release metadata,
manifests and version-bound conformance fixtures; preserve the reviewed
policy and implementation from PRs #224 and #227.

## Kryteria Odbioru (Acceptance Criteria)

- [x] AC-01: Every live standard-version assertion resolves to 0.19.1.
- [x] AC-02: The adoption package is generated from one reviewed immutable SHA.
- [x] AC-03: All hub tests and the deterministic governance gate pass.
- [ ] AC-04: The annotated tag and final GitHub Release point to that exact SHA.

## Ryzyka i Uwagi

- Immutable tags are never moved; any post-release defect requires a new patch.
- Historical TODO and changelog references to 0.18.10 remain historical facts.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-134/`.
