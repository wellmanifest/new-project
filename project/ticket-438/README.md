# Ticket 438: Register pending bootstrap receipt regressions in CI

- **ID**: ticket-438
- **Owner**: agent:codex
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Created**: 2026-11-14

## Goal and authorization

SESSION_EXECUTION_AUTHORIZATION: continue the requested tested delivery. The
frozen source PR616 fails only because its new Python suite is absent from the
explicit CI inventory. This disjoint CI-only dependency owns one workflow path
under native session codex-bootstrap-refresh-ci-wiring-20261114, CAS1/1. It must
merge before the source PR is requalified. Existing tests, checks and protected
publication remain required. No source paths of ticket437 are written here.

Implementation stage: 2026-11-14T10:10:24.323166+00:00–2026-11-14T10:20:24.323166+00:00, maximum10minutes.

## Acceptance criteria

- [x] AC-01: Register strict execution of the new suite when present, preserving every existing job and step.
- [ ] AC-02: Inventory/native validation pass, then independent protected publication qualifies this CI dependency.

## Boundaries

This branch can merge before the pending test file exists. Its existence guard
does not ignore failures when the file is present. No test suppression, policy
change, target adoption or source admission. Raw evidence stays external.

## Validation

Workflow YAML parses. Structural comparison proves every prior job and step is
unchanged. The unchanged suite-inventory script passes in disposable fixtures
both without and with the incoming source test filename. The new step executes
strictly when that file is present; it has no continue-on-error override. Native
governance and independent protected exact-head checks remain required.
