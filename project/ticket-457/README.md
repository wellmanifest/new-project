# Ticket 457: Resume released canonical leases through protected handoff

- **ID**: ticket-457
- **Owner**: agent:codex / codex-np053-released-resume-20261118t0605z
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Created**: 2026-11-18

Planfile: NP-053, related issue #538. This bounded slice adds an explicit
released-slot resume operation; it does not complete the broader cleanup issue.
SESSION_EXECUTION_AUTHORIZATION: the user requested continued autonomous fixes,
tests, delegation and protected publication. Merge remains the independent
controller's decision for the exact reviewed HEAD.

Reuse the anchored handoff transaction. Require independently authenticated
old-writer release or controller-observed stopped state, the exact full request,
current worktree/index/intent snapshot and old lease CAS. Resume only the same
ticket/branch/worktree with a fresh bounded session and monotonic fencing.
Preserve unfinished dirty work. Legacy basename identity can map only to the
exact canonical origin in this explicit released mode. Ordinary handoff remains
strict. Request labels, JSON, FD, expiry and lack of a PID grant no authority.

## Acceptance criteria

- AC-01: Protected released resume preserves scope, birth plan, current dirty
  payload and HEAD while advancing the canonical lease and bounded session.
- AC-02: Wrong identity/state/proof, changed snapshot or policy, unsafe paths,
  known completed delivery, races and replay drift are refused without loss.
- AC-03: Meaningful real-Git regressions, full qualified suite, native and
  hosted platform gates, and independent exact-head review precede publication.

No consumer source or lease changes belong to this standards ticket. Source
implementation is bounded by the original stage deadline below; checks and
publication continue with the source frozen.

Stage deadline: 2026-11-18T06:33:08+00:00.
