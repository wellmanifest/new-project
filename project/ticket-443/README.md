# Ticket 443: Add verified controller lease settlement and safe ignored-runtime worktree pruning

- **ID**: ticket-443
- **Owner**: agent:antigravity
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Authorization**: SESSION_EXECUTION_AUTHORIZATION — autonomous execution and protected publication authorized on 2026-11-15 for Recommendations #3 and #4 (`terminal_lease_release.py` verified controller settlement and `prune_merged_worktrees.py` safe ignored-runtime worktree pruning). Task consent only, never review evidence.
- **Created**: 2026-11-15

## Goal and Scope

1. **Controller Terminal Lease Settlement (`scripts/terminal_lease_release.py`)**:
   Preserve `--request` current-owner handoff unchanged while adding explicit controller terminal settlement (`--settle-verified`, optional `--ticket ticket-NNN`, read-only plan by default and `--apply` to execute). Transition `claimed`, `editing`, `validating`, `approved`, `merged`, and `closed` leases to `released` without requiring original `ownerSession` context ONLY when:
   - `.git/new-project/terminal-receipts.json` contains an unambiguous receipt for `lease['ticketId']` on `lease['targetBranch']` whose outcome declares `releasesReservation: true` in `ticket-activity.json` and passes `activity._terminal_verified(...)` ancestry/rewrite checks;
   - `_verify_terminal(...)` passes (clean checkout at `receipt['headSha']` on `lease['branchRef']` if `.worktrees/<worktreeId>` exists, or verified allocation-base ancestry with no lingering directory/symlink/ref/registration if removed);
   - POSIX `O_NOFOLLOW` directory anchoring, `lease_lock`, and exact `read_at` CAS hold, writing an immutable receipt under `.subactor/receipts/terminal-owner-release/` recording `"settledBy": "controller:verified-terminal-receipt"` and `terminalReceiptRef`.
2. **Safe Ignored-Runtime Cleanup for Merged Worktrees (`scripts/prune_merged_worktrees.py`)**:
   Preserve arbitrary unknown ignored files by default while allowing canonical `.worktrees/<ticket>--<slug>` merged checkouts that have zero tracked/untracked changes (`git status --porcelain --untracked-files=all` empty), only allowlisted disposable runtime/cache ignored paths (`.venv`, `.pytest_cache`, `.mypy_cache`, `.ruff_cache`, `.subactor/{cache,sessions,recovery,receipts}`, `.planfile`, `__pycache__`, etc.), a terminal lease (`released`, `merged`, or `closed`), and no open process cwd/fd/lock to remove those allowlisted runtime caches safely (`O_NOFOLLOW`) and prune via `git worktree remove` without `--force` (both automatically for terminal-leased canonical checkouts and via `--include-ignored-runtime`).
3. **Standard Release `0.20.152`**:
   Update `error/GOV-CHANGE-LEASE.md`, regression suites, `CHANGELOG.md`, `VERSION`, `governance/manifest.default.json`, `governance/manifest.hub.json`, and `packages/wellman/pyproject.toml`.

## Acceptance Criteria

- [x] AC-01: `terminal_lease_release.py --settle-verified` plans read-only by default, settles verified terminal leases across `claimed`/`editing`/`validating`/`approved`/`merged`/`closed` with `--apply` and immutable `"settledBy": "controller:verified-terminal-receipt"` receipts, and refuses unmerged, dirty, frozen, ambiguous, or CAS-raced leases while keeping `--request` behavior 100% intact.
- [x] AC-02: `prune_merged_worktrees.py` preserves unknown ignored files (e.g. `.env`, `ignored-data.txt`), active/non-terminal leases, and checkouts with open process handles, while cleanly pruning merged canonical worktrees whose only remaining ignored paths are allowlisted disposable runtime/cache directories without ever invoking `git worktree remove --force`.
- [x] AC-03: `tests/terminal_lease_release_test.py`, `tests/prune_merged_worktrees_test.py`, `packages/wellman/sync_bundled.py --check`, `tests/version-parity.test.sh`, `tests/wellman-package.test.sh`, and `project/governance-check.sh` pass for `0.20.152`.

## Risks and Mitigations

- **Risk 1**: Accidental destruction of unique ignored data (such as `.env`, `.subactor/snapshots/`, or user scratch files) during worktree pruning.
  **Mitigation**: Strictly allowlist only reproducible runtime/test caches, require empty `git status --porcelain --untracked-files=all`, require canonical `.worktrees/<ticket>--<slug>` with a verified terminal lease and no live process handles, unlink only anchored `O_NOFOLLOW` cache entries, and invoke `git worktree remove` without `--force` so Git itself refuses if any other file exists.
- **Risk 2**: Premature settlement of an in-flight or frozen publication lease.
  **Mitigation**: Refuse `publication_frozen`, `dispatching`, `expired`, and any lease lacking an unambiguous verified terminal receipt + clean checkout / removed-ref ancestry proof under exclusive `lease_lock` CAS.
