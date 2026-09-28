# Ticket 279: Controller-fenced snapshot allocator and immutable package

- **ID**: ticket-279
- **Owner**: agent:codex
- **Status**: IN_PROGRESS
- **Workflow state**: VALIDATION

## Outcome

Reserve proposals without writer authority and materialize exact imports only
under a reviewed external grant and live controller fencing. Publish the
allocator and unchanged-import proof in immutable standard 0.20.54 source.

## Acceptance criteria

- [ ] AC-01: Reservation, preservation, races and authority failures pass real Git tests.
- [ ] AC-02: Normal governance and immutable package projections pass.

## Limits

No production grant issuance, consumer deployment or adopter merge. Preserve
source history, detached failures and peer ownership. Remaining implementation
is bounded to 25 minutes; publication requires independent review.

## Validation

16 real Git allocator tests passed, including full governance import acceptance,
concurrent reservation, source/index preservation and late plan/ref rejection.
Managed gate passed without errors or warnings. Publication remains independent.
