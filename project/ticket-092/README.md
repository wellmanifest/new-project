# Ticket 092: Proactive worktree overlap guard

- **ID**: ticket-092
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
- **Created**: 2026-08-19

## Goal and scope

Add a pyqual-style `worktree-guard.yaml` plus a deterministic overlap checker
so adopters fail closed when two worktrees of the same repository write the
same paths. Ship the three triggers that make it act on its own: a chainable
pre-commit hook, a `pyqual` stage, and `systemd --user` timer + `.worktrees`
path units for whole-workspace scans. Do not touch files owned by
ticket-089/090/091.

## Acceptance criteria

- [x] AC-01: `./tests/worktree-overlap.test.sh` covers shared-path fail,
  disjoint pass, `conflictsWith`, branch-based ticket attribution,
  repository-vs-workspace scope, `--report`, the pyqual snippet and the
  installer.
- [x] AC-02: Live scan of `~/github/wellmanifest` produces a structured
  report (44 checkouts, 8 findings).
- [x] AC-03: Live scan of `~/github/subactor` produces a structured
  report (114 checkouts, 11 findings, ~3.4s).
- [x] AC-04: `systemd --user` timer and `.worktrees` path unit are installed and
  observed to fire for both workspace roots.
- [x] AC-05: A repository-level run reports only its own repository identity, so
  an unrelated conflict cannot block a commit.
- [x] AC-06: The pre-commit trigger lands in the directory git actually reads
  and blocks an overlapping commit; verified across `core.hooksPath` unset,
  tracked and non-standard layouts, and in the three subactor pilots.
- [x] AC-07: The three `GOV-WORKTREE-OVERLAP` codes are registered in
  `governance/diagnostics.json` and the suite is wired into `ci.yml`, so both
  CI gates pass.
- [x] AC-08: The verdict is a real `git merge-tree` merge, not path
  intersection: branches editing different regions of one file pass, a stacked
  branch never conflicts with its ancestor, merged leftovers are not writers,
  and two branches rewriting the same lines fail.

## Known follow-up

`governance/worktree-guard.schema.json` is deferred: the hub policy caps a
ticket at 9 implementation files. Nothing references it. See
[changelog.md](changelog.md).

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-cursor.md](ai-cursor.md)
