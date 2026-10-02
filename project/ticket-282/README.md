# ticket-282: Bind snapshot entry proofs to the opened descriptor

- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION

SESSION_EXECUTION_AUTHORIZATION: the user requested continued fixes, testing and protected merges. Independent review of the NL adoption exposed a stat/open race in the canonical standard runtime; this material correction belongs in the standard source.

## Acceptance criteria

- [x] AC-01: Stable mode/hash proof with deterministic replacement and mutation race tests.
- [ ] AC-02: Canonical and bundled runtime match; native governance and required CI pass.
- [ ] AC-03: Independent merge and immutable 0.20.56 publication from clean merged source.

## Risk boundary

No migration grant, merge authority, destructive scope expansion or policy relaxation is introduced. External raw evidence stays outside Git.
