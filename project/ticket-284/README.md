# Ticket 284: Correct repository identity and continuous workspace overlap observation

- **ID**: ticket-284
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION

## Outcome and scope
Distinguish repositories on non-default ports, provide conservative complete inventory for overlap analysis, and detect dirty edits during the configured watcher interval. Source scripts, regression tests and immutable release 0.20.58 share this bounded S change.

## Acceptance criteria
- AC-01: Regression tests cover port identity, omitted/incomplete inventory and dirty linked-worktree overlap without topology changes.
- AC-02: Native governance, existing workspace checks and required protected CI pass.
- AC-03: Independent exact-head merge and final immutable 0.20.58 release are verified externally.

## Risks
Periodic read-only checking costs more than topology-only observation; the existing configured interval bounds its frequency. Inventory omission fails conservatively. No test fixture supplies execution or merge authority.

## Evidence
Raw logs and controller receipts remain in external operational storage. Tests belong in tests/workspace_observation_test.py. Protected approval is required independently of session authorization.
