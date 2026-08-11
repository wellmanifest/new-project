---
participant-id: agent:codex
participant: codex
role: agent
ticket: ticket-056
---
# Participant: codex (AI agent)

## Understanding

Pilots `fixop` and `gillm` independently lacked the target-owned `TODO.md`.
Goal correctly planned the managed governance package but did not reveal that
the resulting repository would still fail the required-file gate. The package
already carries the authoritative target manifest, so its adoption generator
can calculate readiness without moving policy into Goal or owning target files.

## Execution plan

1. Add a small pure resolver for missing required files after planned payloads.
2. Emit deterministic `MISSING target prerequisite` lines in check and write
   modes while preserving adoption/drift exit codes.
3. Extend the adoption fixture to distinguish managed planned files from
   target-owned prerequisites and prove warning resolution.
4. Document the informational contract at the Goal entrypoint.
5. Run focused and complete Linux contracts, Ruff, then recheck a real isolated
   downstream pilot.

## Actual changes

- Initialized the bounded ticket and recorded `SESSION_EXECUTION_AUTHORIZATION`
  from the request to execute this work.
- Confirmed from `fixop` and `gillm` that the current preflight omits missing
  target-owned `TODO.md`; `gillm` otherwise passed 163 workspace tests.
- Verified that Goal already dispatches to the pinned package generator, so no
  Goal-side policy duplication is needed.

## Blockers

- None inside the recorded intent; proceed without a second confirmation.
- New authority is still required for destructive action, secret access, new
  external coordination, material objective expansion and trusted merge.
