---
participant-id: agent:codex
participant: codex
role: agent
ticket: ticket-049
---
# Participant: codex (AI agent)

## Understanding

The atomic-adoption exception verifies upgrades by comparing package manifests
and locks on both sides. A first adoption has no base package or lock, so all
managed files fall back into ordinary implementation accounting and cannot fit
one workstream/ticket. The safe bootstrap distinction is whether each managed
target was absent in the accepted Git base.

## Execution plan

1. Add the explicit nullable bootstrap variant to intent v3 and its parser.
2. Validate absence of base package/lock, the immutable head binding and hashes.
3. Exempt only newly introduced managed targets; keep overwritten target files
   in ordinary scope, ownership and budget accounting.
4. Add positive and adversarial bootstrap regressions while preserving the
   existing upgrade matrix.
5. Document the bootstrap/upgrade distinction and run the full Linux contract.

## Actual changes

- Initialized the bounded ticket and recorded `SESSION_EXECUTION_AUTHORIZATION`
  from the request to execute this work.
- Reproduced `GOV-TICKET-005` on the live `glon` pilot because initial adoption
  has no base lock and therefore receives none of the existing upgrade
  transaction's managed-path accounting.
- Bounded the change to the intent contract, validator, its test suite and
  enforcement documentation.
- Added nullable `fromRevision` as an explicit initial-adoption declaration,
  while retaining exact full-SHA validation for every upgrade and target
  revision.
- Made bootstrap fail closed when the accepted base already has a package
  manifest or lock and verify the complete head package/lock/hash binding.
- Exempted only new managed targets absent from the accepted base; pre-existing
  target content remains in ordinary ticket, workstream and budget accounting.
- Added positive bootstrap and adversarial ownership/existing-lock regressions;
  the focused validator and full Linux CI contract pass.

## Blockers

- None; the bounded local objective is complete.
- New authority is still required for destructive action, secret access, new
  external coordination, material objective expansion and trusted merge.
