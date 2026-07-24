# Version

## Current Version

`0.5.0`

## Version Type

Minor infrastructure release over `0.4.0`.

This version adds GitHub Actions verification wiring for Windows and Linux and documents the local Codex Windows sandbox limitation for Vitest/Vite process creation. It does not change Intent/Contract runtime approval semantics.

## Project Status

The repository contains a working offline Office DSL MVP, a repeatable scenario runner for the current example fixtures, a standalone canonical Intent/Contract DSL model package, an Office DSL to Intent/Contract migration path, and CI wiring for the default verification workflow.

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
- GitHub Actions workflow for `project.sh install` and `project.sh verify` on Windows and Linux,
- `intent-contract.dsl.v1` model package with formal fields, statuses, source references, canonical serialization, and stable hashing,
- deterministic `officeDslToIntentContractDsl` compatibility adapter with migration notes,
- expanded regression coverage for DSL validation, runtime controls, security policy, CLI workflows, backend API workflows, and file-backed store behavior,
- documented Codex Windows sandbox `spawn EPERM` limitation for Vitest/Vite startup,
- TypeScript and Python tests for the current scope.

Target scope documented but not implemented:

- runtime use of canonical Intent/Contract snapshots for approvals,
- Human1/Human2 bilateral approval,
- planner population of field-level source traceability,
- contract and legal document renderers,
- JS/Node.js code generation,
- DSL-based test generation,
- TypeScript runtime integration with the Python verifier as a normal gating step.

## Included In 0.5.0

- Added `.github/workflows/verify.yml` with an Ubuntu and Windows matrix.
- Added CI steps for checkout, Node.js 22, Python 3.11, Corepack, `bash project.sh install`, and `bash project.sh verify`.
- Added `docs/codex-sandbox-vitest.md` with the exact local sandbox failure mode and reproduction notes.
- Updated root Vitest scripts to run against `tests` and avoid generated/cache paths such as `.pytest_cache` and `verifier/`.
- Updated package, app, verifier, and OpenAPI version metadata to `0.5.0`.

## Not Included In 0.5.0

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
- CI Node.js: `22`.
- CI Python: `3.11`.

Validated in this pass:

- Windows workspace checks listed in the final task report.
- Intent/Contract model and adapter tests.
- Example runner with Python verifier in mock mode.
- Reproduced the Codex Windows sandbox `spawn EPERM` limitation and documented the escalation requirement for full verification in this environment.

Expected but not yet fully validated as release criteria:

- Online OpenRouter planner mode.
- Online LiteLLM/OpenRouter verifier mode.

## Versioning Policy Note

This pass uses a minor bump from `0.4.0` to `0.5.0` because it adds CI workflow infrastructure for the default project verification command.

A future production hardening task should define how root package metadata, package versions, OpenAPI metadata, `VERSION.md`, and `CHANGELOG.md` are kept in sync.
