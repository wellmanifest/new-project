# TODO

This roadmap is intentionally split between the current offline Office DSL MVP and the target Intent/Contract DSL Runtime. A checked item means the behavior exists in code or documentation and has at least relevant validation for the current scope. Target features must not be described as done until implemented and tested.

## Current Baseline

DONE:

- Offline `office.dsl.v1` model, parser, structural validator, and human-readable token renderer.
- Mock planner for selected single-message office commands.
- TypeScript runtime with simple state machine, policy checks, `user.ask`, one-side confirmation, plan hashing, dry-run mock actions, file store, and audit records.
- CLI, backend API, static web demo, mock data, six runner-backed examples, Vitest tests, and Python verifier tests.

PARTIAL:

- OpenRouter and LiteLLM paths exist but are not the validated default path.
- A general missing/ambiguous/conflicting field model exists at the `intent-contract-model` layer (`diagnoseIntentContractDsl`), but runtime clarification still uses simple `user.ask` workflow steps; the diagnosis is not yet wired into the runtime/CLI/backend/UI.
- Rendering exists as readable Office DSL text, not formal documents.
- Office runtime confirmations still use execution plan hashes; the runtime now also stores a canonical Intent/Contract snapshot hash and minimal Human1/Human2 approval records, but this is not yet exposed through CLI/backend/UI flows.

MOCK:

- Planner semantic understanding.
- Python verifier semantic judgment.
- External connectors and email delivery.
- Web UI as a production surface.

NOT IMPLEMENTED:

- runtime field traceability population, code generation, DSL-based test generation, CLI/backend/UI exposure for canonical approvals, runtime-to-Python verifier integration, and production document ingestion/OCR providers beyond the deterministic mock-safe recruitment example runner. Contract/legal document renderers now exist at the `@office-dsl/document-renderer` layer (Phase 6); wiring them into the runtime/CLI/backend/UI remains open.

---

## Phase 0 - Repository Audit And Documentation Alignment

- [ ] Audit `README.md`, `TODO.md`, `CHANGELOG.md`, `VERSION.md`, `CONTRIBUTING.md`, `POLICY.md`, `HANDOFF.md`, `docs/`, `research/`, `examples/`, `packages/`, `apps/`, `verifier/`, `tests/`, and `mock-data/`. **Test gap:** `tests/docs.test.ts` only checks `README.md`, `VERSION`/`CHANGELOG.md`, `docs/system-purpose-and-runtime-flow.md`, and `docs/codex-sandbox-vitest.md`; it does not validate `TODO.md`, `CONTRIBUTING.md`, `POLICY.md`, `HANDOFF.md`, or the `research/`, `examples/`, `packages/`, `apps/`, `verifier/`, `tests/`, and `mock-data/` directories.
  - Done when the documented status is based on actual files and tests, not README claims.
- [x] Create `docs/system-purpose-and-runtime-flow.md`.
  - Done when it describes purpose, H2M/H2H, runtime flow, LLM, verifier, traceability, approvals, documents, code, tests, examples, and current-vs-target state with Mermaid diagrams.
- [x] Update README to separate current implementation from target architecture.
  - Done when Office DSL MVP is no longer presented as the full system.
- [ ] Rebuild TODO into staged phases with concrete outcomes and completion criteria. **Test gap:** no test validates the `TODO.md` phase structure, completion criteria, or that checked items match code evidence.
  - Done when checked items match code evidence.
- [ ] Update HANDOFF, CHANGELOG, and VERSION metadata for the documentation alignment pass. **Test gap:** `tests/docs.test.ts` validates `VERSION`/`CHANGELOG.md` consistency but does not check `HANDOFF.md` contents or that mocks are not presented as production behavior.
  - Done when the next agent has a clear start point and no mock is presented as production behavior.

---

## Phase 1 - Stabilize Current Office DSL MVP

- [x] Keep `office.dsl.v1` structurally valid for current examples.
  - Done when `parseTaskDsl` and `validateTaskDsl` pass existing DSL fixtures.
- [x] Keep supported mock actions explicit.
  - Done when unsupported actions fail validation or policy checks.
- [x] Keep email send guarded by confirmation.
  - Done when `email.send` without confirmation is rejected by DSL validation and runtime tests.
