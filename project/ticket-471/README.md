# Ticket 471: Cancelled terminal outcome with owner-decision verification

- **ID**: ticket-471
- **Owner**: tom
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-11-23

## Cel i Zakres
Implements option A of issue #661 and step 6 of
`docs/information/work-registration.md`. A ticket whose pull request the owner
closed without merge (redundant or superseded) kept its scope reservation
indefinitely: only `merged`/`no-change` released it, both requiring the head on
the target. Add verification `owner-decision` for an outcome `cancelled`. The
receipt's `decision` binds the PR number, `closed-unmerged`, the deciding actor
and a reference. No closure commit, no branch deletion; new ticket work after the
decided head re-activates the reservation. Requested by the owner on 2026-11-23.

Phase one only: the default policy does not list `cancelled` yet. Resolvers that
predate this change reject a policy naming `owner-decision`, and the overlap
inspector reads every checkout's policy with its own resolver (observed while
developing this ticket). A follow-up enables the outcome once every managed copy,
including the bundled Wellman runtime, is updated.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: With `cancelled: owner-decision` in the policy, a receipt with a closed-unmerged decision releases the reservation and the ticket branch is preserved; with the shipped default policy the receipt is refused.
- [x] AC-02: Missing decision, non-closed PR state, unknown head and a decision on a merged receipt are rejected without touching the registry.
- [x] AC-03: New commits on the ticket branch after the decided head re-activate the reservation; existing activity, work-start, overlap, handoff and lease-release tests pass.

## Ryzyka i Uwagi
- Recording a receipt is the controller's authority (local git-common-dir registry, as for `merged`); the PR state is supplied by the controller, not fetched. A false decision releases a reservation, but never deletes work, and resumed commits re-activate it.
- Adopters get the resolver now and the outcome in a later managed policy update; mixing a new policy with an old resolver fails closed (`remain-active`) with GOV-TICKET-ACTIVITY-001.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-471/`.

<!-- ticket-radar:start -->
## Ticket Radar

Initial planned-scope estimate; advisory only, not execution or merge approval.

| Measure | Initial assessment |
| --- | --- |
| Impact score | 64/100 |
| Complexity | L |
| Estimated effort | 75 min |
| Planning budget | 30 min |
| Split recommended | yes |

Diagnostics: RADAR-ACCEPTANCE-MISSING, RADAR-BUDGET-EXCEEDED.
<!-- ticket-radar:end -->
