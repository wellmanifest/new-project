# ticket-428: Prevent disjoint peer work-start starvation and bound controller store observation (v0.20.147)

- **ID**: ticket-428
- **Owner**: agent:antigravity
- **Status**: IN_PROGRESS
- **Workflow state**: VALIDATION

## Goal and scope

SESSION_EXECUTION_AUTHORIZATION: explicit owner authorization to execute `wellmanifest/new-project#602` (`NP-046`: bounded coherent work-start admission under continuous disjoint peer writes) and `wellmanifest/new-project#599` (`NP-043`: bounded streaming controller store observation and authenticated, archive-preserving controller lease store compaction), add deterministic regression coverage, and prepare release `0.20.147`.

## Acceptance criteria

- [x] AC-01: Update `scripts/work_start_check.py` so end-of-observation stability verification permits uncommitted/index dirty-state progression exclusively within already-registered, non-quarantined, disjoint peer ticket worktrees whose `HEAD`, `branch`, `intent.json`, `workstream`, activity status, and non-overlapping material paths remain unchanged, while failing closed on any selected/primary/caller checkout mutation, ref/manifest/registration/SQLite change, foreign ticket carrier mutation, or scope overlap.
- [x] AC-02: Replace the 4 MiB whole-file `state.json` read in `scripts/work_start_check.py`, `scripts/ticket_recovery.py`, and `scripts/ticket_restoration.py` with a strict RFC 8259 bounded streaming projection reader (`MAX_CONTROLLER_STATE_BYTES = 128 MiB`) that rejects duplicate keys, invalid UTF-8, symlinks, non-regular files, and concurrent state changes without mutating controller state.
- [x] AC-03: Add managed `scripts/controller_store_compaction.py` (registered in `governance/package-manifest.json`) providing read-only `plan` inspection and authenticated, `flock`-serialized, CAS-bound (`--expected-state-sha256`), archive-preserving (`store/archive/`) `--apply` compaction of `subactor.repository-change-lease-store/v1` stores that preserves `nextFencingToken` monotonicity, all active/expired/merged/in-flight leases, `previousReceiptRef` expiry receipts, recent idempotency receipts, and audit history.
- [x] AC-04: Add regression tests in `tests/governance-v147-regressions.test.py` (wired into `tests/governance-scripts.test.sh`) covering both `#602` and `#599`, bump version parity surfaces (`VERSION`, `CHANGELOG.md`, `governance/manifest.default.json`, `governance/manifest.hub.json`, `packages/wellman/pyproject.toml`) to `0.20.147`, and pass full governance and package gates.
