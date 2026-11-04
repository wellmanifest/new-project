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
The gate on the first local commit reported `GOV-BUDGET-001`: the manifest
counts `scripts/governance_check.py` as a public surface. Its budget is now
one, with the behavior correction explicitly declared; signatures are unchanged.

Goal's complete 23-check contract passed its first 19 stages in a private
mount namespace with checkout-local temporary storage and an unprivileged
interpreter. This filesystem boundary preserves the external-snapshot tests'
refusal to trust files in Git checkouts. Stage 20 stopped on missing build
prerequisites; a separate checkout-owned environment now contains the exact CI
build prerequisites. No required suite is waived and no full PASS is claimed.

The tracked distribution copy at
`packages/wellman/src/wellman/_bundled/governance_check.py` now accompanies the
canonical source byte-for-byte through the existing bundle generator. It was
incorrectly identified as ignored during initial scope preparation. The user's
continuation covers the persisted bounded correction: that one distribution
path, a four-file implementation budget and one declared public surface.
The same live owner applied a descriptor-bound CAS using the native transition
contract and filesystem primitives. The advisory allocation projection moved
from rev1/fence1 to rev2/fence2; its original expiry remains unchanged. The
immutable preparation and accepted transition records preserve both plans.
No ownership transfer or protected approval is inferred from this local record.
Exact committed governance, complete source-hub qualification, protected CI and
independent publication must still pass before this ticket is complete.

This ticket advances no release version and does not claim consumer adoption
or disposal of preserved history. Ticket402 retains its release/version scope.
