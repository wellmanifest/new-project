# Ticket 387: Preserve unmerged branches

- **ID**: ticket-387
- **Owner**: agent:codex
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Created**: 2026-10-31

## Goal and scope

Closing an unmerged PR preserves its branch. Replace the distributed deletion
workflow with a read-only notice; GitHub's repository setting handles deletion
after merge. Execute the embedded script across ticket, long-lived, default,
merged and fork events. Release version 0.20.121 and its projections belong to
this same seven-file implementation slice (class S, estimate 20 minutes).

## Acceptance criteria

- [x] AC-01: Closing an unmerged PR invokes no branch-write API.
- [x] AC-02: Workflow has read-only permissions and is excluded from required pre-merge checks.
- [ ] AC-03: Complete all source-hub checks and protected exact-head publication.

## Session authorization

SESSION_EXECUTION_AUTHORIZATION: user requested correction of standards needed
for operational multipacks and repeated continuation with protected merging.
Fix the semantic source; do not edit managed adopter copies by hand.

## Validation

Branch/adoption/bootstrap regressions: 104 passed, 1 skipped, 35 subtests.
The gate for the entire prepared file inventory passed without errors or
warnings. The installed Goal API supports a 900-second per-command budget;
it executes all 23 checks and owns its cache. Provisioned an isolated runtime
with the CI build/schema dependencies and PyYAML. Installed-wheel and overlap
guard regressions pass there. Full-contract and protected delivery receipts
remain external; neither a local pass nor this ticket grants merge approval.
