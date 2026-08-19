# ticket-092 understanding

## Intent

HOME=`wellmanifest`, shape=`domain_pack`. Not a runtime_service. The guard is
an adopted YAML + script, same class as `pyqual.yaml` / `goal.yaml`.

## Scope

New files only. Forbidden: package-manifest, governance_check.py, AGENTS.md,
install-agent-hosts, pre-commit, diagnostics.json, new-ticket.sh.

## Acceptance

Synthetic fixture plus a live scan of wellmanifest/.worktrees and
subactor/.worktrees.
