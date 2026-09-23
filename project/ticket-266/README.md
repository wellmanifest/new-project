# Ticket 266: Bundle complete governance checker runtime in wellman package

- **ID**: ticket-266
- **Owner**: claude
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-09-23

## Cel i Zakres
Make the installed `wellman` runtime actually run the governance gate.
`_bundled/governance_check.py` was a one-off copy from #379 and never shipped
the sibling modules it loads (`ticket_activity.py`, `repository_policy.py`,
...), so every released runtime crashed on start; `--version` and the
documented `check [--json]` form were never supported. Ship the complete
closure synchronized from `scripts/`, support the documented CLI and test the
installed wheel in CI; release as standard 0.20.48.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: `_bundled/` contains `governance_check.py` and its eight sibling
      modules byte-identical to `scripts/`; `sync_bundled.py --check` fails on
      drift or undeclared files.
- [x] AC-02: The wheel installed in a clean venv answers `wellman --version`
      with the standard version and runs `wellman check --json` without
      crashes or missing-module findings (`tests/wellman-package.test.sh`, CI).
- [ ] AC-03: Protected merge, then tag `wellman-v0.20.48`; runtime installed
      from the tag passes the same smoke commands.

## Ryzyka i Uwagi
- Bundled copies can drift when `scripts/` changes; CI runs the drift check,
  and `python3 packages/wellman/sync_bundled.py` restores them.
- PyPI trusted publishing is still misconfigured (`invalid-publisher`); adopters
  install from the Git tag, so this does not block them.

## Delivery contract

- **Accepted base**: `786e43f64c772706e8e0769f97992e1057478913`
- **Target**: `main`
- **Complexity**: S
- **Validation**: bundle drift check, installed-wheel smoke test, required
  checks, governance validator, and `git diff --check`.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-266/`.
