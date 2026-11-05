# Ticket 406: Explicit existing-file acknowledgment in native upgrades

- **ID**: ticket-406
- **Owner**: agent:codex
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Created**: 2026-11-05

## Goal and scope

Continue canonical NP-028, dependency of Fixos PLF-21812. Native upgrade
allocation currently rejects independently pinned existing files that become
managed in the incoming package. The standard already supports exact
`managedTargetTakeovers` in reviewed adoption intents; expose this through
read-only planning and revalidate its committed state in native allocation.
The user's continuation, testing and merge request provides
SESSION_EXECUTION_AUTHORIZATION for this bounded repair, patch0.20.136,
required tests and independent protected publication.

## Acceptance criteria

- [x] AC-01: Exact acknowledged, committed governance-owned new managed files can be planned; default refusal remains.
- [x] AC-02: Native allocation recomputes the full plan and preserves intent/lease bindings; stale, foreign and malformed input fails before reservation.
- [ ] AC-03: All required source checks, exact-head protected merge and matching immutable release pass before production adoption.

Acknowledgments and allocation are not writer, takeover, execution, review or
merge authority. Old managed hash closure and foreign state remain protected.
