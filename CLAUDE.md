# CLAUDE.md — wellmanifest/new-project

Same contract as `GEMINI.md` and `AGENTS.md`. Claude Code must follow it
even when this session did not start in Cursor.

1. Read `AGENTS.md` first.
2. Allocate with `./project/new-ticket.sh` only. Never copy ticket directories.
3. Use a `ticket-NNN` branch/worktree. Do not write on `main` or a dirty primary.
4. Stay inside `intent.json` `allowedPaths`.
5. Run `./scripts/install-agent-hosts.sh` once per clone, then `./project/governance-check.sh` before done.

The git hook rejects unbound commits. Markdown is not a substitute for the hook.
