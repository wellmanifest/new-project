# Changelog

## [Unreleased]

### Added

- Added `docs/project-summary.md` with current project status, architecture and workflow diagrams, verification evidence, and remaining production work.
- Added `script/readme.sh`, root `Makefile` documentation targets, generated README include menu, per-example README files, and CI documentation freshness checks.
- Added a generated examples artifacts index command that merges office, chat, and recruitment example inputs, expected fixtures, and output links into one Markdown file.
- Added three more `examples-recruitment` scenarios so the recruitment fixture set now has four runnable cases covering single acceptance, negotiated acceptance, PDF text extraction, OCR fallback, and cancellation.
- Added `@office-dsl/chat-negotiation`, `@office-dsl/recruitment-workflow`, `@office-dsl/document-ingestion`, `@office-dsl/dsl-artifact-renderer`, `@office-dsl/regression-runner`, `@office-dsl/verifier-bridge`, and `@office-dsl/verifier-mock` package boundaries.
- Added `tests/package-boundary.test.ts` to guard extracted packages, package-name imports, workspace dependency declarations, and lockstep package/app versions.

- Added `@office-dsl/pdf-generator` as a standalone package for deterministic minimal PDF generation and fixture text extraction, and moved chat/recruitment PDF generation out of `@office-dsl/example-runner`.
- Added `system:check`, `project.sh system-check`, and Windows `project.bat system-check` aliases for the full functional system test suite, plus regression coverage that keeps TypeScript tests, Python verifier tests, examples, chat examples, recruitment examples, formatting, linting, typechecking, and whitespace checks wired together.

### Changed

- Moved checked-in expected JSON fixtures from `out/` to `expected/` across office, chat, and recruitment examples so `out/` stays reserved for generated/result artifacts.
- Standardized `examples-recruitment` document conversion fixtures so every md2pdf/pdf2md process is a scenario-level one-process folder with its own `in/`, `out/`, and `test.json`.
- Moved chat negotiation, recruitment workflow, deterministic document ingestion/OCR fixture processing, DSL artifact rendering, regression comparison, Python verifier invocation, and CLI mock verification out of example-runner/CLI internals.
- Updated all workspace package/app versions to `0.12.0` and replaced internal source-relative package imports with package-name imports plus `workspace:*` dependencies.
- Updated stale architecture/status documentation for `project.sh`, bilateral approval, renderers, codegen, testgen, and Python verifier integration.

## [0.12.0] - 2026-07-27

### Added

- Added `script/readme.sh`, root `Makefile` documentation targets, generated README include menu, per-example README files, and CI documentation freshness checks.
- Added explicit Phase 10 LiteLLM/OpenRouter semantic verifier mode for `verify_semantic(..., mode="openrouter")`, including structured `semantic-verifier.report.v1` provider parsing, deterministic monkeypatched adapter coverage, and an opt-in live smoke test gated by `RUN_OPENROUTER_SEMANTIC_TEST=1` plus `OPENROUTER_API_KEY`.
- Added Phase 11 cross-platform CLI surface in `packages/cli`: `well-manifest-intent` entry point with canonical Intent/Contract commands (`plan`, `plan-file`, `render`, `testgen`, `codegen`, `verify`, `approve`, `chat`, `example`, `recruitment`, `version`, `help`).
- Added `packages/cli/src/cross-platform.ts` helpers for `file://` URL decoding, POSIX/Windows separator normalization, and dynamic-import safe URL conversion.
- Added `--json` and `--human` output modes for all canonical CLI commands.
- Added `project.bat` Windows equivalent for `./project.sh` validation commands.
- Added `tests/cli-cross-platform.test.ts` coverage for POSIX-style paths on Windows, `file://` URLs, JSON/human output modes, and canonical Intent/Contract command dispatch.

### Changed

- Marked Phase 10 complete for the Python semantic verifier boundary while keeping default verification offline and mock-safe.
- Updated root package, dsl-runtime package, verifier package, `VERSION`, and documentation consistency tests to `0.12.0`.
- Marked Phase 11 TODO items complete for canonical Intent/Contract CLI commands and Windows/Linux path compatibility.

## [0.11.0] - 2026-07-27

### Added

