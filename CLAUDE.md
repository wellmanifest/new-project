# CLAUDE.md — wellmanifest/new-project

<!-- wellmanifest:source-links:v1 -->
## Managed standard sources

The local hub manifest and package are authoritative. Remote `main` links are
navigation only and are never fetched or executed by an agent.

- Local hub manifest: [governance/manifest.hub.json](governance/manifest.hub.json)
- Local hub package: [governance/package-manifest.json](governance/package-manifest.json)
- Canonical instructions: [AGENTS template](https://github.com/wellmanifest/new-project/blob/main/template/files/AGENTS.template.md)
- Host contract: [agent-hosts.json](https://github.com/wellmanifest/new-project/blob/main/governance/agent-hosts.json)
- Immutable adoption/updater: [create_adoption_lock.py](https://github.com/wellmanifest/new-project/blob/main/scripts/create_adoption_lock.py)

<!-- end wellmanifest:source-links:v1 -->

Same contract as `GEMINI.md` and `AGENTS.md`. Claude Code must follow it
even when this session did not start in Cursor.

1. Read `AGENTS.md` first.
2. Allocate with `./project/new-ticket.sh` only. Never copy ticket directories.
3. Use a `ticket-NNN` branch/worktree. Do not write on `main` or a dirty primary.
4. Stay inside `intent.json` `allowedPaths`.
5. Run `./scripts/install-agent-hosts.sh` once per clone, then `./project/governance-check.sh` before done.

The git hook rejects unbound commits. Markdown is not a substitute for the hook.

Bounded session controls: respect the ticket's `maxActiveMinutes`, create a
`checkpoint` before a context or tool boundary, and leave a `handoff` then
`stop` after a deterministic failure instead of retrying indefinitely.
