# Ticket 468: Preserve a live writer lease while waiting for independent CI

- **ID**: ticket-468
- **Owner**: agent:codex
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-11-20

## Goal and scope

Planfile PLF-29358 records a writer takeover while the owner was observing
independent CI. The inactivity timer had elapsed although the lease was valid.
Treat the lease expiry as a separate condition in the automatic idle path.
The board identifies a quiet but still-valid lease. A deliberate transfer uses
the existing protected owner handoff.

SESSION_EXECUTION_AUTHORIZATION. Continue the recorded autonomy backlog and
submit this bounded correction for independent verification.

## Acceptance criteria

- [x] A quiet live lease stays assigned to its owner during independent CI.
- [x] The write path refuses the takeover under its lock and preserves the exact lease bytes.
- [x] The existing owner checkpoint and expired lease tests pass.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-468/`.

<!-- ticket-radar:start -->
## Ticket Radar

Initial planned-scope estimate; advisory only, not execution or merge approval.

| Measure | Initial assessment |
| --- | --- |
| Impact score | 56/100 |
| Complexity | M |
| Estimated effort | 58 min |
| Planning budget | 30 min |
| Split recommended | yes |

Diagnostics: RADAR-ACCEPTANCE-MISSING, RADAR-BUDGET-EXCEEDED.
<!-- ticket-radar:end -->
