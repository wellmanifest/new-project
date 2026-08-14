# Ticket 080: Adopt immutable Policy DSL runtime for CONTRIBUTING

- **ID**: ticket-080
- **Owner**: unresolved:human
- **Status**: PLAN
- **Workflow state**: PLAN
- **Created**: 2026-08-14

## Goal and scope

Make Policy DSL a managed, immutable dependency of `wellmanifest/new-project`.
The published package will install the exact dependency-free checker and a
closed upstream lock into every adopting repository. If `CONTRIBUTING.md`
exists, the governance gate and `scripts/runtime.sh policy` validate its
canonical `dsl` fences before evaluating or auditing repository rules.

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
- [ ] AC-04: `scripts/runtime.sh policy` and rule-enforcement audit consume the
  pinned Policy DSL runtime instead of the optional `wellm`/regex fallback.
- [ ] AC-05: The immutable adoption package installs and hash-locks the policy
  checker and dependency lock in every target repository.
- [ ] AC-06: Repositories without `CONTRIBUTING.md` remain valid and no policy
  action is executed during validation.
- [ ] AC-07: Focused tests, the full Linux contract, package/adoption tests,
  exact-diff and governance checks pass at the reviewed HEAD.
- [ ] AC-08: The change is released through protected publication so targets
  can adopt a published `new-project` revision containing the immutable pin.

## Current prerequisite

Policy DSL pull request [wellmanifest/policy-dsl#1](https://github.com/wellmanifest/policy-dsl/pull/1)
is open at exact head `7407fc5bd9f6b04477f3912658bbf2b580513a01`.
Its remote lifecycle check is green, but independent exact-head review is still
required. This ticket remains `PLAN / PLAN`, which releases the governance
workstream while that external publication boundary is pending.

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
