# Ticket 419: Batch Git ancestry and scope reads in activity and overlap checks

- **ID**: ticket-419
- **Owner**: agent:antigravity
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION

SESSION_EXECUTION_AUTHORIZATION: the user requested continuing autonomous testing, merging, fixing, optimization, and improving `wellmanifest/*` standards.

## Goal and scope

Eliminate per-ticket Git subprocess storms and TOCTOU gaps during `ActivityReadBatch` resolution (`delivery_landed` and `_ancestor`) and avoid discarding expensive `ticket_scopes`/`dirty_paths`/`changed_paths` inspections for unrelated repository identities when `worktree_overlap_check.py` is scoped via `--identity-of`. Keep `scripts/ticket_activity.py` and `packages/wellman/src/wellman/_bundled/ticket_activity.py` byte-identical.

## Acceptance criteria

- [x] AC-01: `delivery_landed` and `_ancestor` batch and revalidate Git tree (`ls-tree`) and ancestry (`merge-base --is-ancestor`) observations inside `ActivityReadBatch` without per-ticket subprocess growth, preserving exact parity with standalone resolution and keeping `scripts/ticket_activity.py` byte-identical to `packages/wellman/src/wellman/_bundled/ticket_activity.py`.
- [x] AC-02: `worktree_overlap_check.py --identity-of` preserves workspace-wide checkout inventory and broken-metadata detection while skipping `ticket_scopes`, `dirty_paths`, and `changed_paths` for checkouts of other repository identities.
- [x] AC-03: Unit, shell, and governance checks pass in `wellmanifest/new-project`.