- Added `script/readme.sh`, root `Makefile` documentation targets, generated README include menu, per-example README files, and CI documentation freshness checks.
- Added Phase 5 bidirectional NL <-> DSL support in `@office-dsl/llm-planner` with a controlled `intent-contract.planner-response.v1` schema, OpenRouter prompt boundary, schema validation, and canonical Intent/Contract DSL conversion.
- Added deterministic single-message NL planning for canonical Intent/Contract DSL fields with source references, explicit missing governing-law handling, payment, deadline, deliverable, acceptance, and exclusion extraction.
- Added guideline-file planning for text guidelines with file-backed source references and missing-field preservation.
- Added DSL-to-NL summary rendering as `intent-contract.nl-summary.v1`, where each rendered statement carries the source DSL path, field name, and optional source id.
- Added rendered-statement path extraction for round-trip regression checks.
- Added Phase 6 contract and legal document renderers in the new `@office-dsl/document-renderer` package: `renderTaskDelegation`, `renderServiceAgreement`, `renderEmploymentAgreement`, and a `renderDocument` dispatcher.
- Added the shared `DRAFT_DISCLAIMER` embedded in every rendered document, marking output as a non-binding draft that must not invent terms.
- Added explicit gap and unapproved-assumption handling so missing, ambiguous, conflicting, or rejected fields render as `[GAP: ...]` markers instead of fabricated legal language.
- Added a document-to-DSL traceability map (`traceability` array plus a `Traceability Map` table) linking each rendered item to its DSL field paths and source reference ids.
- Added `packages/document-renderer/fixtures/task-delegation.intent-contract.json` and `employment-agreement.intent-contract.json` renderer inputs.
- Added `docs/document-renderers.md` describing renderer responsibilities, legal disclaimers, and the must-not-invent-terms policy.
- Added Phase 8 test generation in the new `@office-dsl/testgen` package: typed `intent-contract.testgen-input.v1` inputs (`REQUIREMENT`, `INVARIANT`, `ACCEPTANCE_CRITERIA`, `PROHIBITED_BEHAVIOR`, `EXPECTED_OUTPUT`, `ERROR_HANDLING`, `SECURITY_POLICY`), `validateTestGenerationInput`, and deterministic `extractTestGenerationInput` from an Intent/Contract DSL snapshot.
- Added `generateUnitTestSpecs` and `generateTestSuite` producing unit, integration, API, E2E, security, and error-handling specifications that map back to DSL input items and paths.
- Added `verifyTestCoverage` producing a `testgen.coverage.v1` report and `testgen.verifier-input.v1` output that surface uncovered acceptance criteria, plus `renderTestPlanMarkdown` for a traceable Markdown test plan.
- Added `packages/testgen/fixtures/testgen-input.json` and `docs/test-generation.md`.
- Added Phase 9 JS/Node.js code generation in the new `@office-dsl/codegen` package with a bounded dependency-free Node ESM target and fixed generated outputs.
- Added deterministic approved-DSL implementation planning, JS artifact generation, generated Node.js test execution, file-hash verification, and `codegen.verifier-input.v1` output.
- Added `docs/code-generation.md` describing the approval gate, target boundary, artifacts, generated tests, and verifier input.
- Added Phase 10 semantic verifier input/report models, deterministic Python checks for original NL/source quotes, approved DSL gaps/conflicts/assumptions, rendered document mismatches, codegen test failures, and testgen uncovered acceptance criteria.
- Added TypeScript `runPythonSemanticVerifier` bridge and `Runtime.createWithPythonSemanticVerifier` gating to capture Python verifier reports in audit and block failed/review-needed sessions at `VERIFICATION_FAILED`.
- Added `docs/semantic-verifier.md` documenting the mock-safe semantic verifier boundary and OpenRouter/LiteLLM limitation.

### Changed

- Updated root package, llm-planner package, `VERSION`, docs, and documentation consistency tests to `0.9.0`.
- Marked Phase 5 TODO items complete for the deterministic mock-safe planner, renderer, and round-trip validation boundary; production OpenRouter execution remains outside the validated default.
- Marked Phase 6 TODO items complete for the document renderers and traceability map; wiring renderers into runtime/CLI/backend/UI remains open.
- Marked Phase 8 TODO items complete for the test-generation inputs, spec generation, and coverage verification; runtime/verifier integration remains open.
- Marked Phase 9 TODO items complete for the package-level JS/Node.js code-generation boundary; runtime/CLI/backend/UI/Python-verifier integration remains open.
- Updated root package, codegen package, `VERSION`, docs, and documentation consistency tests to `0.10.0`.
- Marked mock-safe Phase 10 TODO items complete for NL-vs-DSL checks, rendered-document checks, code/test verifier-input checks, and TypeScript runtime integration; live OpenRouter/LiteLLM validation remains open.
- Updated root package, dsl-runtime package, verifier package, `VERSION`, docs, and documentation consistency tests to `0.11.0`.

### Tests

