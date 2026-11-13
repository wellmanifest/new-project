# Ticket 435: Explicit fenced continuation of local reservation leases

- **ID**: ticket-435
- **Owner**: agent:codex
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Created**: 2026-11-13

## Goal and authorization

SESSION_EXECUTION_AUTHORIZATION: user requested continued implementation, testing
and independent protected merges. An expired local reservation with no checkout
cannot use ordinary takeover or restoration. Add an explicit, CAS-bound controller
handoff for this missing state. Add the existing owner's missing heartbeat/head
checkpoint operation, without extending expiry or changing ownership. These
material controller fixes ship together in standard0.20.149; this is not a
release-only ticket.

Native owner: codex-expired-reservation-recovery-20261113t2324; accepted revision/fence1/1.
Implementation stage:23:24:16Z–23:54:16Z, maximum30minutes. Preserve checkpoints
and stop implementation at the boundary. Independent protected CI/publication
continues from the frozen material head; no silent source-stage reset.

## Acceptance criteria

- [x] AC-01: Explicit recovery of an expired missing reservation issues a fresh fenced owner and a bound request for the existing restoration controller; identity and high-water remain unchanged.
- [x] AC-02: Active, frozen, released, invalid, ambiguous and stale requests preserve existing state; deleted-cwd writers block recovery; interrupted effects replay idempotently with no second claim.
- [ ] AC-03: A live owner can checkpoint its canonical HEAD without extending expiry; version149, focused regressions, protected CI and independent publication pass.

## Boundaries

Use generated disposable repositories only before publication and supported
adoption. No source replay, cleanup of unknown work, self approval, credential
changes or publication authority from diagnostic output. Reuse pinned transition,
identity and atomic-storage helpers. The normal work-start gate remains required
after a recovered checkout is restored. Keep the owned material checkout and
current controlled lease until its qualified immutable release is complete.
Raw logs and snapshots stay in external private evidence storage.

## Local validation

48 idle/continuation tests and22 existing restoration tests PASS. Version parity,
bundle synchronization and canonical governance PASS0errors/0warnings. New
recovery tests use generated Linux Git fixtures; no live reservation is changed.
Protected exact-head Linux/Windows/OneDev validation and independent publication
remain required. Final implementation is frozen within the original30minute stage.
