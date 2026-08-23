# Ticket 115: Fix Windows pre-commit executable check and publish 0.18.6

- **ID**: ticket-115
- **Owner**: agent:gemini under SESSION_EXECUTION_AUTHORIZATION
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Created**: 2026-08-23

## Goal and scope

Fix `agent_host_check.py` to guard the POSIX executable check on `.githooks/pre-commit` with `os.name != 'nt'`, preventing false positive test failures on Windows CI.
Publish standard release `0.18.6`.

## Acceptance criteria

- [ ] AC-01: `bash tests/agent-hosts.test.sh` passes.
- [ ] AC-02: `bash tests/adoption-lock.test.sh` passes.
- [ ] AC-03: Governance gate passes on exact head.

## Participants

- Human participant: authorized via active session.
- Agent participant: [ai-gemini.md](ai-gemini.md)
