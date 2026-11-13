# Ticket 433: Restore locally reserved checkouts with owner fencing

- **ID**: ticket-433
- **Owner**: agent:codex
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Utworzono**: 2026-11-13

## Cel i Zakres

A local-single-clone allocation already has a canonical file lease, but checkout
restoration currently demands an unrelated external controller registration.
Add an explicit route for the current live local owner using the reserved identity,
exact metadata snapshot and lease digest/CAS. Retain the external route unchanged.
SESSION authority: user requested continued implementation, testing and independent publication.
Owner session: codex-local-restoration22409-20261113; accepted revision/fence 1/1.
Implementation stage: 2026-11-13T20:51:01Z–21:21:01Z, at most 30 minutes;
checkpoint unfinished work at the boundary, without silently resetting this stage.

## Kryteria Odbioru (Acceptance Criteria)

- [x] AC-01: Missing checkout/branch restores the same reservation and metadata; retry is idempotent.
- [x] AC-02: Exact owner, lease digest/CAS, repository/scope, live phase and expiry are enforced before every effect; expired leases require a separate authorized handoff.
- [ ] AC-03: Existing external recovery, canonical governance and protected independent publication remain required.

## Ryzyka i Uwagi

No new ticket number, lease renewal, source replay, protected-policy changes or
publication authority. Existing files and branches are never overwritten. Tests
use disposable generated repositories; source changes are not used on live targets
before protected publication and supported adoption.

## Granica katalogu

Only this minimal contract is stored here. Raw logs remain outside the repository.

## Validation checkpoint

Local restoration: 22 tests passed; legacy recovery: 27 tests passed. Shell syntax
and native governance passed. Current base includes the independently published
writer identity correction. Protected CI and independent publication remain pending.