- Added `tests/nl-dsl-roundtrip.test.ts` coverage for malformed planner-response rejection, valid schema-to-DSL conversion, varied single-message NL planning, guideline-file planning, traceable DSL-to-NL rendering, and round-trip checks that prevent unauthorized new field paths.
- Added `tests/document-renderer.test.ts` coverage for the draft disclaimer, task delegation, service agreement, employment/guideline renderers, explicit gap and assumption handling, the document-to-DSL traceability map, and renderer dispatch.
- Added `tests/testgen.test.ts` coverage for input validation, deterministic DSL extraction, unit spec mapping to acceptance criteria, integration/API/E2E/security/error-handling generation, and coverage verification that surfaces uncovered acceptance criteria.
- Added `tests/codegen.test.ts` coverage for allowed targets, approval gating, deterministic implementation plans, generated JS artifacts, generated Node.js test execution, source safety checks, file hashes, and verifier input test results.
- Added Python verifier tests for semantic PASS/FAIL/NEEDS_REVIEW behavior and OpenRouter configuration guarding, plus `tests/semantic-verifier.test.ts` for TypeScript-to-Python invocation and runtime gating.

## [0.8.0] - 2026-07-27

### Added

- Added `script/readme.sh`, root `Makefile` documentation targets, generated README include menu, per-example README files, and CI documentation freshness checks.
- Added Phase 4B deterministic recruitment example runner with `example-recruitment:run`, `examples-recruitment:run`, `project.sh example-recruitment`, and `project.sh examples-recruitment` commands.
- Added `examples-recruitment/01-multi-candidate`, covering one accepted and one rejected candidate with `oferta.md`, `cv.md`, `cv.pdf`, OCR mock fallback, per-candidate `chat.txt`, expected summaries, and ignored generated/final artifacts.
- Added document ingestion for recruitment offers and CVs with source documents, line-level source references, deterministic text-PDF extraction, and mock OCR routing through `cv.ocr.txt`.
- Added per-candidate proposal generation, partial Intent/Contract DSL normalization, chat-runner negotiation reuse, and final `out/contract.dsl.txt` creation only after bilateral approval of the current chat contract hash.
- Added `ROADMAP.md` describing current capabilities, target CQRS+ES architecture, REST API surface, CLI shell design, and release milestones.
- Added `packages/cli/src/shell.ts` as an interactive REPL and one-shot command shell for the runtime, exposing `create`, `get`, `list`, `answer`, `confirm`, `approve`, `reject`, `cancel`, `execute`, and `audit` commands.
- Added `cli:shell` script to `package.json`.
- Extended `apps/backend/src/server.ts` with CQRS+ES-style endpoints:
  - `POST /api/tasks/{id}/approve` for Human1/Human2 canonical DSL hash approval.
  - `POST /api/tasks/{id}/dsl` for replacing the canonical Intent/Contract DSL snapshot.
  - `GET /api/tasks/{id}/events` for state-transition event stream projection.
  - `GET /api/tasks/{id}/approvals` for canonical approval records.
  - `GET /api/tasks/{id}/questions` for unresolved questions with optional `?party` filter.
- Wired `diagnoseIntentContractDsl` and `questionsForParty` into the backend query endpoints.

### Changed

- Included recruitment examples in root `verify` and documented Phase 4B as implemented for deterministic mock-safe fixtures; production OCR providers remain outside the validated default.
- Updated root package, example-runner package, `VERSION`, docs, and documentation consistency tests to `0.8.0`.
- Updated `TODO.md` to uncheck several Phase 0, Phase 1, Phase 4A, and Phase 14 items that lack sufficient test coverage, with inline `Test gap:` notes explaining the missing validation.
- Updated `apps/backend/src/server.ts` `openapi.json` to document the new CQRS+ES endpoints.

### Tests

- Added `tests/recruitment-runner.test.ts` coverage for recruitment discovery, Markdown/PDF/OCR ingestion, source references, accepted-candidate finalization, rejected-candidate non-finalization, and expected summary comparison.

## [0.7.7] - 2026-07-27

### Added

- Added `script/readme.sh`, root `Makefile` documentation targets, generated README include menu, per-example README files, and CI documentation freshness checks.
- Added rejected-approval diagnosis in `@office-dsl/intent-contract-model`: Human2 rejections can now block finalization and reopen a clarification question routed back to Human1.
- Extended `ApprovalNode` with optional `field`, `reason`, and `source` metadata so rejection context can identify the insufficient field and explanation.

### Changed

- Marked the Phase 4 "Support reopening clarification after Human2 rejects insufficient detail" TODO item as complete at the model diagnosis layer; live runtime/CLI/backend/UI surfacing remains tracked separately.
- Updated root package, intent-contract model package, `VERSION`, and documentation consistency tests to `0.7.7`.

