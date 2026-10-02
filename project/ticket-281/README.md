# Ticket 281: Preserve exact published branch aliases during fenced recovery

- **ID**: ticket-281
- **Owner**: agent:codex
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT

## Goal and scope

Permit fenced recovery of an already published canonical branch only when its origin tracking ref and the bound local HEAD are identical. Preserve all existing source, refs, controller fencing and collision checks.

## Acceptance criteria

- [x] AC-01: Exact origin alias recovers while preserving existing source and HEAD.
- [x] AC-02: Divergent origin, another remote, duplicate ticket branch and invalid controller are rejected without ticket creation.

## Risks

A matching commit alone does not establish identity or authority: the branch spelling, canonical origin remote and current controller lease must also match.

## Verification

26 recovery tests pass, including exact published alias recovery and rejection of divergent origin, duplicate identity and foreign remote. Native governance gate: GOV-PASS (0 errors, 0 warnings). Recovery does not grant merge approval.
