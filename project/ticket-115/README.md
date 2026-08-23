# Ticket 115: Fix Windows pre-commit executable check and publish 0.18.6

- **ID**: ticket-115
- **Owner**: agent:gemini under SESSION_EXECUTION_AUTHORIZATION
- **Status**: DONE
- **Workflow state**: DONE
- **Created**: 2026-08-23

## Goal and scope

Fix `agent_host_check.py` to guard the POSIX executable check on `.githooks/pre-commit` with `os.name != 'nt'`, preventing false positive test failures on Windows CI.
Publish standard release `0.18.6`.

## Acceptance criteria

- [x] AC-01: `bash tests/agent-hosts.test.sh` passes.
- [x] AC-02: `bash tests/adoption-lock.test.sh` passes.
- [x] AC-03: Governance gate passes on exact head.

## Publication evidence

- Pull request: `wellmanifest/new-project#192`
- Frozen and approved head: `26a320e5fc6990633625411d13b074ff0446bdeb`
- Merge commit: `01397097ac53a01b2dd544f0b5908d22d1b526d5`
- Tag & Release: `v0.18.6`
- Validator approval: review `5002443390`, run `32641347755`.

## Participants

- Human participant: authorized via active session.
- Agent participant: [ai-gemini.md](ai-gemini.md)
