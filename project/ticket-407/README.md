# Fix managed Git hook enforcement

- **ID**: ticket-407
- **Owner**: agent:codex
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION

SESSION_EXECUTION_AUTHORIZATION: user continue, merge and test Maskservice campaign; required source-owner repair NP-029.

## Acceptance criteria

- AC-01: Every ticket-bearing ref is fenced before profile exceptions; malformed/unreadable or explicitly invalid target declarations refuse, absence-only fallback retained. Real Git regressions preserve remote refs and local HEAD.
- AC-02: Live/template parity, native gate, real full source CI and independent exact-head App review before immutable137 publication. Consumers remain frozen separately.
