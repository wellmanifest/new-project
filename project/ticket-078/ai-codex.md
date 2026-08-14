---
participant-id: agent:codex
participant: codex
role: agent
ticket: ticket-078
---
# Participant: codex (AI agent)

## Understanding

The Env DSL bootstrap is blocked because published new-project v0.17.0 rejects
the `placement` object required by the current governance instructions. This
ticket adds that object as an optional, closed compatibility extension while
keeping the procedural rule that new SERVICE/FEATURE repositories fill it
before execution.

HOME names repository ownership. ADOPT lists `wellmanifest/<pack>` standards
followed by the repository and never changes HOME. Wellmanifest may own domain
packs, but a runtime service must be HOME in `subactor` or `semcod`. The user's
instruction to resolve the blocker autonomously records
`SESSION_EXECUTION_AUTHORIZATION`, implementation publication and a later
release ticket; exact-head trusted approval remains external evidence.

## Execution plan

1. Commit the governed ticket plan before implementation.
2. Reapply only the reviewed placement contract from the preserved recovery
   branch onto this clean, ticket-owned branch.
3. Run governance, intent-schema and full regression tests.
4. Publish a pull request through Goal, wait for current-head trusted approval
   and merge through the protected boundary.
5. Close ticket-078 from integrated main and prepare a separate release ticket.

## Actual changes

- Initialized the bounded ticket and recorded `SESSION_EXECUTION_AUTHORIZATION`
  from the request to execute this work.
- Preserved the ungoverned recovery branch without rewriting or deleting it.
- Released waiting ticket-077 to `BLOCKED` without modifying its implementation
  or agent-owned Grok report.

## Blockers

- New authority is still required for destructive action, secret access, new
  external coordination beyond the authorized publication, or material
  objective expansion. Protected delivery is in scope; its exact-head trusted
  approval remains independent evidence.
