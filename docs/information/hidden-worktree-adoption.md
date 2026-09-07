---
{
  "schema": "wellmanifest.docs/document/v1",
  "id": "hidden-worktree-adoption",
  "kind": "information",
  "version": 2,
  "title": "Hidden repository-local worktree adoption",
  "status": "proposed",
  "owner": "wellmanifest/new-project",
  "created": "2026-09-07",
  "updated": "2026-09-07",
  "review_after": "2026-10-07",
  "source_revision": "5848c1efb3386765e221cde57090f8c221f3e857",
  "affected_repositories": [
    "wellmanifest/new-project"
  ],
  "evidence": [
    "https://github.com/wellmanifest/worktrees/pull/17",
    "https://github.com/wellmanifest/worktrees/tree/87d17708895ffad603c5d71cb2b8ef02ab100279",
    "repo://wellmanifest/new-project/tests/worktrees-adoption.test.py"
  ]
}
---

# Hidden repository-local worktree adoption

<!-- docs:section purpose -->
## Purpose

New-project 0.20.9 distributes Worktrees 0.5.1 / v5, whose delivery location is `<primaryCheckout>/.worktrees/<ticket-NNN>--<slug>`. The branch is `ticket/NNN-<slug>` and the lease remains `<primaryCheckout>/.subactor/leases/<ticket-NNN>--<slug>.json`.

<!-- docs:section scope -->
## Scope

This document owns new-project package behavior. The layout standard is HOME wellmanifest/worktrees; Git effects are HOME the adopter and ADOPT wellmanifest/git-lifecycle. Cross-repository rollout evidence is HOME subactor/docs.

<!-- docs:section evidence -->
## Sources

[Worktrees PR 17](https://github.com/wellmanifest/worktrees/pull/17) merged as `87d17708895ffad603c5d71cb2b8ef02ab100279`. `governance/worktrees.lock.json` pins that exact revision and SHA-256 hashes for both the schema and checker. New-project's audited baseline is the metadata source revision; this document ships with its implementation candidate.

<!-- docs:section content -->
## Package behavior

- POLICY, CONTRIBUTING and managed agent instructions use the same hidden repository-local path.
- The adoption generator appends missing anchored worktree and operational-state ignores to the existing `.gitignore`; target rules and historical ignores remain intact. It rejects a symlinked `.gitignore` and does not ignore `.subactor/manifest.json`. The manifest remains a trackable managed file.
- Both overlap and lifecycle inventory derive their schema from the same loaded Worktrees package. A failed observation carries no asserted inventory schema.
- The v5 classifier preserves undotted repository-local worktrees as `legacy-v4`, alongside v1/v2/v3, temporary and unknown locations. Inventory grants no effect authority.
- Git's registered primary checkout is the allocation anchor even when called from a linked worktree. Git 2.51.0 and actual relative-path options remain prerequisites.

<!-- docs:section limitations -->
## Limitations

Installing instructions does not update custom runtime allocators or prove production behavior. Each consumer must adopt the immutable package and test its actual creation path. Existing worktrees are preserved; no automatic move, repair, prune or cleanup is introduced.

<!-- docs:section next_actions -->
## Validation and rollout

`tests/worktrees-adoption.test.py` exercises pinned bytes, POSIX/Windows plans, root-ignore preservation and idempotence, symlink rejection, primary resolution and relative relocation in disposable Git repositories. The shell overlap and lifecycle suites exercise consumer inventory. After protected publication, adopters use `goal governance adopt --source-revision <published-merge-sha> --upgrade` through their own bounded tickets and validation. Source merge, final release, adoption and actual runtime allocation require separate receipts.


## Probe context for parallel hosts

Worktrees 0.5.1 was protected-merged in [PR 19](https://github.com/wellmanifest/worktrees/pull/19) at `81e0d750f18ecace4436706250bf5deb190a000a`. Hosts running from an organization directory must pass `feature-probe --from-worktree <checkout>`. An unavailable repository is reported separately from missing Git support; inherited Git selectors cannot redirect the query. The operation remains read-only.

Host installation also distinguishes the governance hub source paths from adopter target paths using the existing package manifest. Hub activation no longer demands duplicate `.governance` copies of its `scripts` runtime files. Missing source files still fail closed.
