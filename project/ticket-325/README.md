# Ticket 325: Admit unrelated work beside untouched inactive legacy logs

- **ID**: ticket-325
- **Owner**: agent:codex / inactive-carriers325-20261008
- **Status**: IN_PROGRESS
- **Workflow state**: VALIDATION
- **Created**: 2026-10-08

## Goal and scope

PLF-2993, parent PLF-054. SESSION_EXECUTION_AUTHORIZATION: continued autonomous repairs, tests and protected publication. The managed observer currently demands a missing legacy intent before checking whether an unchanged committed inactive ticket acquired only a diagnostic log. Correct the standard observer, preserving foreign work and all active/unknown ownership barriers. Platform broker restoration remains a separately admitted target task.

## Acceptance criteria

- [x] AC-01: Real Git regression reproduces the blocker and proves safe observation for unchanged BACKLOG/PLAN/BLOCKED legacy log-only carriers.
- [ ] AC-02: Active, new/modified carrier, symlink, malformed intent and overlapping material delta remain conservative; required checks and independent publication pass.

## Evidence boundary

Private bounded checkpoints, tests and receipts: work-start-inactive-carriers-20261008 in the operator XDG state. No target source, legacy intent, foreign log, key or encrypted volume changes.

## Local validation

The original regression failed for all three inactive statuses before the fix. All 73 observer tests and the complete governance-scripts suite now pass (129 seconds); governance reports zero errors and warnings. The shell runner includes the observer suite in the required OneDev profile. AC-02 local safety cases pass; independent checks and publication remain pending. Read-only Platform candidate observation admits only narrow compose.yaml infrastructure scope; ticket-443 still blocks overlapping governance scope. No target adoption or broker restoration is claimed.
