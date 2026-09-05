# Ticket 189: Local worktree identity

- **ID**: ticket-189
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Workstream**: governance

## Outcome

A regression fixture without origin accepted two dirty writers: identity used
each checkout path rather than Git's shared common directory. Fix this actual
local-repository gap and retain conservative overlap and read-only inventory.
Release 0.20.7 with an annotated tag bound to its protected merge. The prior
0.20.6 release tag lacks an annotation and is not accepted for adoption; it is
preserved rather than moved.

## Acceptance

- [ ] AC-01: Two linked local writers without origin produce a conflict; inert same-head snapshots still pass.
- [ ] AC-02: Governance and regression suites pass; publication uses protected exact-head validation and an annotated immutable tag.

The added no-origin fixture failed against the prior implementation with “local worktrees without origin escaped overlap detection”. The fix uses the shared Git common directory, keeping independent local repositories separate. Goal runs the full configured validation before publication.
