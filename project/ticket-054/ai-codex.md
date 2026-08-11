---
participant-id: agent:codex
participant: codex
role: agent
ticket: ticket-054
---
# Participant: codex (AI agent)

## Understanding

Live adoption in `semcod/code2logic` exposed two Compose `image:` values that
name local build outputs. Exempting every service with `build:` would be
unsafe, because Compose can still pull its `image:` according to pull policy.
The precise safe contract is a direct service-level `build:` paired with
`pull_policy: build`; every other mutable reference remains blocked.

## Execution plan

1. Commit this bounded plan before implementation.
2. Base the implementation on ticket 052's immutable-image rule.
3. Add a small indentation-aware, dependency-free parser for direct Compose
   service keys and exempt only explicit build-only services.
4. Add passing and fail-closed regressions for pull-policy combinations.
5. Run focused and complete Linux contracts, then integrate the commit into
   the combined downstream candidate.
6. Upgrade the isolated code2logic pilot through Goal and confirm all six
   current mutable references remain visible.
7. Record evidence and stop before external delivery.

## Actual changes

- Initialized the bounded ticket and recorded `SESSION_EXECUTION_AUTHORIZATION`
  from the request to execute this work.
- Reproduced the live ambiguity in code2logic: two local build output tags,
  three Dockerfile bases and one external Compose image are all mutable.

## Blockers

- None inside the recorded intent; proceed without a second confirmation.
- New authority is still required for destructive action, secret access, new
  external coordination, material objective expansion and trusted merge.
