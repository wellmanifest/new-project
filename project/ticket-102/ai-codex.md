---
participant-id: agent:codex
participant: codex
role: agent
ticket: ticket-102
---
# Participant: codex (AI agent)

## Understanding

Platform already tracks `.governance/worktree_overlap_check.py` from an earlier
pilot. Standard 0.18.2 starts managing that target and also changes one lint-only
line, so the deterministic gate rejects the upgrade as a replacement. A broad
exception would permit content laundering. The safe missing primitive is
explicit exact-path, exact-base-digest takeover authorization in the ticket DSL.

## Execution plan

1. Bind the reproduced failure and the smallest intent-contract extension.
2. Commit this plan before changing validator or schema code.
3. Add strict syntax, duplicate and lifecycle validation for takeover entries.
4. Verify base bytes, require exact consumption and preserve head hash checks.
5. Add positive and fail-closed mutation fixtures.
6. Run the full validator suite and exact-base governance, then use Validator.

## Actual changes

- Initialized the bounded ticket and recorded `SESSION_EXECUTION_AUTHORIZATION`
  from the request to execute this work.
- Added optional `managedTargetTakeovers` entries with strict exact-path and
  lowercase SHA-256 syntax, duplicate rejection and no initial-adoption use.
- Bound every declaration to bytes read from the accepted Git base and require
  every declaration to be consumed by one changed, newly managed target.
- Preserved immutable head-lock verification and the default rejection when no
  matching takeover exists.
- Added positive, missing, wrong-digest, unused and duplicate regression cases;
  the full deterministic validator suite passes.

## Blockers

- None inside the recorded intent; proceed without a second confirmation.
- New authority is still required for destructive action, secret access, new
  external coordination or material objective expansion. Protected delivery
  may be invoked without another prompt when publication is in scope; its
  exact-head trusted approval remains independent evidence.
