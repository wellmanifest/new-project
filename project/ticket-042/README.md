# Ticket 042: Preserve deleteBranchOnMerge in protected lifecycle snapshot

- **ID**: ticket-042
- **Owner**: agent:codex
- **Status**: BLOCKED
- **Workflow state**: BLOCKED
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

- [x] AC-01: The protected workflow always writes a boolean
  `deleteBranchOnMerge` obtained from the typed GraphQL repository field.
- [x] AC-02: Missing or malformed lifecycle facts remain rejected by the
  unchanged deterministic validator.
- [x] AC-03: Branch-lifecycle, governance, adoption, Linux, Windows and Docker
  contracts pass.
- [ ] AC-04: A clean downstream protected run no longer reports a missing
  `deleteBranchOnMerge` field.

## Validation evidence

- Implementation commit: `7f836f055976887a8701e635efa9747ab43acfb8`.
- `bash tests/branch-lifecycle.test.sh`: PASS, including the new GraphQL
  acquisition regression and unchanged strict malformed-snapshot cases.
- Full Linux CI command contract: PASS across JSON, required checks, decision
  replay, governance scripts/validator/environment, lifecycle, adoption lock
  and rule-enforcement suites.
- Local PowerShell is unavailable; the protected `windows-governance` job
  remains required before merge.
- The standard source repository has no Dockerfile or compose definition; its
  authoritative runtime contract is the Linux/Windows CI matrix. Downstream
  todo2code Docker smoke already passes for the adopting payload.
- Protected PR #62 passed `test` and `windows-governance`; trusted Validator
  App approved exact head `2a0001a7ddde314d3af5a7d23553869d01f70bb6`.
  The PR merged as `main@b01cae0f47bb311d1e795600af49e0ba436e175d`.
- AC-04 requires an immutable release and downstream protected execution. The
  ticket is `BLOCKED` without reserving the governance workstream until the
  release ticket publishes v0.13.2 and todo2code adopts it.

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