- [x] Keep unsafe shell/dynamic-code/path traversal requests blocked.
  - Done when security tests cover these cases.
- [x] Keep dry-run execution as default.
  - Done when tests show mock sending does not perform real external delivery.
- [ ] Add a root `verify` script that runs typecheck, lint, format check, TypeScript tests, Python tests, and `git diff --check`. **Test gap:** `packages/example-runner/src/verify.ts` exists and `pnpm run verify` is wired, but no test in `tests/` exercises the verify pipeline or asserts that it runs on Windows and Linux.
  - Done when `corepack pnpm run verify` works on Windows and Linux.
- [x] Fix or document any dependency/link issue that prevents default Vitest startup in the Codex sandbox.
  - Done when the exact environment failure is reproducible or removed. Documented in `docs/codex-sandbox-vitest.md`; root test scripts avoid `.pytest_cache` scanning, but this Codex Windows sandbox still blocks Vite/Vitest process creation with `spawn EPERM`.
- [x] Reorganize `.office-dsl/` into per-client folders for runtime state.
  - Done when runtime task sessions and audit records are stored under `.office-dsl/<createdBy>/tasks/` and `.office-dsl/<createdBy>/audit/` and no flat `tasks/` + `audit/` dump remains.
- [x] Keep generated `examples` and `examples-chat` outputs beside their scenarios.
  - Done when `examples/<scenario>/generated/` and flat `examples-chat/<scenario>/generated/` files hold all runner output and `.office-dsl/` only stores runtime state.
- [x] Remove JSON from generated runner artifacts.
  - Done when generated runner artifacts use `*.dsl.hcl` project DSL/HCL files or human-readable Markdown/PDF files, without JSON output artifacts.
- [x] Update Python verifier to consume DSL/markdown inputs instead of JSON.
  - Done when `verifier-input.dsl.hcl` and `verifier-input.plan.dsl.hcl` are parsed directly and mock verifier results match the previous JSON-based behavior.

---

## Phase 2 - Canonical Intent/Contract DSL

- [x] Define the canonical DSL package boundary separate from `office.dsl.v1`.
  - Done when the repo has a documented versioned model such as `intent.dsl.v1` or `contract.dsl.v1` and existing Office DSL compatibility is preserved.
- [x] Add core constructs: `DOCUMENT`, `CONTRACT`, `PARTY`, `ROLE`, `INTENT`, `SUBJECT`, `OBLIGATION`, `DELIVERABLE`, `DEADLINE`, `PAYMENT`, `CONDITION`, `DEPENDENCY`, `ACCEPTANCE_CRITERIA`, `EXCLUSION`, `ASSUMPTION`, `RISK`, `CONFLICT`, `QUESTION`, `APPROVAL`, `SOURCE_REFERENCE`, `RENDER`, and `EXECUTION`.
  - Done when each construct has TypeScript types, validation rules, and at least one fixture.
- [x] Add field status semantics: `CONFIRMED`, `MISSING`, `INCOMPLETE`, `AMBIGUOUS`, `CONFLICTING`, `ASSUMED`, `REJECTED`, and `NOT_APPLICABLE`.
  - Done when fields can carry status, source, required-for-completion flag, and approvals.
- [x] Define canonical JSON serialization and stable hashing rules.
  - Done when equivalent DSL snapshots hash identically across Windows and Linux.
- [x] Add migration or adapter notes from `office.dsl.v1` to the canonical model.
  - Done when current examples still validate and have a documented compatibility path through `officeDslToIntentContractDsl`.

---

## Phase 3 - Missing, Ambiguous, And Conflicting Information Model

- [x] Implement completeness validation for required fields.
  - Done when missing deadline/payment/acceptance criteria can be represented and reported without guessing. `diagnoseIntentContractDsl` reports required `MISSING`/`INCOMPLETE` fields as completeness gaps and emits a question that asks for the value without inventing one.
- [x] Implement ambiguity detection hooks.
  - Done when a field can be marked `AMBIGUOUS` with competing interpretations and a generated question. `FormalField.interpretations` carries competing interpretations and the diagnosis emits an `AMBIGUOUS` question listing them.
