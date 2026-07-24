# TODO

This roadmap is intentionally split between the current offline Office DSL MVP and the target Intent/Contract DSL Runtime. A checked item means the behavior exists in code or documentation and has at least relevant validation for the current scope. Target features must not be described as done until implemented and tested.

## Current Baseline

DONE:

- Offline `office.dsl.v1` model, parser, structural validator, and human-readable token renderer.
- Mock planner for selected single-message office commands.
- TypeScript runtime with simple state machine, policy checks, `user.ask`, one-side confirmation, plan hashing, dry-run mock actions, file store, and audit records.
- CLI, backend API, static web demo, mock data, six static examples, Vitest tests, and Python verifier tests.

PARTIAL:

- OpenRouter and LiteLLM paths exist but are not the validated default path.
- Clarification exists as workflow steps, not as a general missing/ambiguous/conflicting field model.
- Rendering exists as readable DSL text, not formal documents.
- Hashing is based on execution plan content, not canonical Intent/Contract DSL snapshots.

MOCK:

- Planner semantic understanding.
- Python verifier semantic judgment.
- External connectors and email delivery.
- Web UI as a production surface.

NOT IMPLEMENTED:

- Canonical Intent/Contract DSL, Human2 approval, field traceability, legal renderers, example runner, code generation, DSL-based test generation, and runtime-to-Python verifier integration.

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
- [ ] Add a root `verify` script that runs typecheck, lint, format check, TypeScript tests, Python tests, and `git diff --check`.
  - Done when `corepack pnpm run verify` works on Windows and Linux.
- [ ] Fix or document any dependency/link issue that prevents default Vitest startup in the Codex sandbox.
  - Done when the exact environment failure is reproducible or removed.

---

## Phase 2 - Canonical Intent/Contract DSL

- [ ] Define the canonical DSL package boundary separate from `office.dsl.v1`.
  - Done when the repo has a documented versioned model such as `intent.dsl.v1` or `contract.dsl.v1` and existing Office DSL compatibility is preserved.
- [ ] Add core constructs: `DOCUMENT`, `CONTRACT`, `PARTY`, `ROLE`, `INTENT`, `SUBJECT`, `OBLIGATION`, `DELIVERABLE`, `DEADLINE`, `PAYMENT`, `CONDITION`, `DEPENDENCY`, `ACCEPTANCE_CRITERIA`, `EXCLUSION`, `ASSUMPTION`, `RISK`, `CONFLICT`, `QUESTION`, `APPROVAL`, `SOURCE_REFERENCE`, `RENDER`, and `EXECUTION`.
  - Done when each construct has TypeScript types, validation rules, and at least one fixture.
- [ ] Add field status semantics: `CONFIRMED`, `MISSING`, `INCOMPLETE`, `AMBIGUOUS`, `CONFLICTING`, `ASSUMED`, `REJECTED`, and `NOT_APPLICABLE`.
  - Done when fields can carry status, source, required-for-completion flag, and approvals.
- [ ] Define canonical JSON serialization and stable hashing rules.
  - Done when equivalent DSL snapshots hash identically across Windows and Linux.
- [ ] Add migration or adapter notes from `office.dsl.v1` to the canonical model.
  - Done when current examples still validate or have a documented compatibility path.

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
- [ ] Add bilateral approval records.
  - Done when Human1 and Human2 approvals include party, hash, timestamp, and verdict.
- [ ] Invalidate approvals after DSL changes.
  - Done when tests prove both sides must reapprove after any material DSL edit.
- [ ] Support reopening clarification after Human2 rejects insufficient detail.
  - Done when Human2 can block finalization and trigger a question back to Human1.

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

- [ ] Define `scenario.json`.
  - Done when it declares input files, expected outputs, verifier mode, runtime mode, and optional answer scripts.
- [ ] Convert or mirror examples into `in/` and `out/` structure.
  - Done when existing six examples can still run and target examples have room for richer artifacts.
- [ ] Add runner for a single example.
  - Done when `corepack pnpm example:run <name>` generates artifacts and returns non-zero on mismatch.
- [ ] Add runner for all examples.
  - Done when `corepack pnpm examples:run` is CI-friendly on Windows and Linux.
- [ ] Add readable diffs for generated versus expected artifacts.
  - Done when JSON and Markdown differences are easy to inspect.
- [ ] Run Python verifier from the example runner when configured.
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

- [ ] Add CI for Windows and Linux.
  - Done when default checks pass on both systems.
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

1. Add the root `verify` script and document its exact command sequence.
2. Define `scenario.json` for current examples.
3. Build a single-example runner with generated artifact output.
4. Build all-example runner and CI-friendly diff reporting.
5. Add a canonical field-status model draft in TypeScript types.
6. Add source-reference types for DSL fields.
7. Add a minimal Human1/Human2 approval record model.
8. Change hashing design from plan hash only to canonical DSL snapshot hash.
9. Add runtime-to-Python verifier invocation behind a mock-safe interface.
10. Add the first target fixture: `01-chat-to-dsl` with `in/` and `out/` artifacts.
