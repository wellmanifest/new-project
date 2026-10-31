# Ticket 390: Prevent governance imports from creating bytecode in managed worktrees

- **ID**: ticket-390
- **Owner**: agent:codex
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT

SESSION_EXECUTION_AUTHORIZATION: user requested investigation, fixes and independent protected merges. This scoped prerequisite is NP-018 for NP-017/ticket-388.

## Goal and scope

Keep managed checks read-only while dynamically importing trusted validators; synchronize source and bundled runtimes. Preserve all scope and lease gates.

## Acceptance criteria

- [ ] AC-01: Both actual scheduled workflows pass with an isolated installed runtime and create no bytecode in the managed worktree.
- [ ] AC-02: Governance and relevant package tests pass; protected OneDev and an independent Validator remain required for delivery.

## Validation and publication boundary

- The unmodified base reproduced both scheduled workflow failures with `GOV-SCOPE-001` caused by generated managed-check bytecode.
- The installed runtime package suite passes; the nine range tests also pass independently on Python 3.11 and 3.13. Governance and bundled-source consistency pass.
- Release projection paths have a separate pending owner delta in ticket-389; work-start reports `HANDOFF_REQUIRED`. No release version or foreign change was modified. Protected OneDev and Validator remain required.
