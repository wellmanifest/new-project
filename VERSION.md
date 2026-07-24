# Version

## Current Version

`0.4.0`

## Version Type

Minor feature release over `0.3.0`.

This version adds a deterministic compatibility adapter from the current executable `office.dsl.v1` model into the standalone canonical `intent-contract.dsl.v1` model. It does not integrate canonical snapshots into runtime approvals yet.

## Project Status

The repository contains a working offline Office DSL MVP, a repeatable scenario runner for the current example fixtures, a standalone canonical Intent/Contract DSL model package, and an Office DSL to Intent/Contract migration path.

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
- deterministic `officeDslToIntentContractDsl` compatibility adapter with migration notes,
- expanded regression coverage for DSL validation, runtime controls, security policy, CLI workflows, backend API workflows, and file-backed store behavior,
- TypeScript and Python tests for the current scope.

Target scope documented but not implemented:

- runtime use of canonical Intent/Contract snapshots for approvals,
- Human1/Human2 bilateral approval,
- planner population of field-level source traceability,
- contract and legal document renderers,
- JS/Node.js code generation,
- DSL-based test generation,
- TypeScript runtime integration with the Python verifier as a normal gating step.

## Included In 0.4.0

- Added `officeDslToIntentContractDsl` for deterministic Office DSL compatibility snapshots.
- Added migration notes that record `fromPath`, `toPath`, mapping decision, status, and reason.
- Added explicit mapping documentation in `docs/office-to-intent-contract-migration.md`.
- Added tests for Office DSL migration validity, clarification-to-question mapping, and deterministic migrated snapshot hashing.
- Expanded current Office DSL/runtime regression tests around unsupported actions, structural validation, dry-run export, reject/cancel transitions, security denials, CLI workflows, backend API workflows, and `FileTaskStore`.
- Updated package, app, verifier, and OpenAPI version metadata to `0.4.0`.
- Fixed ready-session rejection so explicit rejection can move `READY` sessions to `DENIED`.

## Not Included In 0.4.0

- No runtime approval migration from plan hash to canonical DSL hash.
- No Human2 approval runtime flow.
- No canonical Intent/Contract CLI commands.
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
- Intent/Contract model and adapter tests.
- Example runner with Python verifier in mock mode.

Expected but not yet fully validated as release criteria:

- Linux behavior.
- Online OpenRouter planner mode.
- Online LiteLLM/OpenRouter verifier mode.

## Versioning Policy Note

This pass uses a minor bump from `0.3.0` to `0.4.0` because it adds a new backward-compatible adapter and migration documentation.

A future production hardening task should define how root package metadata, package versions, OpenAPI metadata, `VERSION.md`, and `CHANGELOG.md` are kept in sync.