- [x] Implement conflict representation.
  - Done when contradictory values from Human1 and Human2 can coexist with source references and block finalization. `ConflictNode.values`/`ConflictValue` hold competing party values with source references, and the diagnosis lists them and clears `finalizationReady`.
- [x] Implement assumption tracking.
  - Done when LLM-added values are marked `ASSUMED` and require explicit approval. Unapproved `ASSUMED` value-carrying fields (empty `approvedBy`) block finalization until approved.
- [x] Add source traceability for material fields.
  - Done when each relevant field can point to message ID, speaker, file path, or source span. `SourceReference` carries `id`, `speaker`, `path`, `quote`, and `span`, and the diagnosis flags any material valued field without a source as a traceability gap.

Note: Phase 3 is implemented at the `@office-dsl/intent-contract-model` layer via `diagnoseIntentContractDsl`. Wiring the diagnosis and `finalizationReady` gate into the runtime, CLI, backend, and UI is tracked in Phases 4, 11, and 12.

---

## Phase 4 - Human1/Human2 Conversation Workflow

- [x] Define conversation input format for Human1 and Human2.
  - Done when examples can store speaker, message ID, timestamp, and text. `Conversation`/`ConversationMessage` now define `intent-contract.conversation.v1` with `Human1`, `Human2`, and `system` speakers; `validateConversation`/`parseConversation` enforce version, unique message IDs, ISO timestamps, and non-empty text; `conversationToSourceReferences` maps each line to traceable message sources.
- [x] Add planner support for conversation history.
  - Done when a two-party fixture produces partial DSL with sources and unresolved fields. `mockPlanConversationHistory` converts `intent-contract.conversation.v1` fixtures into valid partial `intent-contract.dsl.v1`, preserves every line as a source reference, extracts deterministic payment/deadline hints, and leaves unresolved legal/approval fields as blocking questions.
- [x] Add runtime routing of questions to Human1 or Human2.
  - Done when the runtime knows which party must answer a missing or conflicting field. `diagnoseIntentContractDsl` now tags each generated question with `targetParties` (derived from `source.speaker`, `ConflictValue.partyId`, and `parties`), and `questionsForParty` filters questions per party. Surfacing this through the live runtime/CLI/UI is tracked in Phases 11 and 12.
- [x] Add bilateral approval records.
  - Done when Human1 and Human2 approvals include party, hash, timestamp, and verdict.
- [x] Invalidate approvals after DSL changes.
  - Done when tests prove both sides must reapprove after any material DSL edit.
- [x] Support reopening clarification after Human2 rejects insufficient detail.
  - Done when Human2 can block finalization and trigger a question back to Human1. `diagnoseIntentContractDsl` now reports `REJECTED` approval records, blocks finalization, and generates a reopened clarification question routed to Human1 when Human2 rejects a field as insufficient.

---

## Phase 4A - Testable Human1/Human2 Negotiation Examples

- [x] Store executable Human1/Human2 chat examples with `scenario.json` and `chat.txt`. `examples-recruitment` discovery processes candidate folders with local `in/`, `out/`, `chat.txt`, and scenario-local generated artifacts.
  - Done when `examples-chat/01-short-agreement`, `02-long-negotiation-agreement`, `03-short-conversation-cancelled`, and `04-long-negotiation-cancelled` are runnable by the example runner and declare expected summaries.
- [x] Process each conversation line by line.
  - Done when every non-empty `@user1`/`@user2` line becomes a numbered event with generated per-event artifacts.
- [x] Maintain separate contract state for each side plus a merged contract.
  - Done when generated artifacts include the speaking party contract and the current merged contract after every utterance.
- [x] Merge the two party contracts deterministically.
  - Done when compatible values are accepted into one merged field, conflicting values are preserved with source references, missing required fields remain explicit, and the merged hash is stable.
- [x] Generate a readable diff after every utterance.
  - Done when each event writes `diff.md` showing added fields, changed positions, invalidated approvals, conflicts, approvals, or no material change.
- [x] Render generated DSL artifacts as HCL-highlighted editable project DSL, not JSON.
  - Done when `*.dsl.hcl` artifacts use project-specific `document`/`field`/`conflict`/`change` blocks, reject JSON object syntax, are validated before writing, and open with syntax coloring based on the `.hcl` extension.
