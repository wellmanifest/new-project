---
participant-id: agent:codex
participant: codex
role: agent
ticket: ticket-085
---
# Participant: codex (AI agent)

## Understanding

The requested `events/` skeleton is useful only if it cannot become a second
authority beside command handlers, protobuf files or prose. The bounded source
contract therefore needs one semantic registry: `operations/index.json` owns
command/query identities and their permitted effects; `events/index.json` and
`error/index.json` catalog facts and rejections referenced by that registry;
models describe payload shape only. A deterministic graph check, not an LLM,
enforces these boundaries.

`new-project` governs both domain standards and ordinary application
repositories. Making the folders unconditional for all targets would be a
breaking and conceptually incorrect migration. The manifest remains backward
compatible and exposes an explicit `none`/`cqrs` mode; Wellmanifest standards
adopt `cqrs` through their own bounded tickets.

## Execution plan

1. Bind the ticket to integrated `main` and constrain it to the manifest
   contract, deterministic checker, regression shell and managed prose.
2. Add the closed `domainContracts` schema and a default non-domain mode while
   reserving canonical integration ownership paths.
3. Validate the CQRS catalogs and their command/query/event/error graph with
   fail-closed, repository-relative reads.
4. Add positive, compatibility and adversarial regressions.
5. Document the sole-source and transport-model boundaries in managed agent and
   policy guidance.
6. Run the full Linux contract, source-hub scope gate and protected exact-head
   delivery.

## Actual changes

- Initialized the bounded ticket and recorded `SESSION_EXECUTION_AUTHORIZATION`
  from the request to execute this work.
- Selected `operations/index.json` as the sole C/Q authority; event, error and
  model catalogs may reference it but may not redefine operations.
- Chose an explicit opt-in so domain standards can make the skeleton mandatory
  without imposing CQRS on ordinary target applications.

## Blockers

- None inside the recorded intent; proceed without a second confirmation.
- New authority is still required for destructive action, secret access, new
  external coordination or material objective expansion. Protected delivery
  may be invoked without another prompt when publication is in scope; its
  exact-head trusted approval remains independent evidence.
