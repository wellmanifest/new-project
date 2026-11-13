# Ticket 434: Release terminal leases carrying the canonical repository identity

- **ID**: ticket-434
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-11-13

## Cel i Zakres
{Jasny opis celu biznesowego i zakresu prac}

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: Lease carrying the canonical `owner/name` identity releases through `cancel → release`.
- [x] AC-02: Foreign repository identity still refuses; legacy `local/<digest>` keeps working.
- [x] AC-03: `tests/terminal_lease_release_test.py`, `tests/governance-validator.test.sh` and `project/governance-check.sh` pass.

## Ryzyka i Uwagi
- Risk 1: {Opis ryzyka i mitygacja}

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-434/`.

<!-- ticket-radar:start -->
## Ticket Radar

Initial planned-scope estimate; advisory only, not execution or merge approval.

| Measure | Initial assessment |
| --- | --- |
| Impact score | 60/100 |
| Complexity | M |
| Estimated effort | 59 min |
| Planning budget | 30 min |
| Split recommended | yes |

Diagnostics: RADAR-ACCEPTANCE-MISSING, RADAR-BUDGET-EXCEEDED.
<!-- ticket-radar:end -->
