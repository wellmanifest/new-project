# Ticket 448: Bound path matching cost in scope overlap checks

- **ID**: ticket-448
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Utworzono**: 2026-11-16

## Cel i Zakres
PR #626's current-base OneDev run timed out after 1800 seconds in the installed
governance package. A bounded diagnostic located repeated path matching in
`check_scope_overlaps`: the clean CI checkout has 304 projected active tickets
and 1760 repository files. Compute each ticket's path membership once per
invocation while retaining every overlap predicate and diagnostic.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: Preserve findings, forbidden/governance exclusions, virtual overlaps, duplicate path ordering and concrete counts.
- [x] AC-02: Bound path matching by tickets times files, recheck changed inputs, and qualify the diagnosed CI workload.
- [ ] AC-03: Pass bundled parity, full tests, current-base CI and independent protected publication.

## Ryzyka i Uwagi
Precomputation must remain local to one invocation and must preserve input
positions. Terminal-receipt policy and active ticket projections stay unchanged.
This ticket owns the checker and its existing performance tests; ticket-446
retains its separate controller change and publication.
The user approved extending this ticket to `tests/workspace_activity_test.py`
and increasing the implementation-file budget from 3 to 4. Its unreadable
inventory fixture must contain invalid Git metadata so it fails independently
of whether the runner creates temporary files inside another Git checkout.
Diagnostic receipt: `artifact:terminal446/scope-cost-diagnostic-20261116`.

## Verification

14 activity/cost regressions pass; the new cost bound fails on the accepted
implementation. The actual 304-ticket/1760-file workload completes in 20.7s
with 21,886 identical complete findings against the accepted pair loop using
transparent local memoization of its pure matcher. The comparison retains all
policy inputs. Governance reports zero errors/warnings and bundled parity
passes. Full tests, protected CI and independent publication remain pending.
Receipt: `artifact:ticket448/scope-cost-qualification-20261116`.

The updated activity and performance modules pass through the full Wellman
runner: 23 tests and 53 subtests. The refusal fixture now has explicit broken
Git metadata and retains its existing `ActivityError` assertion. Full tests,
current-base protected CI and independent publication remain required for the
updated head.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-448/`.

<!-- ticket-radar:start -->
## Ticket Radar

Initial planned-scope estimate; advisory only, not execution or merge approval.

Assessment unavailable: runtime not installed.
<!-- ticket-radar:end -->
