# Ticket 273: Use canonical release tag in adopter runtime install and publish 0.20.52

## Metadata

- **Owner**: agent:codex
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT

## Outcome

Generated adopter CI currently asks pip to install `wellman-v<version>`, but standard releases are published as immutable `v<version>` tags. Make adopter and reusable workflows agree on the canonical standard tag, guard both paths with a regression, and publish the correction as standard 0.20.52.

## Acceptance criteria

- [ ] AC-01: Wellman package regression asserts both generated adopter CI and reusable CI install from canonical `v<version>`.
- [ ] AC-02: Required checks, managed governance gate and diff checks pass on the ticket HEAD.
- [ ] AC-03: Protected exact-head CI and independent Validator pass, the protected controller merges, clean merged-SHA retests pass, and Goal publishes immutable `v0.20.52`.

## Authorization and ownership

SESSION_EXECUTION_AUTHORIZATION: the user requested continued implementation, testing, protected merge and publication. On 2026-09-24 the user explicitly approved one additional disjoint corrective release ticket despite the hub WIP limit: “Tak — jeden ticket naprawczo-wydaniowy”. The process-local admission exception is bounded to this allocation; the tracked WIP limit remains 1. Ticket-270 and its owner remain untouched. No review or CI gate is waived.

## Scope and risks

This ticket changes only the release projections, generated adopter runtime source and its regression. It does not change ticket-270 paths or permanent governance capacity. The immutable release must bind the reviewed and retested merged SHA.

## Validation

Run the Wellman package regression, required-checks regression, managed governance gate and `git diff --check`, then use Goal and the independent Validator for exact-head delivery.
