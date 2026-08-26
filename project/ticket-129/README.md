# Ticket 129: Enforce role-based standard pack adoption

- **ID**: ticket-129
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Created**: 2026-08-26

## Goal and scope

Make Wellmanifest adoption deterministic across repository roles without
duplicating standards or breaking the fleet during rollout.

## Acceptance criteria

- [ ] AC-01: Every concern has one canonical HOME pack.
- [ ] AC-02: Repository roles map to minimum S0-S5 evidence.
- [ ] AC-03: Managed projection drift is distinguished from source duplication.
- [ ] AC-04: The managed CI gate supports staged audit and enforce modes.

## Risks

- Fleet-wide enforcement remains staged until the immutable release is adopted.

## Participants

- Human participant: unresolved; no user-* file was created.
- Agent participant: [ai-codex.md](ai-codex.md)
