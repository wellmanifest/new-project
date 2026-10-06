# Ticket 311: Fresh native adoption bootstrap

- **Owner**: agent:codex
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION

SESSION_EXECUTION_AUTHORIZATION: continue scanner fixes using native tickets and canonical worktrees. The existing first-allocation acknowledgement requires a committed legacy scaffold and cannot recover a repository with no manifest. Add an explicit fresh mode with original-HEAD absence and exact installer-byte binding; retain controller, WIP, pin and independent publication checks.

- [x] AC-01: Real first allocation works for a fresh repository; malformed state and foreign overlaps refuse.
- [x] AC-02: Native governance and affected regressions pass.
- [ ] AC-03: Independent publication precedes any target use.

Validation: the complete adoption-lock gate passed, including 14 adopter cases and 11 nested fresh-allocation cases. The existing work-admission suite and native governance passed. Published release and independent delivery remain pending.
