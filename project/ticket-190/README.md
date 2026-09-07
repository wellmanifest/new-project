# Ticket 190: Adopt hidden repository-local worktrees v5

- **ID**: ticket-190
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Created**: 2026-09-07

## Goal and scope

SESSION_EXECUTION_AUTHORIZATION: the user requested implementation and rollout of `[repo]/.worktrees/<ticket>--<slug>` in the related standards. Adopt the protected Worktrees v5 package, align managed instructions, bootstrap and inventory consumers, validate and publish through the protected delivery process. This also authorizes bootstrapping this ticket in the requested new layout. Preserve pre-existing dirty primary changes and historical worktrees.

Canonical result: [hidden worktree adoption](../../docs/information/hidden-worktree-adoption.md).

## Acceptance criteria

- [ ] AC-01: An installed package plans repository-local hidden worktrees, emits v5 inventories with v4 legacy entries, preserves relative links after relocation, and leaves `.subactor/manifest.json` tracked.
- [ ] AC-02: Governance and the hub test contract pass; immutable publication and adopter readback are observed separately.
