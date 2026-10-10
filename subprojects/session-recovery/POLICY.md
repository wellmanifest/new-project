# POLICY.md — LLM Host Session Recovery Standard

`wellmanifest/session-recovery` establishes the normative, provider-neutral standard for LLM host session resilience, crash isolation, automated storage salvage, and workspace state rehydration.

## 1. Foundational Principle

> **Conversation Memory is a Cache, Never Task Storage.**
>
> An LLM chat trajectory or transcript is an ephemeral observation stream. Ground truth belongs exclusively to the Git repository HEAD commit, the active ticket (`intent.json` / `README.md`), execution leases, and cryptographic verification receipts.
>
> No host process failure, SQLite B-tree page corruption, transcript loss, or conversation history degradation may permanently destroy, lock, or invalidate authorized work.

---

## 2. Normative Invariants

### INV-SR-001: Crash Isolation
A host application (interactive TUI, CLI runner, or background daemon) must isolate individual session access errors. If a session store is unreadable, malformed, locked, or corrupt:
1. The host MUST NOT panic, segfault, or throw an unhandled exception (`nil pointer dereference`).
2. Catalog and listing views (such as conversation pickers or status tables) MUST degrade gracefully, displaying a status badge (e.g. `[CORRUPTED]`) rather than aborting.
3. Other valid sessions MUST remain fully accessible and selectable.

### INV-SR-002: Preflight Storage Integrity
Before accessing a persistent session file:
1. SQLite-backed stores MUST run integrity preflight checks (`PRAGMA quick_check`).
2. JSONL-backed stores MUST validate stream delimiters and syntax bounds.
3. If corruption is detected (`database disk image is malformed` or parse failure), the store manager MUST return a typed error that triggers automated quarantine and salvage, never passing a `nil` trajectory handle to downstream renderers.

### INV-SR-003: Automated Quarantine and Salvage
When a session store fails integrity checks:
1. **Quarantine**: The host preserves the damaged file with a `.bak` or `.corrupt.<timestamp>` suffix.
2. **Salvage**: The host attempts deterministic record salvage (e.g. SQLite `.dump` and reconstruction into a clean schema, or JSONL valid line extraction).
3. **Verification**: The recovered store MUST pass `PRAGMA integrity_check` before being restored to the active path.
4. **Receipt**: A `wellmanifest.session-recovery-salvage/v1` receipt is emitted recording original SHA-256, salvaged record count, recovered SHA-256, and timestamp.

### INV-SR-004: Standardized Resumption and Discovery CLI Interface
Every compliant LLM CLI host MUST support a uniform interaction model:
- `--continue` (or `-c`): Resume the most recent active session in the workspace.
- `--conversation <id>` (or `--session <id>`): Resume a specific session by its identifier.
- `--list-sessions`: Output a machine-readable list of sessions with health status (`HEALTHY`, `DEGRADED`, `CORRUPTED`, `SALVAGED`).
- `--repair-session <id>`: Force diagnostic scan and automated salvage of a specified session.
- **Helpful Positional Argument Routing**: If a user runs an intuitive but unsupported positional command (e.g. `agy resume`), the CLI MUST reject it with an actionable suggestion (e.g. `Did you mean '--continue' / '-c' or '--conversation <id>'?`) rather than a cryptic parameter error.

### INV-SR-005: Workspace State Rehydration
If a session cannot be replayed from local conversation history (due to unrecoverable damage, remote handoff, or cross-machine migration), the host MUST construct a `SYSTEM_SESSION_REHYDRATION` context envelope:
1. Re-read Git branch, working tree diff, and `HEAD` commit.
2. Re-read active ticket `intent.json` and accepted delivery criteria.
3. Inspect active leases and latest `new-project.work-continuity/v2` checkpoint.
4. Inject a synthetic rehydration turn that restores full working memory to the LLM agent without requiring raw conversational transcript replay.

---

## 3. Conformance Levels (S0 – S5)

- **S0**: Normative JSON Schema `session-recovery.schema.json` and policy invariants published.
- **S1**: Deterministic conformance tool `conformance.py` checks session stores and validates salvage receipts.
- **S2**: Immutable source revision and SHA-256 digests locked in `new-project`.
- **S3**: CI checks verify that session storage fixtures (including intentionally corrupted test databases) do not trigger unhandled crashes.
- **S4**: Host release pipeline gates deployment on zero unhandled panics during corrupted session scans.
- **S5**: Live runtime emits verified salvage receipts and self-heals corrupted stores in production.
