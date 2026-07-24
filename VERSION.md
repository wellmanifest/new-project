# Version

## Current Version

`0.3.0`

## Version Type

Minor feature release over `0.2.0`.

This version adds the first canonical Intent/Contract DSL model package. It does not integrate that model into the Office DSL runtime, planner, renderer, or Human1/Human2 approval flow yet.

## Project Status

The repository contains a working offline Office DSL MVP, a repeatable scenario runner for the current example fixtures, and a standalone canonical Intent/Contract DSL model package.

Current validated implementation scope:

- single-request Office DSL planning through mock planner,
- `office.dsl.v1` JSON validation,
- TypeScript runtime orchestration,
- deterministic policy checks,
- simple clarification questions,
- one-side confirmation with plan hash,
- mock dry-run execution,
- audit output,
- CLI, backend API, static web demo,
- Python mock verifier package,
- canonical example manifests with `in/` and `out/` folders,
- deterministic single-example and all-example runner,
- root verification command,
- `intent-contract.dsl.v1` model package with formal fields, statuses, source references, canonical serialization, and stable hashing,
- TypeScript and Python tests for the current scope.

Target scope documented but not implemented:

- runtime use of the canonical Intent/Contract DSL,
- Human1/Human2 bilateral approval,
- planner population of field-level source traceability,
- contract and legal document renderers,
- JS/Node.js code generation,
- DSL-based test generation,
- TypeScript runtime integration with the Python verifier as a normal gating step.

## Included In 0.3.0

- Added `@office-dsl/intent-contract-model`.
- Added `intent-contract.dsl.v1` versioned model boundary.
- Added TypeScript types for core Intent/Contract constructs.
- Added `FormalField<T>` with status, required-for-completion, source, and approvals.
- Added `SourceReference` for message, conversation, file, human, system, and derived sources.
- Added structural validation for field statuses and unresolved required fields.
- Added canonical JSON serialization and stable SHA-256 hashing helpers.
- Added a service-agreement fixture covering the current canonical constructs.
- Added Vitest tests for parsing, validation, status rules, canonicalization, and hashing.

## Not Included In 0.3.0

- No Office DSL to Intent/Contract DSL adapter.
- No runtime approval migration from plan hash to canonical DSL hash.
- No Human2 approval runtime flow.
- No legal document renderer.
- No JS/Node.js code generator.
- No DSL-based test generator.

## Runtime Compatibility Notes

Declared by the repository:

- pnpm: `9.12.0` through `packageManager`.
- TypeScript: `5.7.3`.
- Vitest: `3.0.4`.
- Python verifier: `>=3.11`.

Validated in this pass:

- Windows workspace checks listed in the final task report.
- Intent/Contract model package tests.
- Example runner with Python verifier in mock mode.

Expected but not yet fully validated as release criteria:

- Linux behavior.
- Online OpenRouter planner mode.
- Online LiteLLM/OpenRouter verifier mode.

## Versioning Policy Note

This pass uses a minor bump from `0.2.0` to `0.3.0` because it adds a new backward-compatible model package and fixtures.

A future production hardening task should define how root package metadata, package versions, OpenAPI metadata, `VERSION.md`, and `CHANGELOG.md` are kept in sync.
