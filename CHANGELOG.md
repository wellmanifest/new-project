# Changelog

## [0.5.0] - 2026-07-24

### Added

- Added `.github/workflows/verify.yml` to run the repository verification workflow on `ubuntu-latest` and `windows-latest`.
- Added `docs/codex-sandbox-vitest.md` documenting the Codex Windows sandbox `spawn EPERM` failure mode for Vitest/Vite startup and the required escalated verification path in this environment.

### Changed

- Updated root Vitest scripts to run against `tests` and exclude generated/cache paths such as `.pytest_cache` and `verifier/`.
- Updated package, app, verifier, and OpenAPI version metadata to `0.5.0`.

### Known limitations

- The current Codex Windows sandbox still blocks Node/Vite process creation used by Vitest internals, so full verification in this environment requires escalated execution.

## [0.4.0] - 2026-07-24

### Added

- Added `officeDslToIntentContractDsl` to convert validated `office.dsl.v1` tasks into canonical `intent-contract.dsl.v1` snapshots.
- Added migration notes for adapter outputs with source path, target path, mapping decision, field status, and reason.
- Added `docs/office-to-intent-contract-migration.md` documenting the compatibility path and deliberate omissions.

### Changed

- Marked the Phase 2 Office DSL to Intent/Contract migration path as implemented.
- Updated package, app, verifier, and OpenAPI version metadata to `0.4.0`.

### Fixed

- Allowed ready runtime sessions to transition to `DENIED` when explicitly rejected, matching the public reject workflow.

### Tests

- Added Vitest coverage for Office DSL migration validity, clarification steps becoming canonical missing questions, and deterministic hashing of migrated snapshots.
- Expanded Office DSL/runtime regression coverage for unsupported actions, structural validation, dry-run file export, rejection/cancellation, security denials, CLI workflows, backend API workflows, and file-backed task storage.

### Known limitations

- Runtime approval checks still use Office DSL execution plan hashes, not canonical Intent/Contract snapshot hashes.
- The adapter does not infer legal contract terms, payments, deadlines, conflicts, bilateral approvals, or named real parties from Office DSL inputs.

## [0.3.0] - 2026-07-24

### Added

- Added `@office-dsl/intent-contract-model` as the canonical Intent/Contract DSL package boundary separate from `office.dsl.v1`.
- Added `intent-contract.dsl.v1` TypeScript types for document, contract, party, role, intent, subject, obligation, deliverable, deadline, payment, condition, dependency, acceptance criteria, exclusion, assumption, risk, conflict, question, approval, source reference, render, and execution constructs.
- Added field status semantics for `CONFIRMED`, `MISSING`, `INCOMPLETE`, `AMBIGUOUS`, `CONFLICTING`, `ASSUMED`, `REJECTED`, and `NOT_APPLICABLE`.
- Added canonical serialization and SHA-256 hashing helpers for Intent/Contract DSL snapshots.
- Added a service-agreement fixture covering all canonical constructs.

### Changed

- Updated roadmap and docs to classify the canonical Intent/Contract model as implemented at the model layer while leaving runtime integration open.
- Updated package, app, verifier, and OpenAPI version metadata to `0.3.0`.

### Fixed

- No runtime fixes in this release.

### Tests

- Added Vitest coverage for Intent/Contract fixture parsing, field-status validation, required unresolved field validation, canonicalization, and stable hashing.

### Known limitations

- The canonical Intent/Contract model is not yet integrated into the TypeScript runtime, planner, renderer, or approval workflow.
- Office DSL execution still uses `office.dsl.v1` and plan-hash confirmation.
- Migration notes or adapters from `office.dsl.v1` to `intent-contract.dsl.v1` remain open.

## [0.2.0] - 2026-07-24

### Added

- Added canonical `scenario.json` manifests for the six current office examples.
- Added mirrored `in/` and `out/` example fixture folders while keeping legacy fixture files in place.
- Added `@office-dsl/example-runner` with single-scenario and all-scenario commands.
- Added generated example artifacts under `.office-dsl/generated/examples/<scenario-id>/`.
- Added Python verifier execution from the example runner in configured scenarios.
- Added root `verify`, `example:run`, `examples:run`, and `python:test` scripts.
- Added safe `project.sh` command dispatch for install, typecheck, lint, format, tests, examples, verify, and backend startup.

