# Version

## Current Version

`0.1.1`

## Version Type

Documentation-alignment patch over the `0.1.0` offline Office DSL MVP.

This version clarifies the real project direction and implementation boundaries. It does not add new runtime features.

## Project Status

The repository currently contains a working offline Office DSL MVP and a newly aligned documentation/backlog layer for the target Intent/Contract DSL Runtime.

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
- static example fixtures,
- TypeScript and Python tests for the current scope.

Target scope documented but not implemented:

- canonical Intent/Contract DSL,
- Human1/Human2 bilateral approval,
- field-level missing/ambiguous/conflicting/assumed statuses,
- source traceability for every material field,
- contract and legal document renderers,
- example runner with regeneration and diffs,
- JS/Node.js code generation,
- DSL-based test generation,
- TypeScript runtime integration with the Python verifier.

## Included In 0.1.1

- Added `docs/system-purpose-and-runtime-flow.md`.
- Updated README to separate current implementation, partial behavior, mocks, and target architecture.
- Rebuilt TODO into phased roadmap with concrete completion criteria.
- Updated documentation index and handoff notes.
- Updated changelog and root package metadata for a documentation-only patch release.

## Not Included In 0.1.1

- No runtime rewrite.
- No new DSL implementation beyond `office.dsl.v1`.
- No Human2 approval implementation.
- No verifier orchestration from TypeScript runtime.
- No example runner implementation.
- No code/test generation.

## Runtime Compatibility Notes

Declared by the repository:

- pnpm: `9.12.0` through `packageManager`.
- TypeScript: `5.7.3`.
- Vitest: `3.0.4`.
- Python verifier: `>=3.11`.

Validated in this documentation pass:

- Windows workspace checks listed in the final task report.

Expected but not yet fully validated as release criteria:

- Linux behavior.
- Online OpenRouter planner mode.
- Online LiteLLM/OpenRouter verifier mode.

## Versioning Policy Note

The repository does not yet define a formal release policy. This pass uses a conservative patch bump from `0.1.0` to `0.1.1` because it changes documentation, roadmap, and repository metadata without adding runtime features.

A future production hardening task should define how root package metadata, package versions, OpenAPI metadata, `VERSION.md`, and `CHANGELOG.md` are kept in sync.
