# Ticket 439: Isolate the literal branch-name Git oracle

- **ID**: ticket-439
- **Owner**: agent:codex
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Created**: 2026-11-14

## Goal and authorization

SESSION_EXECUTION_AUTHORIZATION: the ongoing request to continue and merge
Forge/Polycell fixes covers queued PLF-27165. Native admission permits this
disjoint source test repair. Writer session: codex-branch-oracle-isolation-20261114-1052,
initial lease revision/fencing: 1/1. Independent protected review remains required.
Implementation stage: 2026-11-14T10:51:41.040023+00:00 to 2026-11-14T11:16:41.040023+00:00, maximum25minutes.

## Acceptance criteria

- [x] AC-01: Isolate the Git oracle and reproduce parent-history discovery deterministically; preserve all existing38literal cases across3fields, bounds, CLI and27unit cases. Pass with Git-nested and nonGit TMPDIR.
- [ ] AC-02: Native governance and delivery checks pass; submit the exact head for independent protected publication.

## Scope and risks

Only tests/branch-lifecycle.test.sh and this ticket's carriers are owned here.
The production parser already rejects checkout shorthand. An empty directory
can still discover parent Git history; the fixture must stop discovery at its
parent, not at its own directory. Git fixture commands must be local, deterministic
and avoid user hooks/signing. No version/release, production parser, dependency,
case removal or deadline change. Raw logs and recovery snapshots stay external.

## Validation before publication

The complete unchanged case set passes with the controlled parent-history
regression under default SDK Git-nested TMPDIR (4.375s) and nonGit TMPDIR
(3.006s). Each run includes the38literal cases across3fields, bounds/CLI and
27reconciliation unit tests. Production code is unchanged; git diff --check
passes. Native full delivery and independent protected checks remain required.
Raw evidence: external forge-polycell-20261113/source-branch-oracle receipts.

The first native Goal preflight stopped when adoption-fresh-bootstrap exceeded
its unchanged300second limit in the SDK private temporary cache. The same
complete29test suite passes with an owned nonGit /tmp temporary directory
(98.557s; wrapper98.759s). Full native delivery will use this observed
execution environment; no test, assertion or gate timeout is removed or raised.
Both outcomes remain in the external source-branch-oracle receipts.
