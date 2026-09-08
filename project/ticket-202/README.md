# SQLite allocation and local commit checks

- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Authorization**: SESSION_EXECUTION_AUTHORIZATION — implement, test and publish the SQLite ticket workflow.

## Goal and scope

Wire the managed allocator and local hook to the Registry ticket store while retaining clone-wide reservation and independent CI input.

## Acceptance criteria

- [ ] AC-01: A real allocation and commit need no ticket directory; runtime tampering fails before allocation and legacy behavior remains covered.