- [x] Detect conflicts and changes of position.
  - Done when tests prove competing party values block finalization and a party's changed field is recorded as a changed position.
- [x] Accept only the same current merged contract version from both parties.
  - Done when `final-contract.dsl.hcl`, `contract.pdf`, and `approvals.dsl.hcl` are written only after active Human1 and Human2 approvals reference the current merged hash with no missing fields or conflicts.
- [x] Invalidate approvals after any merged contract change.
  - Done when a one-side approval becomes `INVALIDATED` if a later utterance changes the merged contract hash.
- [x] Support ending a conversation without agreement.
  - Done when cancellation scenarios end as `CANCELLED` and do not produce `final-contract.dsl.hcl`, `contract.pdf`, or `approvals.dsl.hcl`.
- [ ] Generate final DSL, PDF, approvals, diff summary, and annex only after bilateral approval. **Test gap:** `tests/chat-runner.test.ts` asserts `final-contract.dsl.hcl`, `contract.pdf`, `approvals.dsl.hcl`, and `annex.dsl.hcl`, but it does not check `final/diff-summary.md` or `final/contract.md` content/existence.
  - Done when agreed scenarios create final artifacts under `examples-chat/<scenario>/generated/final/` only at the event where the second party approves the same current hash.
- [x] Add commands for chat examples and include them in verification.
  - Done when `example-chat:run`, `examples-chat:run`, `project.sh example-chat`, `project.sh examples-chat`, and the root `verify` flow execute the chat examples.
- [x] Compare generated artifacts with expected outcomes and cover the flow with tests.
  - Done when the runner compares the generated summary model with `out/expected.summary.json`, writes `summary.dsl.hcl`, and tests cover parsing, discovery, merging, conflict detection, approval invalidation, finalization, cancellation, and all four scenario outcomes.

---

## Phase 4B - Document Ingestion, OCR, And Recruitment Workflow

Goal: support a multi-candidate recruitment flow where one job offer is negotiated against many CVs. Each candidate lives in an isolated folder, receives an individual proposal derived from the shared offer, negotiates through CHAT/EMAIL, and ends in acceptance or rejection. This phase depends on the Phase 4/4A Human1/Human2 negotiation, merge, conflict, and approval model and the Phase 6 renderers.

Target folder convention (one recruitment, many candidates):

```text
[numer-rekrutacji--stanowisko]/
  [numer-osoby]/
    in/
      oferta.md        # shared job offer (Markdown), copied or referenced per candidate
      cv.pdf           # candidate CV as PDF (text-based or scanned)
      cv.md            # candidate CV as Markdown (extracted or provided)
    out/
      contract.dsl.txt # final per-candidate contract, only after bilateral approval
    chat.txt           # per-candidate negotiation transcript
```

- [x] Define a document ingestion interface for offers and CVs.
  - Done when Markdown offers (`oferta.md`) and CV inputs in Markdown (`cv.md`) and PDF (`cv.pdf`) load into the runtime as source documents with source references, without inventing content. `loadRecruitmentSources` returns source documents with line-level `SourceReference` entries for offer, Markdown CV, text PDF CV, and OCR-fallback CV inputs.
- [x] Add PDF text extraction for text-based CVs.
  - Done when a text-based `cv.pdf` is parsed to plain text through a deterministic mock-safe PDF text extractor with a fixture path. `extractPdfText` handles deterministic fixture text markers and PDF text operators without network or external side effects.
- [x] Add OCR fallback for scanned or image-only CVs.
  - Done when an image-only CV can be routed to an OCR provider (external API or a local library such as Tesseract) behind a mock-safe interface, and mock mode remains the validated default. Scanned fixture PDFs route to deterministic `cv.ocr.txt` mock OCR text; production OCR providers remain outside the validated default.
- [x] Normalize extracted offer/CV content into Intent/Contract DSL source.
  - Done when extracted text maps into canonical source documents with field statuses and source spans, never fabricating terms that are absent from the offer or CV. The recruitment runner creates a partial `intent-contract.dsl.v1` with sourced role, candidate, salary, start date, skills, missing governing law, and source spans.
