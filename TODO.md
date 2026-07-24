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
- Clarification exists as workflow steps, not as a general missing/ambiguous/conflicting field model.
- Rendering exists as readable Office DSL text, not formal documents.
- Office runtime confirmations still use execution plan hashes; the runtime now also stores a canonical Intent/Contract snapshot hash and minimal Human1/Human2 approval records, but this is not yet exposed through CLI/backend/UI flows.

MOCK:

- Planner semantic understanding.
- Python verifier semantic judgment.
- External connectors and email delivery.
- Web UI as a production surface.

NOT IMPLEMENTED:

- runtime field traceability population, legal renderers, code generation, DSL-based test generation, CLI/backend/UI exposure for canonical approvals, and runtime-to-Python verifier integration.

---

## Phase 0 - Repository Audit And Documentation Alignment

- [x] Audit `README.md`, `TODO.md`, `CHANGELOG.md`, `VERSION.md`, `CONTRIBUTING.md`, `POLICY.md`, `HANDOFF.md`, `docs/`, `research/`, `examples/`, `packages/`, `apps/`, `verifier/`, `tests/`, and `mock-data/`.
  - Done when the documented status is based on actual files and tests, not README claims.
- [x] Create `docs/system-purpose-and-runtime-flow.md`.
  - Done when it describes purpose, H2M/H2H, runtime flow, LLM, verifier, traceability, approvals, documents, code, tests, examples, and current-vs-target state with Mermaid diagrams.
- [x] Update README to separate current implementation from target architecture.
  - Done when Office DSL MVP is no longer presented as the full system.
- [x] Rebuild TODO into staged phases with concrete outcomes and completion criteria.
  - Done when checked items match code evidence.
- [x] Update HANDOFF, CHANGELOG, and VERSION metadata for the documentation alignment pass.
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
- [x] Add a root `verify` script that runs typecheck, lint, format check, TypeScript tests, Python tests, and `git diff --check`.
  - Done when `corepack pnpm run verify` works on Windows and Linux.
- [x] Fix or document any dependency/link issue that prevents default Vitest startup in the Codex sandbox.
  - Done when the exact environment failure is reproducible or removed. Documented in `docs/codex-sandbox-vitest.md`; root test scripts avoid `.pytest_cache` scanning, but this Codex Windows sandbox still blocks Vite/Vitest process creation with `spawn EPERM`.

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

- [ ] Implement completeness validation for required fields.
  - Done when missing deadline/payment/acceptance criteria can be represented and reported without guessing.
- [ ] Implement ambiguity detection hooks.
  - Done when a field can be marked `AMBIGUOUS` with competing interpretations and a generated question.
- [ ] Implement conflict representation.
  - Done when contradictory values from Human1 and Human2 can coexist with source references and block finalization.
- [ ] Implement assumption tracking.
  - Done when LLM-added values are marked `ASSUMED` and require explicit approval.
- [ ] Add source traceability for material fields.
  - Done when each relevant field can point to message ID, speaker, file path, or source span.

---

## Phase 4 - Human1/Human2 Conversation Workflow

- [ ] Define conversation input format for Human1 and Human2.
  - Done when examples can store speaker, message ID, timestamp, and text.
- [ ] Add planner support for conversation history.
  - Done when a two-party fixture produces partial DSL with sources and unresolved fields.
- [ ] Add runtime routing of questions to Human1 or Human2.
  - Done when the runtime knows which party must answer a missing or conflicting field.
- [x] Add bilateral approval records.
  - Done when Human1 and Human2 approvals include party, hash, timestamp, and verdict.
- [x] Invalidate approvals after DSL changes.
  - Done when tests prove both sides must reapprove after any material DSL edit.
- [ ] Support reopening clarification after Human2 rejects insufficient detail.
  - Done when Human2 can block finalization and trigger a question back to Human1.

---

## Phase 4A - Testable Human1/Human2 Negotiation Examples

- [x] Store executable Human1/Human2 chat examples with `scenario.json` and `chat.txt`.
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
  - Done when `final-contract.dsl.hcl`, `contract.pdf`, and `approvals.json` are written only after active Human1 and Human2 approvals reference the current merged hash with no missing fields or conflicts.
- [x] Invalidate approvals after any merged contract change.
  - Done when a one-side approval becomes `INVALIDATED` if a later utterance changes the merged contract hash.
- [x] Support ending a conversation without agreement.
  - Done when cancellation scenarios end as `CANCELLED` and do not produce `final-contract.dsl.hcl`, `contract.pdf`, or `approvals.json`.
- [x] Generate final DSL, PDF, approvals, diff summary, and annex only after bilateral approval.
  - Done when agreed scenarios create final artifacts under `examples-chat/<scenario>/generated/final/` only at the event where the second party approves the same current hash.
- [x] Add commands for chat examples and include them in verification.
  - Done when `example-chat:run`, `examples-chat:run`, `project.sh example-chat`, `project.sh examples-chat`, and the root `verify` flow execute the chat examples.
- [x] Compare generated artifacts with expected outcomes and cover the flow with tests.
  - Done when the runner compares generated `summary.json` with `out/expected.summary.json`, and tests cover parsing, discovery, merging, conflict detection, approval invalidation, finalization, cancellation, and all four scenario outcomes.

---

## Phase 5 - Bidirectional NL <-> DSL

- [ ] Define controlled NL-to-DSL planner prompts and response schemas for OpenRouter.
  - Done when schema validation rejects malformed LLM output.
- [ ] Add single-message planner mode beyond current mock patterns.
  - Done when fixtures cover varied natural language without hard-coded action matching.
- [ ] Add guideline-file planner mode.
  - Done when text guidelines can produce DSL with missing fields and source references.
- [ ] Add DSL-to-NL summary renderer.
  - Done when every rendered statement maps back to a DSL field.
- [ ] Add round-trip regression tests.
  - Done when DSL rendered to NL and reprocessed does not introduce unauthorized meaning for selected fixtures.

---

## Phase 6 - Contract And Legal Document Renderers

- [ ] Define renderer responsibilities and legal disclaimers.
  - Done when docs state that generated documents are drafts and must not invent terms.
- [ ] Implement task delegation renderer.
  - Done when output includes assignee, deliverable, deadline, dependencies, exclusions, and acceptance criteria from DSL only.
- [ ] Implement service agreement renderer.
  - Done when payment, parties, scope, acceptance, and exclusions render from approved DSL.
- [ ] Implement employment agreement/guideline renderer as draft output.
  - Done when legal-guideline fixtures render without unsupported fields.
- [ ] Add document-to-DSL traceability map.
  - Done when each paragraph references DSL paths or source references.

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

- [x] Add CI for Windows and Linux.
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
