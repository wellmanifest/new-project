# Ticket 137: Own monorepo packages in application workstream

- **ID**: ticket-137
- **GitHub issue**: #225
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-08-28

## Cel i zakres

Make the default application workstream own conventional monorepo package
roots so adopters do not need a local governance override for application code.

## Kryteria odbioru

- [ ] AC-01: Default application ownership includes `packages/**`.
- [ ] AC-02: Conformance tests cover monorepo package ownership.
- [ ] AC-03: Full governance hub test contract passes.

## Ryzyka i uwagi

- Existing adopters receive the new ownership only through an explicit immutable
  standard upgrade; no target repository is silently changed.
