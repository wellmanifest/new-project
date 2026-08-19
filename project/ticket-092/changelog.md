# ticket-092 changelog

- Added the worktree overlap checker, YAML runner, installer, tests and docs.
- Split ignored paths from declared-scope comparison and attributed tickets by
  branch, so the rule stops firing on `TODO.md` and on stale ticket copies.
- Added repository-vs-workspace scope: an in-repo gate answers only for its own
  repository identity while still discovering the whole workspace.
- Added the scheduled triggers: `systemd --user` timer, `.worktrees` path unit
  and a `--report` file for scans with nowhere to print.
- Added a safe, idempotent `pyqual.yaml` stage installer that leaves the file
  byte-identical when it cannot verify the edit.
- Resolved the pre-commit trigger from `git rev-parse --git-path hooks` instead
  of a hard-coded `.githooks/`, and added `--wire-hook` to chain it into
  `pre-commit` idempotently. Two of the three first adopters had the fragment
  in a directory git never reads.
- Recorded the 2026-08-19 retest matrix (`retest-2026-08-19.json`).
- Stripped `GIT_DIR`, `GIT_WORK_TREE`, `GIT_INDEX_FILE` and the rest of git's
  scoping variables before invoking git. A hook inherits them, they override
  `git -C <path>`, and the checker saw one checkout instead of the workspace —
  so the gate passed on a real overlap. Covered by a regression test.

- Registered `GOV-WORKTREE-OVERLAP-001/002/003` in `governance/diagnostics.json`
  and wired `tests/worktree-overlap.test.sh` into `ci.yml`. Both were CI
  failures, not optional polish: the validator rejects any emitted code missing
  from the catalog, and the workflow refuses to pass while a suite exists that
  no step runs. Scope amended and the file budget raised 8 -> 9;
  `governance/diagnostics.json` left `forbiddenPaths` for the same reason.
- Dropped `governance/worktree-guard.schema.json`. The hub policy caps a ticket
  at 9 implementation files and the two CI fixes made 10. Nothing references
  the schema and `worktree_guard.py` already rejects an unknown `schema:` value
  at load time, so it is the one file that can wait.

## Required follow-up (not in this ticket's scope)

A dependent ticket should re-add `governance/worktree-guard.schema.json` and
register it in `governance/package-manifest.json`, once this ticket frees the
workstream slot.
