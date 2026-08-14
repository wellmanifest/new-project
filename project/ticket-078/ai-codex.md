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
- Added optional closed placement fields to the intent schema and matching
  deterministic validation for HOME, shape, runtime owner and adopted packs.
- Added policy, procedure, hub/target instructions, enforcement mapping and
  regression coverage without changing the v0.17.0 release carriers.
- Passed the complete local Hub test contract, Ruff 0.15.21 and the current
  ticket scope gate.
- Committed the bounded implementation as
  `04715d71aa5c5aa822eb45217d51412fbc563688` and entered `PUBLICATION` after
  the exact committed diff passed the deterministic gate.
- Goal published PR #120 at exact head
  `aa7e15f2a6a4c8471b844fd658d4c605f1780d89`; all Linux and Windows checks
  passed, the trusted Validator App approved that head, and the protected
  flow merged it as `335b0f1975c4c9d3f2f99aeeeaba109a2cc41c2d`.
- Closed this ticket only from the integrated default branch. The mechanical
  version bump, tag and immutable release remain owned by a separate ticket.
- Unified the split: published contract is `origin/main@335b0f1` from
  `goal/ticket-078`. Recovery branch `ticket/078-home-adopt-placement`
  stays unmerged (out-of-scope `llms.txt`). Closure docs live on
  `ticket/078-placement-closure` and are not re-merged to `main` this
  session per founder instruction.

## Blockers

- Founder forbade opening a PR or merging ticket-078 onto `main` in the
  follow-up session; PR #120 had already landed. Closure evidence is
  pushed on the ticket branch only. Release publication remains outside
  this ticket's write scope.
