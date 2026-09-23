# Ticket 269: Run the wellman gate as the CI actor in adopter workflows

- **ID**: ticket-269
- **Owner**: claude
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-09-23

## Cel i Zakres
Adopter CI (observed on `wellmanifest/wellman` PR #8 at 0.20.49) failed in
`wellman check --root . --json` with `GOV-AGENT-HOST-006` because a CI runner
never has the developer clone's `core.hooksPath`. The checker already skips
clone-bound host checks for `--actor ci`, and the later `governance_check.py`
step passes it; the `wellman check` invocations did not. Pass `--actor ci` in
both adopter workflows. Released as standard 0.20.50.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: The managed adopter workflow and the reusable gate run
      `wellman check ... --actor ci`.
- [x] AC-02: `tests/wellman-package.test.sh` fails if either workflow drops it.
- [ ] AC-03: Protected merge, standard `v0.20.50` and `wellman-v0.20.50`.

## Ryzyka i Uwagi
- Local developer runs keep the default `agent` actor and still verify the
  hook; only CI invocations change.

## Delivery contract

- **Accepted base**: `a939efa78049d9a62414671b4cd026c548a025da`
- **Target**: `main`
- **Complexity**: S
- **Validation**: wellman package test (with negatives per workflow),
  governance gate, `git diff --check`.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-269/`.
