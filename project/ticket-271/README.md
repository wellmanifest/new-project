# Ticket 271: Pass exact PR range to Wellman governance gates

- **ID**: ticket-271
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Utworzono**: 2026-09-24

## Outcome

Fix CI validation of product PRs after a historical standard adoption. A detached
checkout currently invokes the first Wellman gate without its PR range and can
select the wrong adoption context, failing GOV-SYNC-001 before the managed gate.
Both adopter and reusable workflows must use the event's exact base/head.

## Acceptance criteria

- [x] AC-01: Detached product PR after historical adoption passes both workflow gates with the exact range.
- [x] AC-02: Scheduled checks remain supported; incomplete ranges and managed drift fail closed.

## Authorization and ownership

SESSION_EXECUTION_AUTHORIZATION: the user requested repair, testing and protected
publication. On 2026-09-24 the user explicitly approved one additional isolated
repair ticket despite the hub WIP limit: “Tak — jeden dodatkowy ticket naprawczy”.
The allocator used that one-shot exception; the tracked manifest is unchanged.
Source scope is disjoint from ticket-270, whose work and ownership are preserved.
The exception does not waive required checks or independent exact-head review.
External authorization and allocation receipts: receipt:ci-range-repair.authorization.

## Risk and delivery

A missing range must not silently weaken a PR check. Empty pairs retain non-PR
semantics; partial pairs fail before executing either gate. No dependencies added.
Release/adoption follows source integration and reconciliation of ticket-270.

## Validation

Installed wheel regression: 5 tests passed, including rejection by the old
range-less command and digest drift rejection by the managed gate. Required
checks suite and the hub governance gate pass. Independent CI/review/merge
remain pending; the ticket stays IN_PROGRESS through publication.
