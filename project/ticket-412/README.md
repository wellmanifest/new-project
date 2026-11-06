# Ticket 412: Reject malformed branch lifecycle references

- **ID**: ticket-412
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Utworzono**: 2026-11-06

## Cel i Zakres
Reject invalid literal branch names at the shared branch-lifecycle snapshot boundary before evaluating lifecycle findings. Reuse the existing offline parser; cover defaultBranch, branches and openPullRequests.headRef. Include the material 0.20.141 version; protected release admission remains a separate operational dependency.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: All branch fields reject malformed names and retain valid Git names; public CLI reports GOV-BRANCH-LIFECYCLE-003.
- [ ] AC-02: Native governance and real CI pass; independent Validator reviews the exact published head.

## Ryzyka i Uwagi
- Risk 1: Invalid historical observations now fail closed; preserve all refs and reacquire evidence. No cleanup authority is granted.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-412/`.

<!-- ticket-radar:start -->
## Ticket Radar

Initial planned-scope estimate; advisory only, not execution or merge approval.

| Measure | Initial assessment |
| --- | --- |
| Impact score | 68/100 |
| Complexity | L |
| Estimated effort | 74 min |
| Planning budget | 30 min |
| Split recommended | yes |

Diagnostics: RADAR-ACCEPTANCE-MISSING, RADAR-BUDGET-EXCEEDED.
<!-- ticket-radar:end -->

## Session execution authorization
SESSION_EXECUTION_AUTHORIZATION: user requested continued refactoring, tests and protected merges; PLF-022 / NP-039 finding1. Bounded slice is offline branch-name validation and its regression tests. Independent Validator owns approval and merge.
