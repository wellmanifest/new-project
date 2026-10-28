# Ticket 385: Release a finished local lease through explicit current-owner handoff

- **ID**: ticket-385
- **Owner**: agent:codex
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Created**: 2026-10-28

## Goal and scope

SESSION_EXECUTION_AUTHORIZATION: continue user-requested autonomy repair, tests
and protected publication. This standard-maintenance slice belongs to existing
wellmanifest/new-project #538; actual product rollout remains Willman #430.

Provide a local controller operation that accepts an explicit current-owner
handoff with exact lease bytes, revision/fencing and a recorded, Git-verified
merged receipt. Reuse canonical transitions, preserve receipts for crash replay,
and refuse unknown owners, registered controllers, invalid phases or stale state.
Never turn expiry or missing worktrees into authority. Legacy completed records
require separate controller reconciliation. Worktree/branch deletion is separate.

## Acceptance criteria

- [x] AC-01: Exact current-owner terminal handoff releases canonically; mismatched, missing, nonterminal and stale evidence refuses without lease mutation.
- [x] AC-02: Write-ahead replay is idempotent, changed inputs refuse, unsafe paths and concurrent transitions stay protected.
- [x] AC-03: Managed adoption registration, scoped tests and native governance pass before protected publication.

Local validation: 13 controller/CLI cases (including an isolated adopted copy)
and 15 canonical lease regression cases pass; scoped coverage records all 13
controller cases. Governance passes. The owner amended scope to include the
required existing Linux/Windows CI jobs; fresh work-start admission accepted
that disjoint verification path. No lease metadata or protected check changed.
Nine Testless suggestions remain external advisory data, not published tasks.
Exact-head hosted platform checks, local verification and independent Validator
approval remain required before publication. This slice does not complete all
of #538: legacy malformed-state reconciliation and workspace cleanup remain.
