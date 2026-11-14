# Ticket 437: Verified refresh of pending bootstrap ownership

- **ID**: ticket-437
- **Owner**: agent:codex
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Created**: 2026-11-14

## Goal and authorization

SESSION_EXECUTION_AUTHORIZATION: continue the requested delivery and repair its
existing allocator dependency at the standard's HOME. Ordinary published adoption
upgrades leave a stale first-allocation receipt. Add an explicit receipt-only
refresh for an already up-to-date installation, with no target source admission
or publication authority. Ship this material correction in standard0.20.150.

Native owner session: codex-license-bootstrap-refresh-20261114; observed local
lease revision/fence1/1. Writer check PASS. This local reservation grants no
independent review, merge or release authority.
Implementation stage: 2026-11-14T09:34:36.255016+00:00–2026-11-14T10:04:36.255016+00:00, maximum30minutes.

## Acceptance criteria

- [x] AC-01: A real migrated fixture can upgrade, explicitly refresh and allocate its first native ticket without changing unrelated source.
- [x] AC-02: Wrong base/clone, prior allocation, changed nonmanaged bytes, invalid publication, symlinks and changed observations fail closed without partial source writes.
- [ ] AC-03: Native tests and version150 parity pass; independent protected publication remains required.

## Boundaries

Use generated disposable fixtures only. Preserve all unknown worktrees and
receipts. No manual target receipt edits, handoff by expiry, policy changes or
self approval. Raw logs stay in external evidence storage.

## Validation and publication boundary

21 dedicated receipt regressions PASS, including a real first allocation,
read-only planning, unchanged foreign source, atomic failure and refused
ownership/byte changes. Version parity (9 cases), bundle synchronization and
native governance PASS (0 errors, 0 warnings). Three additional positive scenarios PASS for fresh, committed legacy and
untracked legacy bases, preserving their exact original manifests. Existing
bootstrap regressions are still running in disposable Git fixtures. Logs and
outcomes remain in external evidence storage.

Material source implementation is frozen for publication within the recorded
30minute stage. Exact-head protected Linux/Windows/OneDev checks and independent
Validator approval remain required. New dedicated Python regressions are run
explicitly; this bounded change does not alter protected command inventories.
