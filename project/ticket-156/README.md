# Ticket 156: Make routine governance proportional and parallel

- **ID**: ticket-156
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-08-30

## Goal and scope

Use the last two hours of Subactor delivery history to remove governance work
that does not improve change safety. Routine, bounded changes should use the
compact v3 intent, while a full delivery/architecture contract remains
available for high-risk work. Non-overlapping tickets should proceed in one
broad workstream, allocation should not require live network access, and
estimates longer than thirty minutes should remain valid.

## Acceptance criteria

- [ ] AC-01: A routine source/test change passes with the compact v3 intent
      produced by `new-ticket.sh`; hard file limits and `allowedPaths` remain
      deterministic.
- [ ] AC-02: High-risk paths still require the explicit delivery contract.
- [ ] AC-03: Up to four disjoint tickets may share a workstream, while concrete
      or pattern scope overlap is still rejected.
- [ ] AC-04: Ticket allocation works from local refs by default and a requested
      remote refresh reports an actionable connectivity failure.
- [ ] AC-05: Delivery timeboxes accept realistic work up to two hours without
      weakening exact-base or exact-head validation.
- [ ] AC-06: The full governance suite and a representative compact
      Subactor-style fixture pass.

## Evidence and authorization

The active Founder request explicitly asks to investigate and change the
Wellmanifest standards. It provides `SESSION_EXECUTION_AUTHORIZATION` for this
bounded, non-destructive standard repair. The observed two-hour sample contains
57 non-merge commits: 11 carrier-only commits and 20 mixed carrier/material
commits. Platform alone produced 8 carrier-only commits out of 16.

## Audit findings

- Governance carriers appeared in 31 of 57 non-merge commits (54%). The cost
  was concentrated in `wellmanifest/new-project`, especially verbose delivery
  metadata, lifecycle state projected from stale prose, and serialization of
  unrelated work under one broad workstream.
- The deterministic gate itself was fast: observed runs were approximately
  0.25 s (`config`), 0.28 s (`worktrees`), 0.67 s (`platform`) and 2.12 s
  (`core`). The delay came from semantic deadlocks and repair commits, not CPU
  time in the validator.
- `platform` failed on an unknown historical workstream. `core` accumulated
  stale conflict pairs, excess active tickets, an unknown workstream and scope
  overlap. Immutable terminal receipts and proportional concurrency address
  those causes without treating mutable closure prose as lifecycle truth.
- `wellmanifest/project-ssot` and `wellmanifest/ssot` were not implicated by
  the evidence and remain unchanged. Exact-head approval, protected merge and
  immutable managed-file provenance also remain unchanged.
- The read-only fleet inventory found 23 locked adopters between versions
  0.14.1 and 0.19.7, plus further repositories that claim adoption without a
  recognized lock. Publishing alone will not update them; a reviewed fleet
  upgrade is required after release.

## Implemented decision

Routine, disjoint changes may use compact intent v3, with hard scope and file
ceilings still enforced. Full delivery metadata remains mandatory when the
target opts in or the change touches dependency/integration paths. The default
allows four disjoint tickets per workstream, realistic two-hour delivery
windows, and local ticket allocation; remote synchronization is explicit via
`--refresh-remote`.

Validation also found and fixed two adjacent regressions from terminal-receipt
support: validators no longer create `__pycache__` diffs, and the worktree guard
installer now deploys its `ticket_activity.py` runtime dependency.

## Tracking boundary

This directory holds the minimal reviewed intent. Raw command output remains
outside Git; implementation and tests stay in their normal directories.
