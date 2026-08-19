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
