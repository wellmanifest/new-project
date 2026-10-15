# Ticket 346: Isolate non-Git fixtures from ancestor repository discovery

- **ID**: ticket-346
- **Owner**: agent:codex
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Created**: 2026-10-15

SESSION_EXECUTION_AUTHORIZATION: continued repair of standard enforcement and
bounded release preparation. Parent PLF-15925/PLF-15926; concrete issue PLF-15928.
Native allocation reserves this identity only. Implementation waits for exact
controller admission and authentic fencing.

The actual hardened Goal dry-run after merge345 found that non-Git fixtures
inside owning-repository TMPDIR inherit the ancestor source hub Git context.
Bound discovery at their parent so bootstrap-only cases remain non-Git while
registered nested repositories keep their own identity. Preserve production
allocator semantics, old runtime state and all foreign worktrees.

- [x] AC-01: Existing governance suite passes with repository-owned TMPDIR,
  including non-Git bootstrap and registered/nested Git scenarios.
- [ ] AC-02: Material fixture fix passes scope/governance and independent
  exact-head required CI/App approval/merge.

No runtime deployment, standard tag/Release or adopter operation belongs to
this slice. Private proof, proposed diff and registration data remain in this
worktree's ignored `.subactor/receipts/ticket-346/`.

Local validation: native suite exit 0 (19 allocation and 94 work-start tests),
shell syntax, intent schema and scope/governance gate. Protected publication
remains pending; status stays IN_PROGRESS.
