# Ticket 267: Keep runtime releases from becoming the latest standard release

- **ID**: ticket-267
- **Owner**: claude
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-09-23

## Cel i Zakres
`wellman-publish.yml` created runtime releases (`wellman-v0.20.47`,
`wellman-v0.20.48`) with GitHub's default "Latest" flag. `goal governance adopt
--latest` resolves `releases/latest` and accepts only a final `vX.Y.Z` tag, so
every adopter's `--latest` resolution failed. Runtime releases must never take
"Latest". The workflow runs only in the hub and is not an adopter-managed file,
so no standard version bump is required.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: The "Create GitHub Release" step sets `make_latest: "false"`.
- [x] AC-02: `tests/wellman-package.test.sh` fails when the flag is removed.
- [ ] AC-03: Protected merge; the next runtime release is not marked Latest.

## Ryzyka i Uwagi
- The currently mislabelled `wellman-v0.20.48` release stays Latest until the
  next standard `vX.Y.Z` release is published (separate operator action).

## Delivery contract

- **Accepted base**: `26cbecf4d461250a5b696d573dc300b2acd1b929`
- **Target**: `main`
- **Complexity**: XS
- **Validation**: `bash tests/wellman-package.test.sh` (positive and flag
  removal negative), governance gate, and `git diff --check`.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-267/`.
