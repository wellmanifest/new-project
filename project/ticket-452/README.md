# Ticket 452: Admit bounded packaging scope for the current bootstrap owner

- **ID**: ticket-452
- **Owner**: agent:codex / codex-bootstrap-packaging-refresh-20261117t1705z
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Utworzono**: 2026-11-17

## Goal and scope

First native adoption installs the governance contract but an existing package
marker may be outside the initial installer-only reservation. Its required
metadata cannot then be added under the original scope. The native allocator
has no amendment command and existing owner checkpoints preserve the scope.

Provide an explicit, narrow controller for the same live bootstrap owner.
Only existing literal packaging markers declared by the installed published
contract may be added. Keep the original expiry and source bytes, journal the
exact transaction, and advance fencing before exposing the amended intent.
The operation grants neither publication approval nor general scope expansion.

SESSION_EXECUTION_AUTHORIZATION: the user's ongoing request to repair, test and
complete autonomous API delivery. Coordination: PLF-27911 / PLF-27919.
The 30-minute estimate covers implementation; external verification and release
remain independently recorded stages.

## Acceptance criteria

- [x] AC-01: A real Git bootstrap fixture admits only its missing packaging scope under the current owner.
- [x] AC-02: Owner, CAS, expiry, freeze, file, peer and interrupted-replay negatives preserve unrelated state.
- [ ] AC-03: Native verification, independent approval and immutable published release precede production use.

## Delivery

Keep the implementation ticket in publication until the protected terminal
receipt records the actual result. No closure-only commit is required.

Validation: 16 controller regression tests passed, including managed installation,
peer contention, interrupted fencing/replay and effect-boundary source drift.
The controller also binds the lease HEAD, shares the native allocator lock,
and refuses a rewritten target contract that names product source as packaging.
Native governance and bundled checker parity passed. Full source-hub checks,
exact-head CI, independent approval and final release remain publication gates.
