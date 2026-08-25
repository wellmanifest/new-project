---
participant-id: agent:codex
participant: codex
role: agent
ticket: ticket-125
---
# Participant: codex (AI agent)

## Understanding

The Subactor Orchestrator adoption published a base package and lock that list
four host/CI targets as managed while the accepted Git tree lacks those files
because legacy ignore rules hid them. The current upgrade validator rejects
this inconsistent base, correctly, but offers no explicit recovery primitive.
Automatic acceptance would hide corruption; the narrow missing contract is a
digest-bound restoration declared by the current ticket.

## Execution plan

1. Freeze the accepted base and define the exact upgrade-only restoration
   contract before implementation.
2. Extend intent schema and deterministic validation with mandatory exact
   consumption and no overwrite path.
3. Add positive and adversarial fixtures for all base/head combinations.
4. Run all standard suites, lint and exact-base governance.
5. Publish through a PR and independently dispatch Validator for the frozen
   exact head; do not include the release in this ticket.

## Actual changes

- Initialized the bounded ticket and recorded `SESSION_EXECUTION_AUTHORIZATION`
  from the request to execute this work.
- Added strict `managedTargetRestorations[{path,baseDigest}]` validation without
  changing the existing default failure for missing managed targets.
- Required both base manifests to retain managed ownership, exact accepted-base
  absence, exact old lock digest, exact new payload digest and one-time
  declaration consumption.
- Added positive and adversarial regression coverage for omitted, wrong,
  duplicate, unused, overlapping and initial-adoption bindings.
- Documented the recovery boundary and ran every Linux CI shell suite plus
  schema, syntax and diff hygiene checks.

## Blockers

- None inside the recorded intent; proceed without a second confirmation.
- New authority is still required for destructive action, secret access, new
  external coordination or material objective expansion. Protected delivery
  may be invoked without another prompt when publication is in scope; its
  exact-head trusted approval remains independent evidence.
