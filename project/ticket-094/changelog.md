# ticket-094 changelog

- Added `error/GOV-WORKTREE-OVERLAP.md` to `governance/package-manifest.json`.
  It was the only document under `error/` that adopters never received, which
  is why ticket-092 had to leave the three catalog entries' `documentation` as
  `null`: `tests/adoption-lock.test.sh` requires every non-null documentation
  path to exist inside an adopter's `.governance/`.
- Pointed `GOV-WORKTREE-OVERLAP-001/002/003` at that document, in that order.
- Restored `governance/worktree-guard.schema.json`, deferred by ticket-092 to
  stay inside the hub's 9-file limit.
