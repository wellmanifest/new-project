# Changelog

## [Unreleased]

## [0.7.5] - 2026-07-27

### Added

- Added the `intent-contract.conversation.v1` input model in `@office-dsl/intent-contract-model` with typed `Human1`, `Human2`, and `system` messages, unique message IDs, ISO timestamps, non-empty text validation, parser support, and source-reference mapping for every conversation line.
- Added a checked-in Human1/Human2 conversation fixture for the canonical model package.

### Changed

- Marked the Phase 4 "Define conversation input format for Human1 and Human2" TODO item as complete at the model layer; planner, CLI, backend, and UI integration remain tracked separately.
- Updated root package, intent-contract model package, `VERSION`, and documentation consistency tests to `0.7.5`.

### Fixed

- Flattened `examples-chat/<scenario>/generated/` event artifacts back into one scenario-local folder instead of `generated/<user>/<event>/` subfolders.
- Standardized generated runner DSL artifacts on `*.dsl.hcl`, replacing chat `summary/status/approvals.dsl.md` files and regular example `actual/verifier-input.*.md` DSL artifacts.
- Updated docs and TODO entries so generated example locations and file formats match the runner behavior.
- Normalized existing DSL model formatting so the repository format check stays green.
- Updated Python verifier tests to call the current text-and-action-list `verify` API.

### Tests

- Added `tests/intent-contract-conversation.test.ts` coverage for valid conversations, invalid versions, duplicate message IDs, invalid speakers, invalid timestamps, empty text, parse errors, and message-to-source-reference mapping.

## [0.7.4] - 2026-07-25

### Added

- Implemented Phase 4 question routing in `@office-dsl/intent-contract-model`:
  - Added `PartyRoute` and `GeneratedQuestion.targetParties`; `diagnoseIntentContractDsl` now routes each generated question to `Human1`, `Human2`, or `unknown`, derived from `SourceReference.speaker`, `ConflictValue.partyId`, party roles, and conflict `sourceIds`.
  - Added `questionsForParty(diagnosis, party)` to filter unresolved-field questions per party.

### Changed

- Marked the Phase 4 "Add runtime routing of questions to Human1 or Human2" TODO item as done at the model layer; live runtime/CLI/UI surfacing remains tracked in Phases 11 and 12.
- Updated root package and `VERSION` metadata to `0.7.4`.

### Tests

- Extended `tests/intent-contract-diagnosis.test.ts` with routing assertions (Human1-sourced ambiguity, unknown routing for unsourced missing fields, both-party conflict routing) and a `questionsForParty` per-party routing case.
- Updated `tests/docs.test.ts` to assert `VERSION`/`CHANGELOG.md` consistency at `0.7.4`.

## [0.7.3] - 2026-07-25

### Added

- Implemented the Phase 3 missing/ambiguous/conflicting information model in `@office-dsl/intent-contract-model`:
  - Added `diagnoseIntentContractDsl` and `collectFormalFields`, producing completeness gaps, ambiguity reports, conflict reports, unapproved-assumption reports, traceability gaps, deterministic generated questions, and a `finalizationReady` gate with `blockingReasons`.
  - Added optional model fields for Phase 3: `SourceReference.span`, `FormalField.interpretations`, and `ConflictNode.values`/`ConflictValue` for competing Human1/Human2 values with source references.
- Added `Phase 4B - Document Ingestion, OCR, And Recruitment Workflow` to `TODO.md`, describing the target multi-candidate recruitment flow (one job offer negotiated against many CVs), document ingestion for `oferta.md`/`cv.md`/`cv.pdf`, PDF text extraction and OCR fallback behind mock-safe interfaces, per-candidate proposal generation, CHAT/EMAIL negotiation reuse, acceptance/rejection finalization, and the `[numer-rekrutacji--stanowisko]/[numer-osoby]/{in/…,out/contract.dsl.txt,chat.txt}` folder convention.
- Referenced the new document ingestion/OCR recruitment workflow in the `TODO.md` baseline `NOT IMPLEMENTED` summary.

### Changed

- Renamed `VERSION.md` to `VERSION` and updated references in `README.md`, `docs/README.md`, `HANDOFF.md`, and `tests/docs.test.ts`; removed the extensionless `VERSION` file from the Prettier format glob.
- Updated root package and `VERSION` metadata to `0.7.3`.

### Tests

- Added `tests/intent-contract-diagnosis.test.ts` covering completeness gaps, ambiguity interpretations with generated questions, Human1/Human2 conflict representation, assumption approval gating, traceability gaps, and finalization readiness.
- Updated `tests/docs.test.ts` to assert `VERSION`/`CHANGELOG.md` consistency at `0.7.3`.

### Changed (previously unreleased)

- Reorganized `.office-dsl/` into per-client folders for runtime state:
  - Task sessions and audit records are now stored under `.office-dsl/<createdBy>/tasks/` and `.office-dsl/<createdBy>/audit/` instead of a flat `.office-dsl/tasks/` + `.office-dsl/audit/` dump.
