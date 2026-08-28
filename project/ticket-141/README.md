# Ticket 141: Atomic adoption target bindings

- **ID**: ticket-141
- **Owner**: unresolved:human
- **GitHub issue**: #240
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Created**: 2026-08-28

## Goal and scope

Allow one explicitly declared atomic standard-adoption ticket to install the
verified managed payload and the mandatory target-local adoption bindings
without granting ordinary changes a general cross-workstream bypass.

## Acceptance criteria

- [ ] AC-01: A realistic Python/npm/Docker adoption fixture passes with its managed payload, package bindings and immutable images.
- [ ] AC-02: An unrelated application source change in the same adoption remains rejected by workstream ownership.
- [ ] AC-03: Existing ownership, atomic adoption and mutation tests remain green.

## Risk

The exception must be derived from explicit standard-adoption semantics and a
closed set of target bindings; it must not turn the integration workstream into
an unrestricted repository-wide owner.
