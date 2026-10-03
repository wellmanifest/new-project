# Ticket 307: Migrate minimal Wellman scaffolds through pinned native adoption

- **ID**: ticket-307
- **Owner**: agent:codex
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Created**: 2026-10-03

## Goal and scope

SESSION_EXECUTION_AUTHORIZATION: the user requested fleet-wide Wellmanifest
adoption and continued repair, testing and protected publication. Exact minimal
Wellman baseline scaffolds currently cannot extend the complete native manifest,
so the published adopter refuses them before writing. Add an explicit migration
for only that closed shape. Preserve custom/native manifests, immutable locks,
source publication proof, target prerequisites and protected delivery. Product
changes and controller admission/enrollment stay outside this standard ticket.

## Acceptance criteria

- [x] AC-01: Default refusal stays intact; explicit review/apply works only for
  the exact minimal baseline scaffold without native adoption evidence.
- [x] AC-02: Adversarial CLI, existing adoption and package checks plus native
  governance pass; unrelated target files are preserved.
- [ ] AC-03: Independent exact-head approval and protected merge precede
  immutable standard 0.20.81 publication and readback.
