# Ticket 042: Preserve deleteBranchOnMerge in protected lifecycle snapshot

- **ID**: ticket-042
- **Owner**: agent:codex
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-08-08

## Cel i zakres

The v0.13.1 protected governance workflow obtains repository metadata through
`repos.get` and copies `repository.data.delete_branch_on_merge` into the strict
branch-lifecycle snapshot. In a downstream GitHub Actions run the restricted
`GITHUB_TOKEN` response omitted that REST field, so `JSON.stringify` omitted
`deleteBranchOnMerge` and the deterministic validator rejected an otherwise
correct repository with `GOV-BRANCH-LIFECYCLE-003`.

Acquire the boolean through GitHub's typed GraphQL `Repository.deleteBranchOnMerge`
field while retaining REST acquisition for the default branch. Keep the strict
snapshot schema and fail-closed validator unchanged. Add a static workflow
regression so releases cannot silently return to the optional REST property.

## Kryteria odbioru

- [ ] AC-01: The protected workflow always writes a boolean
  `deleteBranchOnMerge` obtained from the typed GraphQL repository field.
- [ ] AC-02: Missing or malformed lifecycle facts remain rejected by the
  unchanged deterministic validator.
- [ ] AC-03: Branch-lifecycle, governance, adoption, Linux, Windows and Docker
  contracts pass.
- [ ] AC-04: A clean downstream protected run no longer reports a missing
  `deleteBranchOnMerge` field.

## Ryzyka i uwagi

- GraphQL acquisition remains protected network I/O; only the captured strict
  snapshot crosses into the deterministic validator.
- No fallback value is inferred. API failure or a non-boolean response still
  fails closed.
- Publishing an immutable patch release and downstream adoption will be a
  separate governed release ticket after this repair merges.

The user explicitly approved implementation on 2026-08-08 and requested that
diagit be used during delivery. Diagit clean release code audited both
organizations successfully and confirmed only the two active ticket branches
and todo2code PR #70; its main development worktree remains untouched because
it contains unrelated in-progress changes.

## Uczestnicy

- Human participant: unresolved; no `user-*` file was created.
- Agent participant: `ai-codex.md`.

## Granica katalogu

This directory stores governance evidence only. Workflow implementation and
tests remain under `.github/workflows/` and `tests/`.
