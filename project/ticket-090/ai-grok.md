---
participant-id: agent:grok
participant: grok
role: agent
ticket: ticket-090
---
# Participant: grok (AI agent)

## Understanding

Markdown in `AGENTS.md` is not enough. Gemini and Antigravity write on a dirty
primary and skip `new-ticket.sh`. The fail-closed piece is a git hook plus
instruction files each host auto-loads. The installer is the distribution
path while leftover ticket-089 still owns `package-manifest.json`.

`--force-new` and `SESSION_EXECUTION_AUTHORIZATION` are recorded from the
human request to create this ticket and enforce the standard wherever an LLM
starts.

## Execution plan

1. Add GEMINI.md, CLAUDE.md, Cursor alwaysApply rule, and `.githooks/pre-commit`.
2. Add `scripts/install-agent-hosts.sh` for clone + user-level install.
3. Prove the hook and installer in `tests/agent-hosts.test.sh`.
4. Point AGENTS.md / AGENTS.template.md at the same contract.

## Actual changes

- Initialized ticket-090 with `--force-new` after explicit human request.

## Blockers

- None inside the recorded intent. Leftover ticket-089 stays untouched.
