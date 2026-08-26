# Ticket 129: Enforce role-based standard pack adoption

- **ID**: ticket-129
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
- **Created**: 2026-08-26

## Goal and scope

Make Wellmanifest adoption deterministic across repository roles without
duplicating standards or breaking the fleet during rollout.

## Acceptance criteria

- [x] AC-01: Every concern has one canonical HOME pack.
- [x] AC-02: Repository roles map to minimum S0-S5 evidence.
- [x] AC-03: Managed projection drift is distinguished from source duplication.
- [x] AC-04: The managed CI gate supports staged audit and enforce modes.

## Delivery evidence

- Independently merged implementation: `wellmanifest/new-project#220`.
- Merged commit: `54114fbe90e16ba295bebe42df5804301ccba576`.
- The protected merge completed before this governance-only lifecycle closure.

## Risks

- Fleet-wide enforcement remains staged until the immutable release is adopted.

## Participants

- Human participant: unresolved; no user-* file was created.
- Agent participant: [ai-codex.md](ai-codex.md)
