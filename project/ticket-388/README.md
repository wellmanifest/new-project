# Ticket 388: Fix trusted governance runtime bootstrap for both entrypoints

- **ID**: ticket-388
- **Owner**: agent:codex
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION

SESSION_EXECUTION_AUTHORIZATION: the user requested continued fixes, tests and independent protected merges. The managed idle-takeover receipt binds this continuation to revision/fence 7.

## Goal and scope

Resolve exactly one supported installed governance distribution and its matching console entrypoint inside the isolated environment. Probe its version before exporting PATH; reject missing, ambiguous or malformed identity and failed probes. Preserve protected source-pin selection and independent publication authority.

## Acceptance criteria

- [x] AC-01: Eight real-venv installer tests pass for legacy and modern runtime entrypoints and invalid identities.
- [ ] AC-02: Local checks pass; protected OneDev, required hosted checks and independent Validator approval must still precede merge.

## Validation

Full Python suite: 681 passed, 4 skipped, 807 subtests passed. Source-hub preflight: all 23 checks passed (56 JSON documents, 22 shell suites). A parallel preflight hit an embedded test timeout; that test passed in the full suite and the complete sequential preflight. No timeout or test was weakened.

Prerequisite ticket-390 is independently merged as PR551 at `4850b60a4b24c4102e5b861fe54354e8a92c60c1`, the accepted base. Release projections remain with their existing owner; this material change uses Goal commit-only delivery.
