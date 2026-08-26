---
participant-id: agent:codex
participant: codex
role: agent
ticket: ticket-127
---
# Participant: codex (AI agent)

## Understanding

Current automation uses workspace-level, repo-local, parallel-root and nested
worktree layouts. `wellmanifest/worktrees` now defines the canonical placement
contract at immutable revision `bad8fab4ef96e770ccc4e4089bb4a3d623c1651a`.

## Execution plan

1. Bind the published source revision and exact contract bytes.
2. Package managed schema/checker/lock artifacts for generated repositories.
3. Add template guidance and deterministic adoption/drift tests.
4. Run package and governance gates, then use protected delivery.

## Actual changes

- Initialized the bounded ticket and recorded `SESSION_EXECUTION_AUTHORIZATION`
  from the request to execute this work.
- Vendored the published schema and pure conformance checker byte-for-byte.
- Added a revision/digest lock and three managed package entries.
- Added canonical-layout agent guidance and deterministic adoption tests.
- Documented the adoption under `Unreleased`; a coordinated package release
  remains outside this bounded ticket.
- Added a managed standard-pack routing map and documented HOME boundaries.
- Replaced duplicated Git/worktree/merge/validator/provider procedures with
  references to their canonical packs and adopter-owned runtime bindings.
- Added repository-role profiles over the existing S0-S5 enforcement model.
- Added a dependency-free adoption checker with immutable evidence, projection
  digest verification and staged audit/enforce behavior.
- Wired the checker into the managed governance workflow.

## Blockers

- None inside the recorded intent; proceed without a second confirmation.
- New authority is still required for destructive action, secret access, new
  external coordination or material objective expansion. Protected delivery
  may be invoked without another prompt when publication is in scope; its
  exact-head trusted approval remains independent evidence.
