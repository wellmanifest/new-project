# Ticket 454: Preserve adopter concurrency and idle handoff policy during immutable upgrades

- **ID**: ticket-454
- **Owner**: agent:codex
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-11-17

SESSION_EXECUTION_AUTHORIZATION: user authorized autonomous implementation,
delegation, testing, protected publication and merge. This ticket is the
upstream reusable repair for immutable adopters: preserve an existing target's
explicit concurrency and idle-handoff policy while applying a standard, while
leaving new-install defaults unchanged. Ownership, CAS, scope and protected
review gates remain mandatory; timeout alone never grants takeover.

The implementation is limited to the adoption planner/lock, its real Git
regressions, the upgrade documentation, and required producer projections.
Consumer adoption and live runtime changes are out of scope.

## Kryteria Odbioru (Acceptance Criteria)
- [ ] AC-01: Existing target-owned WIP and idle-handoff settings survive a
  standard upgrade, while a fresh target retains published defaults.
- [ ] AC-02: Real Git regressions cover old-base migration, modified target
  policy, stale/foreign ownership and CAS/lease refusal without weakening
  takeover or closure gates.
- [ ] AC-03: Documentation and immutable producer projections describe the
  compatibility rule; focused, full and exact-base governance checks pass.

## Ryzyka i Uwagi
- Risk: a broad default change could silently enable takeover or raise target
  concurrency. Mitigation: project only verified target-owned values from the
  accepted base and keep new-install defaults in the published standard.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-454/`.

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