- [x] Implement the recruitment folder convention in the example runner.
  - Done when the runner discovers and processes `[numer-rekrutacji--stanowisko]/[numer-osoby]/` folders and reads/writes `in/oferta.md`, `in/cv.pdf`, `in/cv.md`, `out/contract.dsl.txt`, and `chat.txt`. `examples-recruitment` discovery processes candidate folders with local `in/`, `out/`, `chat.txt`, and scenario-local generated artifacts.
- [x] Generate a per-candidate proposal from the shared offer.
  - Done when each candidate folder derives an individual proposal (different terms allowed per candidate) from one `oferta.md` plus that candidate's CV, with no cross-contamination between candidates. Each candidate writes an ignored `out/proposal.dsl.txt` with a deterministic proposal hash derived only from that candidate's sources.
- [x] Run per-candidate CHAT/EMAIL negotiation.
  - Done when each candidate negotiates through the chat/email workflow reusing the Human1/Human2 merge, conflict, position-change, and approval model, writing the transcript to `chat.txt`. Recruitment candidates run through `runChatScenario`, preserving bilateral current-hash approval and cancellation semantics.
- [x] Finalize acceptance or rejection per candidate.
  - Done when an accepted candidate writes `out/contract.dsl.txt` only after bilateral approval of the same current contract hash, and a rejected or withdrawn candidate ends without a final contract. Accepted fixtures create ignored `out/contract.dsl.txt`; rejected/cancelled candidates do not.
- [x] Add a recruitment example and regression tests.
  - Done when a fixture recruitment with one offer and multiple candidate folders runs end to end, covers at least one acceptance and one rejection, and is compared deterministically like the other example runners. `examples-recruitment/01-multi-candidate` and `tests/recruitment-runner.test.ts` cover Markdown/PDF/OCR ingestion, proposal generation, accepted finalization, rejected non-finalization, and expected summary comparison.

---

## Phase 5 - Bidirectional NL <-> DSL

- [x] Define controlled NL-to-DSL planner prompts and response schemas for OpenRouter.
  - Done when schema validation rejects malformed LLM output. `CONTROLLED_PLANNER_SCHEMA`, `buildOpenRouterIntentContractPrompt`, `validateControlledPlannerResponse`, and `parseControlledPlannerResponse` define the mock-safe OpenRouter boundary; `tests/nl-dsl-roundtrip.test.ts` rejects malformed structured output, invalid payment shapes, unknown sources, and unsupported paths before DSL creation.
- [x] Add single-message planner mode beyond current mock patterns.
  - Done when fixtures cover varied natural language without hard-coded action matching. `mockPlanIntentContractFromNaturalLanguage` converts varied single-message service/task-style NL into canonical `intent-contract.dsl.v1` fields with source references, missing governing law, payment, deadline, deliverable, acceptance, and exclusions covered by regression tests.
- [x] Add guideline-file planner mode.
  - Done when text guidelines can produce DSL with missing fields and source references. `mockPlanGuidelineFileToIntentContractDsl` accepts guideline text plus source path, emits file-backed source references, preserves missing required fields, and is covered by `tests/nl-dsl-roundtrip.test.ts`.
- [x] Add DSL-to-NL summary renderer.
  - Done when every rendered statement maps back to a DSL field. `renderIntentContractDslToNaturalLanguage` emits `intent-contract.nl-summary.v1` statements with `dslPath`, field name, source id, and rendered text; tests assert every statement is traceable.
- [x] Add round-trip regression tests.
  - Done when DSL rendered to NL and reprocessed does not introduce unauthorized meaning for selected fixtures. `extractRenderedStatementPaths` and the round-trip regression assert the rendered NL contains exactly the valued DSL field paths and does not fabricate absent governing-law terms.

---

## Phase 6 - Contract And Legal Document Renderers

- [x] Define renderer responsibilities and legal disclaimers.
  - Done when docs state that generated documents are drafts and must not invent terms. `docs/document-renderers.md` documents the responsibilities and the `DRAFT_DISCLAIMER`, and `@office-dsl/document-renderer` embeds the draft/must-not-invent disclaimer in every rendered document.