- Restored example outputs to live beside their scenarios:
  - `examples` runner outputs are placed under `examples/<scenario>/generated/`.
  - `examples-chat` runner outputs are placed under `examples-chat/<scenario>/generated/<user>/<event>/` with a shared `final/` directory.
- Removed JSON from all generated runner artifacts. Generated `.dsl.md` files now use the same plain line-oriented DSL commands as other DSL files (e.g. `VALIDATION`, `PLAN`, `ACTION`, `QUESTION`, `CHAT_STATUS`, `CHAT_SUMMARY`, `CHAT_APPROVALS`).
- Updated `renderHumanDsl` so `WITH` and `WHEN` blocks are rendered as plain DSL instead of embedded JSON strings.
- Updated Python verifier to read DSL/markdown input files (`verifier-input.dsl.md`, `verifier-input.plan.md`) and parse actions directly from the DSL text instead of requiring JSON.
- Restored `examples/*/generated/` and `examples-chat/*/generated/` to `.gitignore`.

### Tests (previously unreleased)

- Updated `store.test.ts` for per-client `FileTaskStore` directory layout.
- Updated `chat-runner.test.ts` paths and assertions to match the restored scenario-side output and plain DSL format.

## [0.7.2] - 2026-07-24

### Changed

- Changed generated chat DSL artifacts to `*.dsl.hcl` so editors can apply HCL/Terraform-style syntax highlighting automatically by file extension.
- Changed the generated chat DSL syntax to HCL-like project DSL blocks such as `document`, `field`, `conflict`, and `change`.
- Moved default generated chat outputs next to each scenario under `examples-chat/<scenario>/generated/` instead of `.office-dsl/generated/examples-chat/<scenario>/`.
- Flattened per-event chat artifacts into prefixed files such as `001-user1.intent-contract.dsl.hcl`, `001-user1.status.json`, and `001-user1.diff.md`.
- Added `examples-chat/*/generated/` to `.gitignore`.
- Updated package, app, verifier, and OpenAPI version metadata to `0.7.2`.

### Tests

- Updated chat runner tests to validate `*.dsl.hcl` artifacts, default generated output placement, and non-JSON DSL/HCL structure.

## [0.7.1] - 2026-07-24

### Changed

- Changed generated `examples-chat` `.dsl` artifacts from JSON serialization to line-oriented editable DSL text using `DOCUMENT`, `FIELD`, `VALUE`, `SOURCE`, and `ASSERT` commands.
- Kept JSON only for machine-comparison files such as `summary.json`, `status.json`, scenario manifests, expected summaries, and `approvals.json`.
- Updated package, app, verifier, and OpenAPI version metadata to `0.7.1`.

### Tests

- Added validation that generated `.dsl` artifacts start with `DOCUMENT`, reject JSON object/array syntax, use only supported DSL commands, and cannot be parsed as JSON.

## [0.7.0] - 2026-07-24

### Added

- Added minimal Human1/Human2 canonical approval records to the TypeScript runtime.
- Added per-session canonical Intent/Contract DSL snapshots and stable snapshot hashes derived from the Office DSL compatibility adapter.
- Added runtime APIs to approve the current canonical DSL hash, check bilateral approval, and invalidate active approvals when the canonical DSL changes.
- Added Vitest coverage for current-hash approval, stale-hash rejection, bilateral approval detection, and approval invalidation after canonical DSL changes.

### Changed

- Runtime audit records now include `intent_contract_hash` and canonical approval records.
- Updated package, app, verifier, and OpenAPI version metadata to `0.7.0`.

### Known limitations

- Canonical approval records are available in runtime APIs but are not yet exposed through CLI, backend, or web flows.
- Office action confirmation still uses plan hashes for current Office DSL execution controls.

## [0.6.0] - 2026-07-24

### Added

- Added executable `examples-chat` scenarios for short agreement, long negotiation agreement, short cancellation, and long cancellation conversations.
- Added a deterministic chat example runner that processes `@user1`/`@user2` conversations line by line, maintains per-party contract state, merges contracts, writes per-event diffs, and compares generated summaries with expected outcomes.
- Added bilateral merged-hash approval checks so final chat artifacts are created only after both parties approve the same current merged contract hash.
- Added deterministic final chat artifacts for agreed scenarios: `final-contract.dsl`, `contract.md`, `contract.pdf`, `approvals.json`, `diff-summary.md`, and `annex.dsl`.
- Added Vitest coverage for chat parsing, scenario discovery, merge behavior, conflict detection, position changes, approval invalidation, finalization, cancellation, and all four chat scenario outcomes.

### Changed

- Added `example-chat:run`, `examples-chat:run`, `project.sh example-chat`, and `project.sh examples-chat` commands.
- Included the chat example runner in the root `verify` flow.
- Updated package, app, verifier, and OpenAPI version metadata to `0.6.0`.

### Known limitations

- The chat negotiation runner is deterministic fixture infrastructure for regression coverage; it is not yet the production planner/runtime integration for arbitrary natural-language contract negotiation.
- The generated PDF is a minimal deterministic renderer for example verification, not a legal document renderer.

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
