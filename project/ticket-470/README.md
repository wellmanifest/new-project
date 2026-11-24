# Ticket 470: Run first bootstrap split regression in CI

- **ID**: ticket-470
- **Owner**: agent:antigravity
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Utworzono**: 2026-11-21

## Goal and scope

Planfile NP-059 and issue #656 cover first-bootstrap recovery. PR #657 adds
the split regression. Hosted CI checks that every test suite is registered,
and the existing fresh-bootstrap shell suite runs in GitHub and OneDev.
Register the regression from that shared suite in this separate scope.

## Acceptance criteria

- [x] AC-01: The fresh-bootstrap suite still passes on its base. With the
  controller regression present, the suite runs it and propagates failure.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-470/`.

<!-- ticket-radar:start -->
## Ticket Radar

Initial planned-scope estimate; advisory only, not execution or merge approval.

| Measure | Initial assessment |
| --- | --- |
| Impact score | 48/100 |
| Complexity | M |
| Estimated effort | 44 min |
| Planning budget | 30 min |
| Split recommended | yes |

Diagnostics: RADAR-ACCEPTANCE-MISSING, RADAR-BUDGET-EXCEEDED.
<!-- ticket-radar:end -->
