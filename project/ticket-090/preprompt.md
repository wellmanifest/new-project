Host-agnostic LLM standard. Gemini/Antigravity read GEMINI.md, Claude reads
CLAUDE.md, Cursor reads .cursor/rules. A git pre-commit hook rejects commits
not bound to an IN_PROGRESS ticket-NNN. install-agent-hosts.sh copies the
same files into other clones and user-level host dirs.

Do not edit package-manifest.json or governance_check.py (ticket-089 leftover).
SESSION_EXECUTION_AUTHORIZATION and --force-new come from the human request
to create this ticket so every LLM host respects the standard.
