# Ticket 260: Standardize root LICENSE in governance workstream

- **ID**: ticket-260
- **Owner**: antigravity
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Created**: 2026-09-22

## Goal and scope

Standardize root `LICENSE` recognition and template in the wellmanifest standard:
1. Add `LICENSE*` pattern to `governance` workstream `ownedPaths` in `governance/manifest.default.json`.
2. Add Apache-2.0 template file at `template/files/LICENSE.template`.

## Acceptance criteria

- [x] AC-01: `governance/manifest.default.json` includes `LICENSE*` under governance `ownedPaths`.
- [x] AC-02: `template/files/LICENSE.template` exists as canonical Apache-2.0 template.
- [x] AC-03: Governance checks pass cleanly.
