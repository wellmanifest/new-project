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

- Extracted small classification, package, lock and atomic-adoption helpers
  without changing public entry points or diagnostics.
- Extracted Decision DSL body, line and required-field helpers and added exact
  parser-diagnostic regressions.
- Lizard reports zero functions over CC 15; pinned Vallm reports 2/2 pass with
  zero deterministic findings. All configured Linux tests pass.
- Ticket is in `IN_PROGRESS / VALIDATION`; protected Windows CI remains.

## Blockers

- None.
