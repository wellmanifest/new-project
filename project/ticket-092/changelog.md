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

## Required follow-up (not in this ticket's scope)

`.github/workflows/ci.yml` must gain a step running
`bash tests/worktree-overlap.test.sh`. The workflow asserts that every
`tests/*.test.sh` is wired into it, so until that step exists this branch
cannot pass CI. That file is declared by ticket-090's `allowedPaths`;
adding it here raises `GOV-WORKSTREAM-004` and `GOV-BUDGET-001`
(`maxImplementationFiles: 8`). It belongs in ticket-090's closure or in an
explicitly dependent ticket.
