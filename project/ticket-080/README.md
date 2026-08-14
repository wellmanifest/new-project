# Ticket 080: Adopt immutable Policy DSL runtime for CONTRIBUTING

- **ID**: ticket-080
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Created**: 2026-08-14

## Goal and scope

Make Policy DSL a managed, immutable source dependency of
`wellmanifest/new-project`. This first bounded slice pins the exact
dependency-free checker, normalizes the policy carriers and makes the source
governance gate plus rule audit validate canonical `dsl` fences. A dependent
slice will install the same byte-verified artifacts into every adopting
repository and connect `scripts/runtime.sh policy` before the versioned release.

The runtime remains inert: parsing a rule never executes its `DO` action and
never grants authority. Unrelated Markdown and shell examples are ignored.

## Acceptance criteria

- [ ] AC-01: The dependency lock binds `wellmanifest/policy-dsl`, its exact
  reviewed revision, checker path, version and SHA-256 without a moving ref.
- [ ] AC-02: The vendored checker validates the complete current
  `CONTRIBUTING.md`, including constants, equations, operators, conditions,
  guarded actions and state transitions.
- [ ] AC-03: A malformed selected Policy DSL fence blocks the governance gate
  with stable `GOV-POLICY-DSL-001`; unrelated Markdown and shell examples do
  not enter the policy document.
- [ ] AC-04: The rule-enforcement audit consumes the pinned Policy DSL runtime
  instead of the optional `wellm`/regex fallback.
- [ ] AC-05: Repositories without `CONTRIBUTING.md` remain valid and no policy
  action is executed during validation.
- [ ] AC-06: Existing focused tests, the full Linux contract and exact-diff
  exact-diff and governance checks pass at the reviewed HEAD.
- [ ] AC-07: The source dependency reaches protected `main`; a dependent
  bounded ticket completes managed-package/runtime adoption before release.

## Dependency evidence

Policy DSL pull request [wellmanifest/policy-dsl#1](https://github.com/wellmanifest/policy-dsl/pull/1)
received an approved Validator App review bound to exact head
`daaf7b7b96312a2469de1b4799f2f81c7396de4e` and merged as
`6fe12f9fcce206c1d69b95f9cac1b4bc8c10abbf`. The implementation revision is
therefore immutable, reachable from protected `main` and eligible for the
managed dependency lock. This ticket has returned to `IN_PROGRESS / EDIT`.

## Risks and mitigations

- A vendored runtime could drift from upstream; the closed lock and SHA-256
  verification fail before parsing.
- Markdown may contain examples in several languages; only the normative
  deterministic `dsl` selector is accepted.
- A parser could be mistaken for an executor; package tests assert that the
  dependency contains no execution adapter and validation only emits IR.

## Participants

- Human participant: unresolved; no `user-*` file was created or modified.
- Agent participant: [ai-codex.md](ai-codex.md).

## Directory boundary

This directory stores governance, decisions, logs and evidence only.
Executable runtime and tests belong in their normal repository paths.
