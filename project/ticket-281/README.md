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

27 recovery tests pass, including exact published alias recovery and rejection of divergent origin, duplicate identity and foreign remote. Native governance gate: GOV-PASS (0 errors, 0 warnings). Recovery does not grant merge approval.

- [ ] AC-03: Publish immutable standard 0.20.55 only after trusted merge and clean merged-source verification; verify the annotated tag and final GitHub Release.

Version projections join the material recovery fix in this same ticket. PR415 was withdrawn to draft and its previous frozen controller lease was cancelled and released before extending scope. No product adoption is performed from an unpublished revision.

The published alias is rechecked under the existing controller lock: a matching remote ref changed between observations is rejected before identity reservation. VERSION and wellman package version both declare 0.20.55. Release publication remains pending trusted merge and clean-source retest.
