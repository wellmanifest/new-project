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
4. Replace the false C-DOCKER-004/presence-code mapping with the actual pin
   diagnostic and document exact grammar/remediation.
5. Run focused, traceability and full Linux validation; stop before delivery.

## Actual changes

- Initialized the bounded ticket and recorded `SESSION_EXECUTION_AUTHORIZATION`
  from the request to execute this work.
- Reproduced the missing enforcement on `algitex`: unpinned Docker/Compose
  references pass both the governance gate and Docker static build check.
- Full validation exposed that C-DOCKER-004 was marked deterministic through
  the unrelated presence-only code; amended scope to repair traceability.
- Added dependency-free, line-aware scans for Dockerfile `FROM` and Compose
  scalar `image:` references when Docker is required.
- Allowed immutable SHA-256 references, scratch and build-only services while
  rejecting tags, variables and malformed/uppercase digests.
- Added `GOV-DOCKER-002`, exact location regressions and corrected
  C-DOCKER-004 traceability.
- Passed focused validator, rule audit and the complete Linux CI contract.

## Blockers

- None; the bounded local objective is complete.
- New authority is still required for destructive action, secret access, new
  external coordination, material objective expansion and trusted merge.
