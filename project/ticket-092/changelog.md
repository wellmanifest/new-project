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
- Stripped `GIT_DIR`, `GIT_WORK_TREE`, `GIT_INDEX_FILE` and the rest of git's
  scoping variables before invoking git. A hook inherits them, they override
  `git -C <path>`, and the checker saw one checkout instead of the workspace —
  so the gate passed on a real overlap. Covered by a regression test.

## Required follow-up (not in this ticket's scope)

`.github/workflows/ci.yml` must gain a step running
`bash tests/worktree-overlap.test.sh`. The workflow asserts that every
`tests/*.test.sh` is wired into it, so until that step exists this branch
cannot pass CI. That file is declared by ticket-090's `allowedPaths`;
adding it here raises `GOV-WORKSTREAM-004` and `GOV-BUDGET-001`
(`maxImplementationFiles: 8`). It belongs in ticket-090's closure or in an
explicitly dependent ticket.
