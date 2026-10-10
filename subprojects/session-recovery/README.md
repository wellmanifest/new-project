# wellmanifest/session-recovery

> **Provider-neutral standard for LLM host session resilience, crash isolation, automated storage salvage, and workspace state rehydration.**

## The Problem

Interactive LLM hosts (such as Antigravity `agy`, Claude Code, Aider, and autonomous Subactor daemons) store local session history, transcripts, and metadata in databases (e.g. SQLite) or event streams (JSONL).

In production environments, several critical failure modes frequently occur:
1. **Uncaught Nil Pointer Panics upon Storage Corruption**: A single corrupted session database (e.g. SQLite page corruption `database disk image is malformed`) causes TUI/CLI tools to panic (`nil pointer dereference`) during startup or conversation listing, preventing the user from accessing ANY session.
2. **CLI Resumption Inconsistency**: Lack of standardized resumption commands (e.g. user entering `agy resume` instead of `agy -c` / `agy --continue`), yielding unhelpful error messages.
3. **Conversational Amnesia from Lost Transcripts**: Treating conversation memory as durable task storage. When local chat files are damaged, agents lose track of their work.

## The Standard

`wellmanifest/session-recovery` establishes:
1. **Ephemerality of Conversation Memory**: Conversation history is strictly an advisory cache. Ground truth resides in Git commits, active ticket `intent.json`, execution leases, and cryptographic verification receipts.
2. **Crash Isolation & Preflight Integrity**: Session stores must undergo preflight checks. Damaged session files must never crash the host application or conversational pickers.
3. **Automated Quarantine and Salvage**: Damaged stores are quarantined (`.bak`) and deterministically salvaged (via `.dump` and schema reconstruction) without human intervention.
4. **Uniform CLI Resumption Contract**: Mandatory `--continue` (`-c`), `--conversation <id>`, and `--list-sessions` conventions, with actionable suggestions for common typos (e.g. `resume`).
5. **Authoritative State Rehydration**: Synthetic rehydration prompt generation from Git + Ticket + Work Continuity checkpoints when raw conversational transcripts cannot be restored.

## Conformance Tool

```bash
# Check integrity of a session database
python3 standard/conformance.py check ~/.gemini/antigravity-cli/conversations/<id>.db

# Quarantine and salvage a corrupted database
python3 standard/conformance.py salvage broken.db --out recovered.db --receipt receipt.json

# Generate rehydration envelope from workspace state
python3 standard/conformance.py rehydrate --ticket ticket-001 --session-id <id>
```

## Specification & Policy

- [Normative Policy](standard/POLICY.md)
- [Session Recovery Schema](standard/session-recovery.schema.json)
