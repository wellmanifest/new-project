# Ticket 380: Prepare the local-pin hook fixture with a real writer lease

- **ID**: ticket-380
- **Owner**: agent:codex
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Utworzono**: 2026-10-24

## Cel i Zakres
Repair the positive local-pin hook fixture required by issue #534 and PR #539. Use an isolated real writer lease and retain continuity and updater assertions.

SESSION_EXECUTION_AUTHORIZATION: user requested autonomous backlog fixes, tests and protected publication. Implementation scope: tests/precommit-local-pin.test.py only.

## Kryteria Odbioru (Acceptance Criteria)
- [ ] AC-01: Pin cases reach actual continuity verification after real writer checks.
- [ ] AC-02: Updater suite and governance pass before protected publication.

## Ryzyka i Uwagi
- Keep production guards unchanged. One fixture, 15 estimated minutes, no dependencies.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-380/`.

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
