# Ticket 423: Support pre-0.20.30 adoption plan helpers and Wellman profile scaffolds

- **ID**: ticket-423
- **Owner**: agent:antigravity
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Created**: 2026-11-11

## Goal and scope

SESSION_EXECUTION_AUTHORIZATION: the user requested autonomous verification,
protected PR merging, testing, and bottleneck repair (`kontynuuj,scalaj,testuj, naprawiaj`).
Live ecosystem upgrades exposed two deterministic adoption bottlenecks:

1. **Pre-`0.20.30` `--standard-adoption-plan` helper resolution (`heyasa/taskand` at `0.20.16`)**:
   When invoking `<immutable-source>/project/new-ticket.sh --standard-adoption-plan <plan.json>`
   from a genuine pre-`0.20.30` adopter checkout, `project/new-ticket.sh` resolves
   `ticket_storage.py`, `ticket_activity.py`, `ticket_allocation.py`, `work_start_check.py`,
   and `worktree_path_check.py` only inside `$PRIMARY_CHECKOUT` (`.governance/*` / `scripts/*`),
   failing with `GOV-WORK-START-001: managed work-start checker is missing` on `0.20.16`
   targets whose committed `manifest.lock.json` predates those helpers. After
   `verify_standard_adoption` verifies the complete immutable source helper closure
   against `git_bytes(standard_root, revision, ...)`, `project/new-ticket.sh` must fall back
   to `$ALLOCATOR_PACKAGE_ROOT` when the target lacks those helpers, while continuing to
   reject damaged modern targets via `manifest.lock.json` digest closure.
2. **Minimal Wellman profile scaffold migration (`heyasa/task2willmux` at `0.20.38`)**:
   `scripts/create_adoption_lock.py:validate_wellman_scaffold` hardcoded
   `standard["id"] == "profile:baseline"`, rejecting valid minimal policy-free Wellman
   profile scaffolds (`profile:runtime-service`, `profile:domain-pack`, `profile:agent-executor`,
   `profile:deployment`, `profile:embedded-fleet`, `profile:full`). Accept the closed set of
   canonical Wellman scaffold profile IDs while continuing to reject native, custom, or
   unrecognized manifests.

## Acceptance criteria

- [x] AC-01: `verify_allocation_plan` verifies byte-integrity and non-symlinked paths for
  the immutable source allocator helper closure against `git_bytes(standard_root, revision, ...)`,
  and `project/new-ticket.sh --standard-adoption-plan` falls back to `$ALLOCATOR_PACKAGE_ROOT`
  helpers on genuine pre-`0.20.30` adopters without weakening damaged-lock rejection.
- [x] AC-02: `validate_wellman_scaffold` accepts the closed canonical set of minimal Wellman
  scaffold profile IDs (`profile:baseline`, `profile:domain-pack`, `profile:runtime-service`,
  `profile:agent-executor`, `profile:deployment`, `profile:embedded-fleet`, `profile:full`)
  and continues to reject custom, native, and unknown manifests without writes.
- [x] AC-03: Unit/integration regressions in `tests/ticket-allocation-worktree.test.py` and
  `tests/adoption_legacy_scaffold_test.py`, `./project/governance-check.sh`, and `wellman check`
  pass cleanly.

## Risks and notes

- Risk 1: Falling back to unverified helpers before plan verification or masking damaged
  modern `.governance` installations. Mitigated by binding the full helper closure in
  `verify_allocation_plan` against `git_bytes(standard_root, revision, ...)` and resolving
  fallbacks only after `verify_standard_adoption` validates both source and target lock closure.

## Tracking boundary

This directory contains the minimal reviewed intent. Optional participant prose
and raw command logs remain outside the tracked repository.