### Tests

- Extended `tests/intent-contract-diagnosis.test.ts` with Human2 rejection reopening coverage and a non-reopening approved-control case.

## [0.7.6] - 2026-07-27

### Added

- Added `script/readme.sh`, root `Makefile` documentation targets, generated README include menu, per-example README files, and CI documentation freshness checks.
- Added `mockPlanConversationHistory` in `@office-dsl/llm-planner` to convert `intent-contract.conversation.v1` Human1/Human2 fixtures into valid partial `intent-contract.dsl.v1` snapshots with source references, deterministic payment/deadline hints, unresolved fields, and blocking questions.

### Changed

- Marked the Phase 4 "Add planner support for conversation history" TODO item as complete for the deterministic mock/fixture planner path; production OpenRouter, CLI, backend, and UI conversation ingestion remain tracked separately.
- Updated root package, llm-planner package, `VERSION`, and documentation consistency tests to `0.7.6`.

### Tests

- Added `tests/llm-planner-conversation.test.ts` coverage for conversation-history planning, source preservation, extracted payment/deadline fields, unresolved questions, and non-ready finalization diagnosis.

## [0.7.5] - 2026-07-27

### Added

- Added `script/readme.sh`, root `Makefile` documentation targets, generated README include menu, per-example README files, and CI documentation freshness checks.
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

- Added `script/readme.sh`, root `Makefile` documentation targets, generated README include menu, per-example README files, and CI documentation freshness checks.
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

- Added `script/readme.sh`, root `Makefile` documentation targets, generated README include menu, per-example README files, and CI documentation freshness checks.
- Implemented the Phase 3 missing/ambiguous/conflicting information model in `@office-dsl/intent-contract-model`:
  - Added `diagnoseIntentContractDsl` and `collectFormalFields`, producing completeness gaps, ambiguity reports, conflict reports, unapproved-assumption reports, traceability gaps, deterministic generated questions, and a `finalizationReady` gate with `blockingReasons`.
  - Added optional model fields for Phase 3: `SourceReference.span`, `FormalField.interpretations`, and `ConflictNode.values`/`ConflictValue` for competing Human1/Human2 values with source references.
- Added `Phase 4B - Document Ingestion, OCR, And Recruitment Workflow` to `TODO.md`, describing the target multi-candidate recruitment flow (one job offer negotiated against many CVs), document ingestion for `oferta.md`/`cv.md`/`cv.pdf`, PDF text extraction and OCR fallback behind mock-safe interfaces, per-candidate proposal generation, CHAT/EMAIL negotiation reuse, acceptance/rejection finalization, and the `[numer-rekrutacji--stanowisko]/[numer-osoby]/{in/Ă˘â‚¬Â¦,out/contract.dsl.txt,chat.txt}` folder convention.
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

- Added `script/readme.sh`, root `Makefile` documentation targets, generated README include menu, per-example README files, and CI documentation freshness checks.
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

- Added `script/readme.sh`, root `Makefile` documentation targets, generated README include menu, per-example README files, and CI documentation freshness checks.
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

- Added `script/readme.sh`, root `Makefile` documentation targets, generated README include menu, per-example README files, and CI documentation freshness checks.
- Added `.github/workflows/verify.yml` to run the repository verification workflow on `ubuntu-latest` and `windows-latest`.
- Added `docs/codex-sandbox-vitest.md` documenting the Codex Windows sandbox `spawn EPERM` failure mode for Vitest/Vite startup and the required escalated verification path in this environment.

### Changed

- Updated root Vitest scripts to run against `tests` and exclude generated/cache paths such as `.pytest_cache` and `verifier/`.
- Updated package, app, verifier, and OpenAPI version metadata to `0.5.0`.

### Known limitations

- The current Codex Windows sandbox still blocks Node/Vite process creation used by Vitest internals, so full verification in this environment requires escalated execution.

## [0.4.0] - 2026-07-24

### Added

- Added `script/readme.sh`, root `Makefile` documentation targets, generated README include menu, per-example README files, and CI documentation freshness checks.
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

- Added `script/readme.sh`, root `Makefile` documentation targets, generated README include menu, per-example README files, and CI documentation freshness checks.
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

- Added `script/readme.sh`, root `Makefile` documentation targets, generated README include menu, per-example README files, and CI documentation freshness checks.
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

- Added `script/readme.sh`, root `Makefile` documentation targets, generated README include menu, per-example README files, and CI documentation freshness checks.
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
