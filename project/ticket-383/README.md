# Ticket 383: Observe integrated staged bytes without discarding pending work

- **ID**: ticket-383
- **Owner**: agent:codex
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Created**: 2026-10-27

## Goal and scope

SESSION_EXECUTION_AUTHORIZATION: continuation of user-requested cross-project intent improvement, coordination PLF-20321, existing dependency wellmanifest/new-project#473. Repair its verified work-start false positive through this standard owner; preserve foreign work and independent publication.

A detached ancestor checkout contains a staged allocator file byte-identical to target main. Work-start currently reserves its whole path as pending work. Observe remaining contributions without changing that checkout, its index, refs, ticket or lease. The exact target and stage-zero index mode/blob must agree with raw worktree mode/blob; any unknown or different evidence keeps the blocker. Named branches and unique commits retain current behavior. An advisory candidate never grants source ownership or publication.

## Acceptance criteria

- [x] AC-01: Exact integrated staged paths do not reserve scope; all dirty metadata and bytes remain visible and unchanged.
- [x] AC-02: Real deltas, active intent, index-only races, hidden worktree changes, mode/type drift and unknown ancestry remain protected.
- [ ] AC-03: Focused real-Git tests, governance and protected CI pass before independent review and merge.

## Delivery

Three material files, S/25 minutes, no dependencies or public-interface change. Native allocation owns canonical ticket-383 with actor agent:codex/session codex-cross-project-intent-20261027-admission, lease revision1/fence1. This does not adopt new allocator behavior in Intract or docs; the separate published adoption and primary-branch limitations remain.

## Validation

Baseline real-Git reproduction failed with RECONCILE for identical staged target bytes. After the fix, 103 work-start/recovery/bootstrap tests passed in 114 seconds and 4 controller-observation tests passed. Governance passed with zero errors and warnings; host hooks and diff whitespace checks passed.

A read-only query against the original detached checkout now reports NEW_TICKET_CANDIDATE for the integrated allocator path. Its staged index and both dirty source files remained byte-identical. This is candidate validation only: no source admission, cleanup, lease release or adopter rollout was performed. Protected test/windows-governance and independent Validator remain required for publication.