- [x] Implement task delegation renderer.
  - Done when output includes assignee, deliverable, deadline, dependencies, exclusions, and acceptance criteria from DSL only. `renderTaskDelegation` renders delegator/assignee, deliverables, deadlines, dependencies, exclusions, and acceptance criteria strictly from the DSL, emitting explicit gaps for missing fields.
- [x] Implement service agreement renderer.
  - Done when payment, parties, scope, acceptance, and exclusions render from approved DSL. `renderServiceAgreement` renders parties, scope (subjects/deliverables/obligations), payment with resolved payer/payee, acceptance criteria, exclusions, and governing law, and marks missing values as gaps.
- [x] Implement employment agreement/guideline renderer as draft output.
  - Done when legal-guideline fixtures render without unsupported fields. `renderEmploymentAgreement` renders employer/employee, duties, remuneration, term, conditions, guidelines, and exclusions from model fields only; `packages/document-renderer/fixtures/employment-agreement.intent-contract.json` renders without any unsupported field.
- [x] Add document-to-DSL traceability map.
  - Done when each paragraph references DSL paths or source references. Every rendered document returns a `traceability` array and appends a `Traceability Map` table mapping each item to `FormalField.field` DSL paths and `SourceReference.id` source ids.

---

## Phase 7 - Example Runner And Regression Fixtures

- [x] Define `scenario.json`.
  - Done when it declares input files, expected outputs, verifier mode, runtime mode, and optional answer scripts.
- [x] Convert or mirror examples into `in/` and `out/` structure.
  - Done when existing six examples can still run and target examples have room for richer artifacts.
- [x] Add runner for a single example.
  - Done when `corepack pnpm run example:run -- <name>` generates artifacts and returns non-zero on mismatch.
- [x] Add runner for all examples.
  - Done when `corepack pnpm run examples:run` is CI-friendly on Windows and Linux.
- [x] Add readable diffs for generated versus expected artifacts.
  - Done when JSON and Markdown differences are easy to inspect.
- [x] Run Python verifier from the example runner when configured.
  - Done when verifier output is saved and compared.

Target scenario set:

- [ ] `01-chat-to-dsl`
- [ ] `02-chat-history-to-service-agreement`
- [ ] `03-guidelines-to-employment-agreement`
- [ ] `04-task-delegation`
- [ ] `05-office-command`
- [ ] ambiguous chat with one-question-at-a-time policy
- [ ] conflicting contract terms
- [ ] both-party approval of the same hash
- [ ] approval invalidated after DSL change
- [ ] source traceability for every material field

---

## Phase 8 - Test Generation From DSL

- [ ] Define test-generation DSL inputs: `REQUIREMENT`, `INVARIANT`, `ACCEPTANCE_CRITERIA`, `PROHIBITED_BEHAVIOR`, `EXPECTED_OUTPUT`, `ERROR_HANDLING`, and `SECURITY_POLICY`.
  - Done when these inputs are typed and validated.
- [ ] Generate unit test specifications from DSL.
  - Done when generated tests map to acceptance criteria and can be verified.
- [ ] Generate integration/API/E2E/security test specifications from DSL where applicable.
  - Done when fixture coverage proves the mapping.
- [ ] Verify test coverage against DSL acceptance criteria.
  - Done when uncovered criteria appear in verifier output.

---

## Phase 9 - JS/Node.js Code Generation

- [ ] Define allowed code-generation targets.
  - Done when generated artifacts have a bounded runtime, dependency, and security model.
- [ ] Generate implementation plan from approved DSL.
  - Done when plan output is deterministic and auditable.
- [ ] Generate JS/Node.js code from DSL-approved requirements.
  - Done when generated code is never created directly from loose prompt text.
- [ ] Run generated tests against generated code.
  - Done when results are included in verifier input.

---

## Phase 10 - Python Semantic Verifier

- [x] Provide Python package with Pydantic report model and mock mode.
  - Done for current Office DSL scope.
- [x] Return machine-readable verdict and recommended action.
  - Done for current mock verifier fields.
- [ ] Validate original NL against approved DSL.
  - Done when missing requirements, contradictions, and unauthorized assumptions are detected beyond heuristics.
- [ ] Validate DSL against rendered document.
  - Done when document mismatches are reported with DSL paths.
