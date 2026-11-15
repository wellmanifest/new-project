# Ticket 444: Batch governance activity observations without weakening invalidation

- **ID**: ticket-444
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Utworzono**: 2026-11-15

## Cel i Zakres
Use the existing ActivityReadBatch boundary for governance activity resolution.
Share observations within one inspection and revalidate them before accepting
terminal receipts. Preserve active reservations on any invalidated observation.
Source scope: scripts/governance_check.py, its generated packaged copy, focused
regression tests and their shell entry point used by native CI test discovery.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: Preserve results for stable real Git histories while reducing repeated subprocesses.
- [x] AC-02: Registry, target, policy or projection changes retain active reservations and emit GOV-TICKET-ACTIVITY-001.
- [x] AC-03: Each invocation observes fresh state; checks with no active projections need no Git inspection.
- [ ] AC-04: Affected checks and the managed gate pass before independent exact-head publication.

## Ryzyka i Uwagi
- Cached inactivity must never survive an invalidated inspection. Reuse the
  canonical context's revalidation and fail closed, without changing source
  authority, ancestry rules, required CI checks or the existing 300s deadline.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-444/`.

<!-- ticket-radar:start -->
## Ticket Radar

Initial planned-scope estimate; advisory only, not execution or merge approval.

| Measure | Initial assessment |
| --- | --- |
| Impact score | 52/100 |
| Complexity | M |
| Estimated effort | 51 min |
| Planning budget | 30 min |
| Split recommended | yes |

Diagnostics: RADAR-ACCEPTANCE-MISSING, RADAR-BUDGET-EXCEEDED.
<!-- ticket-radar:end -->
