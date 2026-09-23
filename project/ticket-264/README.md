# Ticket 264: Synchronize Wellman runtime package with standard 0.20.46

- **ID**: ticket-264
- **Owner**: codex
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-09-23

## Cel i Zakres

Synchronize the published `wellman` runtime package with the immutable
Wellmanifest standard `0.20.46`. The governance workflow installs the runtime
by the adopted standard version, so the package must be built and published
under the same version before downstream adopters can pass CI.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: `packages/wellman/pyproject.toml` declares `0.20.46`, matching
      `VERSION` and both standard manifest projections.
- [ ] AC-02: The package builds, the protected PR merges, and tag
      `wellman-v0.20.46` publishes the package through trusted PyPI workflow.

## Ryzyka i Uwagi
- The immutable standard release already exists; this ticket only restores
  the runtime artifact required by its CI installer.

## Delivery contract

- **Accepted base**: `44fb615715f64ca3be6502669d508dfe8e3078da`
- **Target**: `main`
- **Complexity**: S
- **Validation**: version projection check, package build, governance validator,
  and `git diff --check`.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-264/`.
