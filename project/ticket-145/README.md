# Ticket 145: Release new-project 0.19.6

- **ID**: ticket-145
- **Owner**: unresolved:human
- **GitHub issue**: #247
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Created**: 2026-08-28

## Goal and scope

Publish portable governance-runner selection and durable adoption fixes as the
immutable wellmanifest/new-project 0.19.6 standard.

## Acceptance criteria

- [ ] AC-01: All version projections resolve to 0.19.6.
- [ ] AC-02: The complete deterministic suite passes on the release commit.
- [ ] AC-03: Validator merges the exact head before clean-main publication creates v0.19.6.

## Risks and rollback

An immutable tag must never be moved. If a defect is found after publication,
publish a later corrective version.