- [ ] Validate DSL against generated code and tests.
  - Done when behavior mismatches and uncovered acceptance criteria are reported.
- [ ] Integrate TypeScript runtime with Python verifier execution.
  - Done when runtime can call verifier, capture output, and gate finalization.
- [ ] Validate OpenRouter/LiteLLM mode.
  - Done when documented setup and tests or manual validation prove the online path.

---

## Phase 11 - CLI For Windows And Linux

- [x] Provide current Office DSL CLI commands.
  - Done for `plan`, `run`, `validate`, `inspect`, `answer`, `confirm`, `reject`, `execute`, and `history`.
- [ ] Add canonical Intent/Contract CLI commands.
  - Done when CLI can process message, conversation, guideline file, approvals, render, verify, and example runner flows.
- [ ] Add Windows/Linux path compatibility tests.
  - Done when CI validates both OS targets.
- [ ] Add clear JSON and human-readable output modes for new workflows.
  - Done when automation and human review both have stable outputs.

---

## Phase 12 - Backend And Frontend Integration

- [x] Provide current backend API and static demo UI for the Office DSL MVP.
  - Done for single input, generated DSL, plan, answers, confirmation, execution, and audit display.
- [ ] Add conversation and guideline-file input surfaces.
  - Done when UI/API accepts structured conversation and files.
- [ ] Display field statuses, source references, gaps, assumptions, and conflicts.
  - Done when users can inspect why runtime is blocked.
- [ ] Add Human1/Human2 approval flows.
  - Done when both parties can approve the same hash or reopen clarification.
- [ ] Display rendered documents with traceability.
  - Done when document fragments link back to DSL paths.

---

## Phase 13 - Security, Audit, And Policy Enforcement

- [x] Block obvious unsafe office actions in deterministic policy checks.
  - Done for current tests.
- [x] Keep prompt-injection samples as data in mock log search.
  - Done for current security test.
- [ ] Define canonical security policy for LLM, runtime, renderer, codegen, and verifier.
  - Done when each component has explicit deny/allow boundaries.
- [ ] Add audit event schema for the full lifecycle.
  - Done when input, DSL snapshots, source refs, questions, answers, approvals, verifier output, render output, generated code/tests, and execution results are captured.
- [ ] Add secret handling and redaction policy.
  - Done when generated artifacts and logs are checked for secrets.
- [ ] Add authorization model for Human1/Human2 and backend/API usage.
  - Done when parties cannot approve or edit outside their role.

---

## Phase 14 - Production Hardening

- [ ] Add CI for Windows and Linux. **Test gap:** `.github/workflows/verify.yml` exists, but no test validates its presence, matrix configuration, or that default checks pass on `ubuntu-latest` and `windows-latest`.
  - Done when default checks pass on both systems. CI wiring is in `.github/workflows/verify.yml` and runs `bash project.sh install` plus `bash project.sh verify` on `ubuntu-latest` and `windows-latest`.
- [ ] Add packaging/release policy.
  - Done when version updates are unambiguous across package metadata, changelog, and docs.
- [ ] Add persistence strategy beyond local JSON files.
  - Done when audit and task state can survive production deployment requirements.
- [ ] Add observability and failure-mode documentation.
  - Done when operators know how to diagnose planner, runtime, verifier, renderer, and codegen failures.
- [ ] Add threat model and compliance review for contract/document workflows.
  - Done when legal/document generation risks are explicitly reviewed.

---

## Next 10 Implementation Tasks

1. Add runtime-to-Python verifier invocation behind a mock-safe interface.
2. Add the first target fixture: `01-chat-to-dsl` with `in/` and `out/` artifacts.
3. Add planner-backed scenario mode coverage for mock planner output normalization.
4. Add Markdown diff output for future rendered document artifacts.
5. Add runtime population of source references from planner or scenario inputs.
6. Add adapter output artifacts for current Office DSL examples.
7. Add canonical Intent/Contract CLI commands.
8. Define canonical security policy for LLM, runtime, renderer, codegen, and verifier.
9. Add CLI/backend exposure for Human1/Human2 canonical approval records.
10. Add renderer gating that requires bilateral canonical approval before document output.
