# Ticket 188: Evidence-based agent decisions

- **ID**: ticket-188
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Workstream**: governance

## Outcome

Clarify when existing session authority is sufficient, require inspection of an
actual blocker and non-destructive alternatives before escalation, and repair
overlap detection that confuses common committed history with a second writer.

## Acceptance criteria

- [x] AC-01: Identical-head and ancestor snapshots with no competing delta do not block the active writer; two actual dirty writers remain blocked.
- [x] AC-02: Agent guidance preserves prior authorization, isolates blocked effects and requires concrete questions only for missing authority.
- [ ] AC-03: Managed package carries the same guidance to adopters, with tests and governance passing.

## Coordination

Pre-existing ticket-183 changes in the primary checkout are preserved. Its
BACKLOG does not reserve execution scope; physical changed files still require
independent conflict checking. No quarantine cleanup is part of this ticket.

## Validation and remaining publication

The overlap suite (including equal-head quarantine, ancestor, two-dirty-writer
and competing descendant cases), adoption-lock suite, rule-enforcement suite,
agent-host suite and governance-validator suite pass. The managed hub gate and
whitespace checks pass. A read-only run of the repaired checker against the
reported website incident passes with zero conflicts and preserves the unknown
snapshot. Existing unrelated legacy hub inventory findings remain recorded
externally; no foreign checkout or primary dirty data was changed.

The host installer was invoked and reports missing adopter-only .governance
runtime files in the hub; the existing hub ticket/material pre-commit hook and
core.hooksPath=.githooks remain active. No hook bypass or copied runtime was used.
Publish 0.20.6 through the protected delivery process before target adoption.
