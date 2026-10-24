# Ticket 381: Adopt the reviewed Policy DSL parser fixes for missing defaults and transition endpoints

- **ID**: ticket-381
- **Owner**: agent:codex
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Utworzono**: 2026-10-24

## Cel i Zakres
Adopt exact reviewed Policy DSL producer0ffa41e and verify the actual installed package against findings1and2 of issue #534. No parser forks or schema/policy waivers.

SESSION_EXECUTION_AUTHORIZATION: user requested autonomous backlog implementation, tests and protected merges across ~/github/*/*. Independent exact-head review remains required.

## Kryteria Odbioru (Acceptance Criteria)
- [ ] AC-01: Installed parser rejects DEFAULT without a literal while valid declarations pass.
- [ ] AC-02: Installed parser rejects undeclared IR transition endpoints.
- [ ] AC-03: Exact producer bytes and dependency locks agree, full validation passes before protected publication.

## Ryzyka i Uwagi
- Keep this immutable adoption at four files and 20 estimated implementation minutes; preserve full checks and rollback through protected publication.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-381/`.

<!-- ticket-radar:start -->
## Ticket Radar

Initial planned-scope estimate; advisory only, not execution or merge approval.

| Measure | Initial assessment |
| --- | --- |
| Impact score | 60/100 |
| Complexity | L |
| Estimated effort | 61 min |
| Planning budget | 30 min |
| Split recommended | yes |

Diagnostics: RADAR-ACCEPTANCE-MISSING, RADAR-BUDGET-EXCEEDED.
<!-- ticket-radar:end -->