### Changed

- Changed `project.sh` so the old network-heavy analysis workflow runs only through explicit `legacy-analyze`.
- Updated package, app, verifier, and OpenAPI version metadata to `0.2.0`.
- Updated README, TODO, VERSION, and handoff guidance for the new repeatable example workflow.

### Fixed

- Fixed the mock Python verifier so a policy subject mentioning `email.send` is not treated as an executed `email.send` action.

### Tests

- Added Vitest coverage for scenario manifest loading and a real single-scenario runner execution.
- Added Python verifier regression coverage for policy-subject versus action detection.

### Known limitations

- Current example manifests use fixture DSL input because the existing mock planner still emits random task IDs and does not reproduce the stable expected fixtures.
- The example runner supports current Office DSL scenarios; target Intent/Contract scenarios are still roadmap items.
- In the Codex sandbox, `tsx`/Vitest process spawning can require running the command outside the sandbox.

## [0.1.1] - 2026-07-24

### Changed

- Reframed the project documentation around intent formalization and the target Intent/Contract DSL Runtime vision.
- Added `docs/system-purpose-and-runtime-flow.md` with Mermaid diagrams for architecture, NL-to-DSL-to-NL flow, missing-data handling, Human1/Human2 approval, and DSL-to-code/tests/verifier flow.
- Rebuilt `TODO.md` into staged phases with explicit completion criteria and current implementation status.
- Updated `README.md`, `docs/README.md`, `HANDOFF.md`, and `VERSION.md` to clearly separate implemented behavior, partial behavior, mocks, and target architecture.
- Updated root package metadata to `0.1.1` for this documentation-alignment patch.

### Not Added

- No new runtime behavior was implemented.
- No canonical Intent/Contract DSL was implemented.
- No Human1/Human2 bilateral approval was implemented.
- No legal document renderer, code generator, test generator, or example runner was implemented.

## [0.1.0] - 2026-07-23

### Added

- Added offline Office DSL MVP workspace using pnpm workspaces.
- Added `@office-dsl/dsl-model` with `office.dsl.v1` JSON model, parser, structural validation, and human-readable DSL rendering.
- Added `@office-dsl/dsl-runtime` with state machine, policy engine, action registry, dry-run execution, confirmations, clarification answers, plan hashing, file task store, and audit records.
- Added `@office-dsl/llm-planner` with default mock planning and optional OpenRouter planning path.
- Added CLI commands for planning, validation, inspection, answers, confirmation, rejection, execution, and history.
- Added backend API and static web demo using the same runtime as the CLI.
- Added Python verifier package with mock verification and optional LiteLLM/OpenRouter path.
- Added mock data and six example scenarios.
- Added TypeScript, Vitest, ESLint, Prettier, pnpm workspace, and Python verifier configuration.
- Added architecture documentation, research migration audit, handoff notes, and version metadata.

### Changed

- Moved historical research folders into `research/` and verified historical file contents as byte-identical.
- Updated documentation to describe the current MVP implementation instead of only the original documentation standard.
- Treated `project.sh` as historical context, not as the active MVP bootstrap.

### Fixed

- Fixed repository documentation links that pointed at old research folder locations.
- Added ignore rules for Python caches, pytest cache directories, generated runtime output, pnpm store, and mock outbox.

### Security

- Added deterministic policy checks for blocked shell/dynamic-code patterns, path traversal, unsafe email operations, and confirmation requirements.
- Added tests covering path traversal blocking, absence of `eval`/`new Function` in mock output, prompt-injection-as-data behavior, dry-run email sending, and confirmation hash reuse prevention.
- Kept mock mode as the validated default; no real external email/API action is performed by tests.

### Known limitations

- Full Intent/Contract DSL is not complete.
- Bilateral contract approval and contract finalization are not implemented.
- Conversation and file-guidelines inputs are not implemented as first-class planner modes.
- Example regeneration and diff runner is not implemented.
- OpenRouter and LiteLLM code paths are optional but not tested in this offline MVP pass.
- Linux compatibility is not verified in this run.
- Python tests passed with one pytest cache warning caused by a cache directory write denial; test assertions passed.
