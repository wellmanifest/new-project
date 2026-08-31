# Ticket 159: Resolve terminal receipts in dependency DAG

- **ID**: ticket-159
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-08-30

## Cel i Zakres

Ensure dependency validation uses the same verified terminal-receipt resolver
as active-ticket reservation, so merged prerequisites cannot remain false
blockers solely because their Markdown status is still `IN_PROGRESS`.

## Kryteria Odbioru (Acceptance Criteria)

- [ ] AC-01: A dependency with a verified terminal receipt is accepted as
      complete even if its repository status projection remains active.
- [ ] AC-02: A missing, malformed, unsupported, or unverifiable receipt keeps
      the dependency fail-closed and emits `GOV-DEPENDENCY-002`.
- [ ] AC-03: The complete deterministic standard test suite passes.

## Ryzyka i Uwagi

- Risk: an unverified receipt could release ordering too early. Mitigation:
  reuse the existing resolver and its Git-ancestry checks without a second
  lifecycle heuristic.

## Granica katalogu

This directory stores only the bounded governance contract. Implementation and
regression tests remain in their standard source directories.
