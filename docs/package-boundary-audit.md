# Package Boundary Audit

Date: 2026-07-27
Status: resolved in the package-boundary milestone

This audit checked whether the repository had more issues similar to the earlier PDF generator problem: functionality that should live in a dedicated package, shared module, or single source of truth but was embedded in an example runner, CLI file, or duplicated helper.

## Scope

Reviewed areas:

- packages under `packages/`
- example runners and generated artifact helpers
- CLI and shell verifier paths
- documentation/version status that could mislead future work

## Resolution Summary

The audit findings have been fixed by extracting dedicated packages, switching internal code to package-name imports, documenting a lockstep package/app version policy, and adding `tests/package-boundary.test.ts` as a regression guard.

Resolved package boundaries:

- `@office-dsl/pdf-generator` owns deterministic minimal PDF generation and fixture text extraction.
- `@office-dsl/chat-negotiation` owns Human1/Human2 chat parsing, line-by-line negotiation, party states, merge, conflict detection, approval invalidation, finalization, and chat artifacts.
- `@office-dsl/document-ingestion` owns deterministic `md2pdf`/`pdf2md` fixture processing and mock-safe OCR fallback routing.
- `@office-dsl/recruitment-workflow` owns recruitment candidate orchestration, proposals, source mapping, per-candidate chat reuse, and acceptance/rejection summaries.
- `@office-dsl/dsl-artifact-renderer` owns shared DSL/HCL block, assignment, quoting, indentation, and file-writing helpers.
- `@office-dsl/regression-runner` owns stable JSON sorting and subset/full comparison helpers.
- `@office-dsl/verifier-bridge` owns Python verifier invocation, verifier input files, environment setup, and `PYTHONPATH` handling.
- `@office-dsl/verifier-mock` owns the shared CLI/shell mock verifier.

## Fixed Findings

### P1 - Chat negotiation engine was embedded in the example runner

Fixed: the implementation moved to `packages/chat-negotiation/src/index.ts`. `packages/example-runner/src/chat.ts` is now a compatibility re-export, so the example runner only discovers and invokes fixtures.

Guard: `tests/package-boundary.test.ts` requires `@office-dsl/chat-negotiation` to exist and prevents source-relative package imports.

### P1 - Recruitment workflow was embedded in the example runner

Fixed: recruitment orchestration moved to `packages/recruitment-workflow/src/index.ts`, while document process execution moved further down to `packages/document-ingestion/src/index.ts`. `packages/example-runner/src/recruitment.ts` is now a compatibility re-export.

Guard: `tests/package-boundary.test.ts` requires both packages and checks their workspace dependencies.

### P2 - DSL artifact rendering helpers were duplicated

Fixed: common DSL/HCL writer helpers moved to `@office-dsl/dsl-artifact-renderer` and are used by the extracted chat, recruitment, and example-runner scenario flows.

Guard: package imports and dependencies are checked by `tests/package-boundary.test.ts`.

### P2 - Regression comparison logic was duplicated

Fixed: stable JSON and subset/full comparison helpers moved to `@office-dsl/regression-runner` and are used by chat, recruitment, and general scenario comparison paths.

Guard: package imports and dependencies are checked by `tests/package-boundary.test.ts`.

### P2 - Python verifier bridge was split across packages

Fixed: Python verifier execution and environment handling moved to `@office-dsl/verifier-bridge`. `@office-dsl/dsl-runtime` re-exports the semantic verifier through its existing public API, and the example runner calls `runOfficeDslVerifier` from the same bridge.

Guard: package imports and dependencies are checked by `tests/package-boundary.test.ts`.

### P2 - CLI mock verifier code was duplicated

Fixed: CLI and shell now import `mockVerification` from `@office-dsl/verifier-mock`.

Guard: package imports and dependencies are checked by `tests/package-boundary.test.ts`.

### P2 - Internal package boundaries were bypassed by source-relative imports

Fixed: package/app source imports now use `@office-dsl/*` package names instead of `../../.../src/index.js` style imports. `package.json` files declare internal dependencies with `workspace:*`, and `@office-dsl/dsl-runtime` exposes `./store` for the file store subpath.

Guard: `tests/package-boundary.test.ts` fails when packages/apps reintroduce source-relative package imports or omit workspace dependency declarations.

### P2 - Documentation contained stale implementation status

Fixed: `VERSION`, `TODO.md`, `CHANGELOG.md`, `docs/system-purpose-and-runtime-flow.md`, `docs/architecture.md`, and `docs/README.md` were updated to describe the current package-level boundaries and the remaining production wiring gaps.

Guard: existing docs tests plus the boundary test reduce the chance that package status drifts again.

### P3 - Version policy for packages was unclear

Fixed: workspace packages and apps now use lockstep `0.12.0` package metadata for this milestone.

Guard: `tests/package-boundary.test.ts` asserts package/app versions remain at `0.12.0` for this release line.

### P3 - TODO contained stale next-task entries

Fixed: already-implemented next-task entries for runtime-to-Python verifier invocation and canonical Intent/Contract CLI commands were removed from the immediate next-task list, and a completed package-boundary extraction item was added.

## Current Next Milestone

The next non-GUI milestone should use the extracted packages rather than adding more logic to the example runner. The important remaining work is production wiring: expose canonical approvals, document rendering, code generation, test generation, and semantic verification through runtime/CLI/backend flows without duplicating business logic.

## Non-goals

This audit resolution does not implement Phase 12, Phase 13, or Phase 14. The project remains examples-first until production GUI/backend wiring is explicitly prioritized.
