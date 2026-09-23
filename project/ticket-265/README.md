# Ticket 265: Make governance runtime acquisition independent of PyPI publisher configuration

- **ID**: ticket-265
- **Owner**: codex
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-09-23

## Cel i Zakres

Make every generated governance workflow install the runtime from the
immutable `wellman-v<standard>` tag in `wellmanifest/new-project`, instead of
assuming that PyPI has a matching trusted publisher. PyPI remains an optional
distribution channel whose failure stays visible; the GitHub release asset is
still produced for recovery and audit.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: Reusable and generated adopter workflows use the immutable Git
      runtime tag derived from the adopted standard version.
- [x] AC-02: Standard/package projections are advanced atomically to 0.20.47.
- [ ] AC-03: Protected merge, standard release and `wellman-v0.20.47` tag
      complete; GitHub release contains the built runtime asset.

## Ryzyka i Uwagi
- PyPI trusted publishing may remain unavailable (`invalid-publisher`); this
  no longer blocks adopter CI because the runtime is installed from Git.

## Delivery contract

- **Accepted base**: `e9a2e1fcde9677dbad82c6aa200c05c03035aeae`
- **Target**: `main`
- **Complexity**: S
- **Validation**: version projection checks, governance validator, package
  build, workflow fixture tests, and `git diff --check`.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-265/`.
