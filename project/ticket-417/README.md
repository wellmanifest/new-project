# Ticket 417: Reject malformed adoption binding registry inputs

- **ID**: ticket-417
- **Owner**: agent:codex
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT

SESSION_EXECUTION_AUTHORIZATION: the user requested continuing issue remediation, testing and protected merging. This is one bounded part of NP-039 / wellmanifest/new-project#583.

## Goal and scope

Treat non-object adoption-binding registries and non-string path entries as invalid without raising an unhandled exception. Preserve acceptance of valid registries and keep the hub and distributed checker byte-identical.

## Acceptance criteria

- [x] AC-01: Both checker copies reject malformed registries and path lists, including unhashable entries, and still accept valid registries.
- [ ] AC-02: Required source tests, governance and independent exact-head publication checks pass.

This ticket does not claim to resolve other findings in issue 583 or to update any consumer installation.
