# ticket-092 changelog

- Closed ticket-092 (`DONE / DONE`) from integrated `main` after `7d673d4`
  (PR #144). No implementation files in this closure.
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
- Replaced the path-intersection heuristic with a real in-memory merge
  (`git merge-tree --write-tree`). Sharing a path is a poor proxy for
  conflicting: branches usually edit different regions and merge cleanly, and a
  stacked branch shares every path with its own ancestor. The three
  `www-sub-actor` branches the heuristic called a 41-file three-way collision
  are, under a real merge, two clean pairs and one conflict in two ignored
  files. Path intersection remains the fallback for git without `--write-tree`.
- Stopped pairing leftovers. A checkout whose HEAD is already in the default
  branch with a clean tree contributes nothing to any merge; in
  `~/github/subactor` that is 20 writers out of 117 checkouts. Skipping their
  reads also brought the scan back to ~3.5s and the pre-commit path to ~3.2s.

## Required follow-up (not in this ticket's scope)

A dependent ticket should, once this ticket frees the workstream slot:

- re-add `governance/worktree-guard.schema.json`;
- add `error/GOV-WORKTREE-OVERLAP.md` to `governance/package-manifest.json` as a
  managed file and then point the three catalog entries' `documentation` at it.
  `tests/adoption-lock.test.sh` requires every non-null `documentation` path to
  exist inside an adopter's `.governance/`, so the entries carry `null` until
  the document is actually shipped by the package. Adopters that run
  `install-worktree-guard.sh` already receive it.
