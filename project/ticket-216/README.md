# Ticket 216: Guard the packaging validator against interpreters without tomllib

- **ID**: ticket-216
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-09-12

## Goal and scope

`scripts/agent_host_check.py` imports `tomllib` at module scope. That module is
stdlib only from Python 3.11, while adopters may legitimately declare
`requires-python = ">=3.10"` and test on 3.10.

`governance_check.py` imports this validator inside a `try/except ImportError`
and, on failure, reports:

```
GOV-SYNC-001 ERROR: Managed agent host validator is missing next to governance_check.py.
```

So on 3.10 an interpreter gap is reported as a missing managed file, the gate
fails, and — because `GOV-PACKAGING-003` binds the gate to `pytest` — the whole
test session aborts with `INTERNALERROR`. Observed while adopting 0.20.24 in
`semcod/planfile` (matrix 3.10 + 3.13): the 3.13 job passed, the 3.10 job failed.

Change: import `tomllib`, fall back to an already-installed `tomli`, and
otherwise keep the module importable with `tomllib = None`. `check_packaging`
then skips the Python ecosystem when no reader exists; interpreters at 3.11+
enforce `GOV-PACKAGING-001/002/003` exactly as before. No new dependency is
introduced.

Out of scope: changing what the packaging bindings require, and the separate
question of whether the standard should declare its own interpreter floor.

## Acceptance criteria

- [ ] AC-01: `tests/agent-hosts.test.sh` proves the validator emits no packaging findings when `tomllib` cannot be imported, and keeps its existing assertions on a normal interpreter.
- [ ] AC-02: `./project/governance-check.sh --actor agent` passes.

## Tracking boundary

This directory contains the minimal reviewed intent. Optional participant prose
and raw command logs are not required delivery output.
