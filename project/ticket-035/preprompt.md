# Ticket preprompt — ticket-035

- **Task ID**: ticket-035
- **Task title**: Gate decision logs with GOV-DECISION codes
- **Created**: 2026-08-06

## Directives

1. Prefer deterministic validation of decision logs over prose review.
2. Reuse `scripts/decision_record.py`; do not reimplement DSL parsing.
3. Keep implementation outside `project/ticket-035/` except governance evidence.
4. Do not edit human-owned `user-*.md` files.

## Resources

- `CONTRIBUTING.md` — DOCUMENT DECISION_LOG / C-DECISION-*
- `scripts/decision_record.py`
- `governance/diagnostics.json` — GOV-DECISION-001..004
- validator-agent: append to `project/{ticket}/decisions.md` after approve
