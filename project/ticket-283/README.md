# ticket-283: Reject malformed validation inputs and correct adopted guard paths

- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION

SESSION_EXECUTION_AUTHORIZATION: continued user instructions authorize necessary upstream repairs, testing and protected publication. Full NL adoption review and local reproductions confirmed invalid catalog type crashes, Boolean index acceptance, and a managed adopter command targeting a hub-only path.

## Acceptance criteria

- [x] AC-01: Malformed catalog inputs produce stable diagnostics; Boolean checkpoint sequences are rejected.
- [ ] AC-02: Managed adopter guard command resolves and executes; source/bundle parity, native gate and CI pass.
- [ ] AC-03: Independent exact-head merge and immutable 0.20.57 publication from clean merged source.

## Risk boundary

No execution authority, approval waiver, foreign-work cleanup or policy relaxation. The hub keeps its valid scripts/ guard command; only the managed adopter projection uses .governance/. Raw proof is stored externally.
