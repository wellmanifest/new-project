# Ticket 247: Harmonize adopter manifest workstreams and enhance adoption upgrade tooling

- **ID**: ticket-247
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Created**: 2026-09-19

## Goal and scope

SESSION_EXECUTION_AUTHORIZATION: On 2026-09-19 user requested ongoing fleet standards study, logical improvements and harmonization across the organization.
Harmonize workstream separation in `governance/manifest.default.json` to permanently eliminate the deadlock between `integration` and `governance` workstreams across adopting repositories (`GOV-INTEGRATION-001` vs `GOV-WORKSTREAM-003`). Enhance `scripts/create_adoption_lock.py` to gracefully handle legacy governance callers and automatically run `install-agent-hosts.sh` and `render_dsl_manifest.py` post-adoption.

## Acceptance criteria

- [x] AC-01: `manifest.default.json` workstreams are completely orthogonal: `integration` contains only domain contracts and build manifests; `governance` owns all managed standard files.
- [x] AC-02: `create_adoption_lock.py` filters legacy governance workflow callers and activates agent hosts hooks automatically upon adoption.
- [x] AC-03: Conformance tests and governance gate pass cleanly.

## Boundary

This directory holds the minimal reviewed intent.
