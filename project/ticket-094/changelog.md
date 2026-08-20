# ticket-094 changelog

## Closure - 2026-08-20

- Closed ticket-094 (`DONE / DONE`) from integrated `main` after PR #150.
- Post-merge evidence on the default branch: the `error/GOV-WORKTREE-OVERLAP.md`
  entry in `governance/package-manifest.json`, the three catalog entries
  pointing at it, and `governance/worktree-guard.schema.json`.
- No implementation files in this closure.

- Added `error/GOV-WORKTREE-OVERLAP.md` to `governance/package-manifest.json`.
  It was the only document under `error/` that adopters never received, which
  is why ticket-092 had to leave the three catalog entries' `documentation` as
  `null`: `tests/adoption-lock.test.sh` requires every non-null documentation
  path to exist inside an adopter's `.governance/`.
- Pointed `GOV-WORKTREE-OVERLAP-001/002/003` at that document, in that order.
- Restored `governance/worktree-guard.schema.json`, deferred by ticket-092 to
  stay inside the hub's 9-file limit.
