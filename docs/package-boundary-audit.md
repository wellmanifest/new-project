# Package Boundary Audit

Date: 2026-07-27

This audit checks whether the repository has more issues similar to the earlier PDF generator problem: functionality that should live in a dedicated package, shared module, or single source of truth but is still embedded in an example runner, CLI file, or duplicated helper.

## Scope

Reviewed areas:

- packages under `packages/`
- example runners and generated artifact helpers
- CLI and shell verifier paths
- documentation/version status that could mislead future work

The PDF generator package is treated as the resolved baseline. `packages/pdf-generator` now exists and exports deterministic Markdown-to-PDF fixture generation.

## Findings

### P1 - Chat negotiation engine is embedded in the example runner

Evidence: `packages/example-runner/src/chat.ts` contains chat parsing, line-by-line interpretation, party state, contract merge logic, approval invalidation, finalization rules, DSL rendering, expected-output comparison, and artifact writing.

Why this is a problem: `@office-dsl/example-runner` should orchestrate runnable fixtures. The Human1/Human2 negotiation domain engine is reusable product logic and should be testable without the example runner.

Recommended action: extract a package such as `@office-dsl/chat-negotiation` or `@office-dsl/negotiation-engine`. Keep examples responsible only for loading `scenario.json`, `chat.txt`, expected artifacts, and calling the package.

### P1 - Recruitment workflow is embedded in the example runner

Evidence: `packages/example-runner/src/recruitment.ts` contains document process execution, Markdown/PDF/OCR fixture routing, candidate status/proposal generation, source reference extraction, Intent/Contract DSL rendering, and expected-output comparison.

Why this is a problem: recruitment ingestion and proposal generation are application workflow logic, not only example orchestration.

Recommended action: extract one or two packages, for example `@office-dsl/document-ingestion` for md/pdf/ocr fixture flow and `@office-dsl/recruitment-workflow` for candidate/proposal/contract workflow.

### P2 - DSL artifact rendering helpers are duplicated

Evidence: `packages/example-runner/src/scenario.ts`, `packages/example-runner/src/chat.ts`, and `packages/example-runner/src/recruitment.ts` each contain local helpers for DSL/HCL-style artifact writing such as block/assignment/string quoting and specific `render...Dsl` functions.

Why this is a problem: after the decision that generated DSL files must not be JSON, the DSL textual format needs one writer/validator boundary. Local renderers make it easy for examples to drift into incompatible syntax.

Recommended action: create a shared package such as `@office-dsl/dsl-artifact-renderer`, or extend the existing DSL/model packages with a canonical text writer and parser/validator.

### P2 - Regression comparison logic is duplicated

Evidence: example runner modules implement separate `compareSubset`, stable sort/stringify, and expected summary comparison helpers.

Why this is a problem: every example family can accidentally compare expected output differently. That weakens regression tests.

Recommended action: extract a small `@office-dsl/regression-runner` or test utility package that owns stable JSON, subset comparison, artifact existence checks, and readable mismatch reporting.

### P2 - Python verifier bridge is split across packages

Evidence: `packages/dsl-runtime/src/python-verifier.ts` owns one Python semantic verifier invocation path, while `packages/example-runner/src/scenario.ts` has its own Python verifier runner and `PYTHONPATH` handling.

Why this is a problem: Python invocation, environment setup, and failure reporting should be one maintained boundary.

Recommended action: create or centralize into `@office-dsl/verifier-bridge`, then make runtime, CLI, and examples call it.

### P2 - CLI mock verifier code is duplicated

Evidence: `packages/cli/src/index.ts` and `packages/cli/src/shell.ts` both contain a `mockVerification` implementation.

Why this is a problem: CLI and shell can diverge on the same CQRS/verification behavior.

Recommended action: move the mock verifier behind one shared verifier interface used by both CLI entrypoints.

### P2 - Internal package boundaries are bypassed by source-relative imports

Evidence: packages import each other through paths like `../../pdf-generator/src/index.js`, `../../intent-contract-model/src/index.js`, and other `../../.../src/index.js` imports.

Why this is a problem: packages exist, but they are not fully package-clean. Source-relative imports bypass `package.json` dependency declarations and make the packages harder to publish, test, or consume independently.

Recommended action: add workspace dependency declarations and import through package names, for example `@office-dsl/pdf-generator`, once the build setup supports it reliably.

### P2 - Documentation contains stale implementation status

Evidence found during audit:

- `docs/system-purpose-and-runtime-flow.md` still says bilateral Human1/Human2 approval, canonical Intent/Contract DSL, legal document rendering, JS code generation, DSL-based test generation, and Python verifier integration are not implemented or not connected in places where the repo now has implementations or partial implementations.
- `docs/architecture.md` still says `project.sh` is historical/not active, but the current workflow uses `project.sh` for verification.
- `VERSION` under current version notes still lists some already-created capabilities as not included.

Why this is a problem: future agents and maintainers can make wrong decisions from stale docs.

Recommended action: run a dedicated docs consistency pass before GUI phases. Do not only update changelog; fix architecture/status pages too.

### P3 - Version policy for packages is unclear

Evidence: the root and some new/current packages are at `0.12.0`, while older packages remain at earlier versions. This may be intentional independent versioning, but no clear policy was found during this audit.

Why this matters: when the user asks to update `VERSION.md` and other version sources, it is unclear which package versions must move together.

Recommended action: document whether packages use lockstep or independent versions. If lockstep is intended, add a script/test that checks package version consistency.

### P3 - TODO contains stale next-task entries

Evidence: `TODO.md` still lists some next implementation tasks that appear already implemented, such as runtime-to-Python verifier invocation and canonical Intent/Contract CLI commands.

Why this matters: work selection from TODO can repeat completed tasks or skip the real next boundary cleanup.

Recommended action: update TODO after the package-boundary cleanup decision. Mark only verified completed items and move boundary extraction tasks into the next non-GUI milestone.

## Recommended Next Milestone

Before starting GUI-focused phases, make the examples-first application easier to maintain by extracting these boundaries:

1. `@office-dsl/chat-negotiation`
2. `@office-dsl/document-ingestion` and/or `@office-dsl/recruitment-workflow`
3. `@office-dsl/dsl-artifact-renderer`
4. `@office-dsl/regression-runner` or shared comparison utilities
5. one verifier bridge used by runtime, CLI, shell, and examples

## Non-goals

This audit does not implement Phase 12, Phase 13, or Phase 14. It only lists boundary and consistency issues that should be fixed while the project remains examples-first.
