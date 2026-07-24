# Version

## Current Version

`0.2.0`

## Version Type

Minor feature release over `0.1.1`.

This version adds the first repeatable example-regression workflow and a repository verification command. It does not add the canonical Intent/Contract DSL or Human1/Human2 approval model.

## Project Status

The repository contains a working offline Office DSL MVP plus a repeatable scenario runner for the current example fixtures.

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
- TypeScript and Python tests for the current scope.

Target scope documented but not implemented:

- canonical Intent/Contract DSL,
- Human1/Human2 bilateral approval,
- field-level missing/ambiguous/conflicting/assumed statuses,
- source traceability for every material field,
- contract and legal document renderers,
- JS/Node.js code generation,
- DSL-based test generation,
- TypeScript runtime integration with the Python verifier as a normal gating step.

## Included In 0.2.0

- Added `scenario.json` manifests for all six current examples.
- Added mirrored `in/message.txt` and `out/expected.*.json` fixture structure for all current examples.
- Added `@office-dsl/example-runner`.
- Added `corepack pnpm run example:run -- <scenario>`.
- Added `corepack pnpm run examples:run`.
- Added `corepack pnpm run verify`.
- Added `corepack pnpm run python:test`.
- Added safe command dispatch in `project.sh`.
- Fixed mock verifier action detection so policy subjects are not treated as executed actions.

## Not Included In 0.2.0

- No canonical Intent/Contract DSL implementation.
- No Human2 approval implementation.
- No legal document renderer.
- No JS/Node.js code generator.
- No DSL-based test generator.
- No planner-backed regeneration of current stable expected DSL fixtures.

## Runtime Compatibility Notes

Declared by the repository:

- pnpm: `9.12.0` through `packageManager`.
- TypeScript: `5.7.3`.
- Vitest: `3.0.4`.
- Python verifier: `>=3.11`.

Validated in this pass:

- Windows workspace checks listed in the final task report.
- Example runner with Python verifier in mock mode.

Expected but not yet fully validated as release criteria:

- Linux behavior.
- Online OpenRouter planner mode.
- Online LiteLLM/OpenRouter verifier mode.

## Versioning Policy Note

This pass uses a minor bump from `0.1.1` to `0.2.0` because it adds a new backward-compatible example-runner feature and repository verification command.

A future production hardening task should define how root package metadata, package versions, OpenAPI metadata, `VERSION.md`, and `CHANGELOG.md` are kept in sync.
