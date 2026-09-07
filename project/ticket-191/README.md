# Ticket 191: Worktrees probe context adoption

- **ID**: ticket-191
- **Owner**: codex
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION

SESSION_EXECUTION_AUTHORIZATION: publish improvements to current Wellmanifest standards for parallel agents and adopt them in Subactor.

## Acceptance criteria

- [x] AC-01: Exact protected Worktrees 0.5.1 code and digest are distributed in new-project 0.20.9.
- [x] AC-02: Explicit checkout probe works outside a repository; existing layout v5 and host checks remain compatible.

Canonical documentation: [hidden worktree adoption](../../docs/information/hidden-worktree-adoption.md).

Validation: 10 Worktrees adoption tests; adoption-lock, agent-hosts, governance-validator, rule-enforcement and precommit-standard-update suites passed. Hub host activation is verified with no duplicate .governance runtime; missing sources are rejected. Managed governance and trusted documentation checker passed.
