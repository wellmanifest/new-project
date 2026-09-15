# Ticket 231: Validate one-time lossless snapshot migration contracts

- **ID**: ticket-231
- **Owner**: agent:codex
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Created**: 2026-09-14

## Goal and scope

EXT-02 owns the standard-level migration capability. Taskand owns its actual
migration and adopter changes. SESSION_EXECUTION_AUTHORIZATION: the user asked
on 2026-09-14 to execute the external-dependencies handoff sequentially and
confirmed the bounded migration authorization. This is execution authority,
not independent review or approval of a future head.

## Acceptance criteria

- [ ] AC-01: A source-preserving migration carries its new intent atomically,
  binds exact base/source/tree/inventory, and needs independent grant input.
- [ ] AC-02: Changed subjects, missing/consumed grants, lost history and added
  import files fail. New repairs retain the ordinary budget and every other gate.
- [ ] AC-03: Fixtures, governance, package and diagnostics checks pass; protected
  publication and adopter rollout have distinct evidence.

## Risks and boundaries

An inventory or local PASS never authorizes migration, review or merge. Keep
unknown primary changes and legacy worktrees intact. No source/test/script is
stored in this ticket; canonical guidance is docs/information/snapshot-migration.md.

## Authorized continuation: data impact classification

On 2026-09-14 the user requested the manifest and standard fixes and confirmed
that the previous codex-ext02 session had ended. Continue in this same scoped
worktree; preserve its snapshot-migration implementation. A pre-write backup
and actual controller lease are stored outside Git. This records execution
handoff only, not protected review or historical lease evidence.

AC-04: Explicit component-local state stays with its component workstream;
migrations, ownership transfers, unknown impact and legacy prose still require
integration. The local-state declaration never overrides shared-path ownership.
Run the dedicated regression tests and the complete governance fixtures. Ship
the schema, checker, diagnostic and runbook together in the existing 0.20.30
candidate, then adopt its immutable reviewed revision in target repositories.
