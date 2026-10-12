# Ticket 336: Pin CI governance runtime to trusted immutable source

- **ID**: ticket-336
- **Owner**: agent:codex
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION

## Goal and authority

SESSION_EXECUTION_AUTHORIZATION: the user requested continued repairs, tests and
protected merges for the reviewed upstream defects blocking Coding Agent adoption.
Select a full immutable runtime SHA from the exact trusted base adoption lock or
protected NEW_PROJECT_RUNTIME_SHA configuration. Never use candidate version/tag
or execute a candidate helper before runtime selection. First adoption without a
trusted pin fails closed. Preserve isolated venv and nested target-root behavior.

## Acceptance criteria

- [x] AC-01: Both workflow installers exercise trusted base/config pins and refuse
  missing, malformed or untrusted pins before installation; candidate changes do
  not redirect runtime acquisition.
- [ ] AC-02: Runtime/PR range/package tests, full suites and governance pass.
- [ ] AC-03: Independent exact-head review, protected merge and 0.20.97 release.

## Bounds and risks

maxActiveMinutes: 30; checkpointMinutes: 25. Ten implementation/release files,
two components. No adopter or deployed configuration changes. A missing trusted
base lock needs a separately protected SHA; no candidate fallback is allowed.

## Validation

The prior installers failed 30 regression subcases. Runtime pin selection now
passes the six-method matrix, including malformed/duplicate locks and candidate
Python module shadowing. Seven installed PR gate tests, package build/install,
version parity and managed governance pass. Full Goal validation and independent
exact-head publication remain required.
