---
participant-id: agent:codex
participant: codex
role: agent
ticket: ticket-040
---
# Participant: codex (AI agent)

## Understanding

The target adoption is functionally green and provenance-bound. Its protected
Koru report rejects only five deterministic complexity warnings from managed
upstream Python sources. Skipping `.governance/**`, changing review thresholds
or treating semantic output as authority would weaken the boundary and is not
acceptable. The durable fix is to reduce the upstream source complexity and
publish a new immutable release afterward.

## Execution plan

1. Capture the exact five Koru findings and freeze behavior with focused tests.
2. Extract pure validation helpers from the four governance-check functions.
3. Extract small field/JSON parsing helpers from `parse_dsl_record`.
4. Run the focused suites, complete Linux and Windows contracts and Docker.
5. Reproduce the pinned downstream deterministic Koru/Vallm scan.
6. Obtain exact-head protected review and merge this refactor without a version
   bump; publish it through a separately approved release ticket.

## Actual changes

- User approved the exact four-file scope on 2026-08-08. The ticket is in
  `IN_PROGRESS / EDIT`; implementation has not yet changed a source or test.

## Blockers

- None.
