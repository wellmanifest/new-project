# GEMINI.md — wellmanifest/new-project

Fail-closed. Do not write code until this contract is followed.
This file is the Gemini / Antigravity entry. The same rules are in
`AGENTS.md`, `CLAUDE.md`, and `.cursor/rules/new-project-standard.mdc`.

1. Read `AGENTS.md` and `.governance/manifest.json` (or `governance/manifest.hub.json` in this hub).
2. Allocate tickets only through `./project/new-ticket.sh`. Never copy `project/ticket-*`.
3. Work on a branch/worktree whose name contains `ticket-NNN`. Never commit on `main` or a dirty primary checkout.
4. Stay inside that ticket's `intent.json` `allowedPaths`.
5. Do not edit commercial SSOT, offer, or brand facades unless this ticket is the declared integration workstream.
6. Run `./scripts/install-agent-hosts.sh` once per clone so the git hook is active.
7. Run `./project/governance-check.sh` before claiming done.
8. The pre-commit hook rejects commits that are not bound to an `IN_PROGRESS` `ticket-NNN`.

If any step is unclear: STOP. Do not invent a ticket number.
