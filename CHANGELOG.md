# Changelog

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
