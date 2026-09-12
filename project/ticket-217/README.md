# Ticket 217: Publish wellmanifest/new-project 0.20.25

- **ID**: ticket-217
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-09-12

## Goal and scope

Publish the already validated `0.20.25` standard projection after the protected
merge of ticket-216, which keeps `scripts/agent_host_check.py` importable on
interpreters without `tomllib`.

Adopters cannot pin an unpublished revision, so `semcod/planfile` — where the
defect surfaced on its Python 3.10 matrix job — stays blocked until this
release exists.

## Acceptance criteria

- [ ] AC-01: Release projections and tests identify `0.20.25`.
- [ ] AC-02: Protected checks and Validator approve the exact release head.

## Tracking boundary

This directory records bounded release intent; publication receipts remain
outside Git.
