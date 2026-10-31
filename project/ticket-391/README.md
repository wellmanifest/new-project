# Ticket 391: Allow DockURI ownership for operational package repositories

- **ID**: ticket-391
- **Owner**: agent:codex
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION

SESSION_EXECUTION_AUTHORIZATION: the user requested reusable operational Python/npm packages in DockURI, corrections to restrictive Wellmanifest standards, continued tests and protected merges.

## Goal and scope

Accept dockuri in the closed placement ownership vocabulary and synchronize source, bundled checker and agent guidance. Keep unknown owners rejected and preserve the wellmanifest standards/runtime boundary. The six-file initial bounded scope includes the distributed agent template before any implementation; the external scope decision preserves the prior allocation and ownership observation.

## Acceptance criteria

- [x] AC-01: JSON Schema and real governance checks accept DockURI-owned operational repositories; invalid owner and standard-hosted runtime cases remain rejected.
- [ ] AC-02: Required source-hub, runtime and protected delivery checks pass, with independent approval before merge.

## Focused evidence

The baseline rejected dockuri in JSON Schema and both runtime projections.
After the change, focused checks accept all five existing/new owners and
preserve unknown-owner, invalid adoption and standard-hosted runtime refusals.
Source and bundled checker bytes match. All 23 source-hub checks pass (56 JSON documents, 22 shell suites), including
real governance fixtures for both subactor and dockuri owners. Goal full Python
tests and independent protected review remain pending; no merge is claimed.

## Current publication base

The accepted base is `dc6bf0b825c7e5d2734e402886c126ac3eeaafb3`, including the approved PR553 bootstrap repair. The native hub permits XS/S classes; this single ownership-vocabulary correction uses class S with its original six-file, two-component and one-interface budgets. No budget or write scope is widened. The rebuilt committed subject requires fresh validation before publication.
