---
participant-id: agent:codex
participant: codex
role: agent
ticket: ticket-052
---
# Participant: codex (AI agent)

## Understanding

The standard documents digest-pinned containers but currently checks only that
Dockerfile/Compose exist. Algitex therefore receives GOV-PASS with mutable base
tags and many `latest` services. The validator is dependency-free, so a narrow
grammar over the two normative image-reference locations is appropriate.

## Execution plan

1. Add a strict reusable image-reference predicate and location-aware scans.
2. Invoke them only for targets that require Docker; retain scratch/build-only
   Compose support.
3. Add the stable diagnostic and positive/adversarial fixture matrix.
4. Document exact supported grammar and remediation.
5. Run focused and full Linux validation; stop before delivery.

## Actual changes

- Initialized the bounded ticket and recorded `SESSION_EXECUTION_AUTHORIZATION`
  from the request to execute this work.
- Reproduced the missing enforcement on `algitex`: unpinned Docker/Compose
  references pass both the governance gate and Docker static build check.

## Blockers

- None inside the recorded intent; proceed without a second confirmation.
- New authority is still required for destructive action, secret access, new
  external coordination, material objective expansion and trusted merge.
