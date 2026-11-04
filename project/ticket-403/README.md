# Ticket 403: Validate baseline-equivalent imported history

- **ID**: ticket-403
- **Owner**: agent:codex
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Created**: 2026-11-04

## Goal and scope

SESSION_EXECUTION_AUTHORIZATION: continue NP-024 and the user's
"kontynuuj,scalaj" instruction. Fixos exposed an old backup commit with
material bytes already in the target, incorrectly treated as this new
ticket's first implementation. Correct that distinction using Git objects,
not timestamps or author assertions. Preserve intent checks for every new
material state and for merge resolutions. No cleanup or migration authority
is created. Ticket402 owns separate bootstrap/version/CI paths; do not edit
or revert its work. Source publication precedes any governed consumer adoption.

## Acceptance criteria

- [x] AC-01: Equivalent imported material does not require a future intent; new material in a merge remains visible, including synthetic CI merges.
- [x] AC-02: Late intent, transient changes, non-equivalent imports, mode/deletion changes and Git failures remain rejected; protected migration exclusions retain their existing boundary.
- [ ] AC-03: Required registered regression harness, native governance, exact-head CI and independent publication pass.

## Result

The initial 12 real-Git regressions reproduced four failures before the patch.
A thirteenth case protects intent atomicity when a migration repair returns to
the ordinary base; verified migrations retain their separate baseline rules.
All 30 existing snapshot-migration regressions also pass. A read-only replay
of the actual preserved Fixos candidate reproduces the adopted rejection and
passes the candidate history check, without modifying consumer managed files.
Native governance passes with zero errors and warnings.

Goal's complete 23-check contract passed its first 19 stages in a private
mount namespace with checkout-local temporary storage and an unprivileged
interpreter. This filesystem boundary preserves the external-snapshot tests'
refusal to trust files in Git checkouts. Stage 20 stopped on missing build
prerequisites; a separate checkout-owned environment now contains the exact CI
build prerequisites. No required suite is waived and no full PASS is claimed.

Publication is blocked: the tracked distribution copy at
`packages/wellman/src/wellman/_bundled/governance_check.py` must accompany the
canonical source. It was incorrectly identified as ignored during initial
scope preparation. That path is outside this ticket's allocated scope; the
original rev1/fence1 lease projection remains unchanged. The delivery needs
native scope re-admission for this same ticket and checkout, adding only that
distribution copy and increasing the implementation-file budget to four.
The proposed exact scope, package delta and unchanged lease bindings are
preserved in the private NP-024 recovery outbox. No package source is edited
outside the current scope. Protected CI/review and publication remain pending.

This ticket advances no release version and does not claim consumer adoption
or disposal of preserved history. Ticket402 retains its release/version scope.
