# Ticket 441: Ignore landed standard adoptions in atomic adoption gate on clean heads

- **ID**: ticket-441
- **Owner**: agent:antigravity
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Created**: 2026-11-15

## Goal and authorization

`SESSION_EXECUTION_AUTHORIZATION`: explicit owner authorization (`tak`) to fix
false `GOV-SYNC-001` failures on clean/scheduled `main` checkouts in
`wellmanifest/new-project`. Writer session
`allocation-2026-11-15T14:23:38Z-1921714-adee68f4`, initial fencing `1/1`,
bounded within `maxActiveMinutes` (`20` min planned).

Under `.governance/ticket-activity.json` `missingPolicy="status-projection"`,
fresh CI clones without `.git/new-project/terminal-receipts.json` project
historical merged tickets as `IN_PROGRESS`. `resolve_validation_base()` already
ignores `standardAdoption` tickets verified by `delivery_landed()` on
`refs/remotes/origin/<targetBranch>`, returning `base=None` on clean `HEAD`,
but `atomic_standard_adoption_paths()` still inspected `standard_adoption_records(active)`
and emitted `GOV-SYNC-001`.

## Acceptance criteria

- [x] AC-01: Single and multiple already-landed `standardAdoption` tickets on a clean published checkout (or during an unrelated subsequent diff) do not trigger `GOV-SYNC-001` in `atomic_standard_adoption_paths()`, whereas unlanded adoptions and post-merge diffs touching `project/ticket-NNN/**` retain full atomic verification.
- [ ] AC-02: `packages/wellman/sync_bundled.py --check`, unit/package tests, `project/governance-check.sh`, protected CI/OneDev checks, and independent Validator review pass before merge.

## Risk and scope

Excluding an adoption ticket when its own `project/ticket-NNN/**` carrier path
is in `changed` would drop `adoption_paths` exemptions on push-to-`main` CI
runs for the adoption merge itself. Retaining any record whose ticket directory
prefix appears in `changed` preserves post-merge push verification while
eliminating clean-head and unrelated-ticket false positives. `check_lock`
continues to verify every managed file hash unconditionally.
