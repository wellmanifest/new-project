# DSL Runtime

DSL Runtime is a project for formalizing human intent before a system executes a task, generates a document, creates code, or asks people to approve an agreement.

The current repository is an offline Office DSL MVP. It proves a narrow path:

```text
single natural-language office request
-> mock planner
-> office.dsl.v1 JSON
-> TypeScript runtime
-> validation, policy checks, questions or confirmation
-> dry-run mock execution
-> audit
```

This MVP is useful, but it is not the full target system. The target system is an Intent/Contract DSL runtime for Human-to-Machine and Human-to-Human workflows.

## Target Architecture

The intended architecture is:

```text
NL / conversation / guideline files
-> LLM through OpenRouter
-> canonical Intent/Contract DSL
-> runtime validation and gap/conflict diagnosis
-> clarifying questions to Human1 or Human2
-> hash-based approvals by all required parties
-> DSL to NL/document rendering
-> optional JS/Node.js code generation
-> optional DSL-based test generation
-> Python semantic verifier
-> audit
```

See [docs/system-purpose-and-runtime-flow.md](docs/system-purpose-and-runtime-flow.md) for the full architecture, flow diagrams, component boundaries, and current-vs-target state.

## Current Implementation Status

DONE:

- `packages/dsl-model` defines `office.dsl.v1`, structural validation, parsing, and a readable token renderer.
- `packages/intent-contract-model` defines the standalone `intent-contract.dsl.v1` model boundary with formal fields, statuses, source references, canonical serialization, stable hashing, and a deterministic Office DSL adapter.
- `packages/llm-planner` provides deterministic mock planners for office scenarios, conversation fixtures, and selected canonical NL/guideline-file to Intent/Contract DSL flows, plus a controlled OpenRouter response schema boundary.
- `packages/document-renderer` renders task delegation, service agreement, and employment/guideline draft documents from an Intent/Contract DSL snapshot, with a draft legal disclaimer, explicit gap markers for unresolved fields, and a document-to-DSL traceability map.
- `packages/pdf-generator` owns deterministic minimal PDF generation and text extraction for checked-in fixtures, including Markdown-to-PDF fixture output, contract PDF output, and scanned-fixture OCR routing signals.
- `packages/testgen` defines typed `intent-contract.testgen-input.v1` inputs, extracts them deterministically from an Intent/Contract DSL snapshot, generates unit/integration/API/E2E/security/error-handling test specifications, and verifies coverage against acceptance criteria.
- `packages/codegen` defines a bounded JS/Node.js code-generation target, creates deterministic implementation plans from bilaterally approved Intent/Contract DSL snapshots, emits dependency-free Node ESM artifacts, runs generated tests, and returns verifier input with generated file hashes and test results.
- `verifier` exposes a mock-safe semantic verifier that checks original NL/source quotes against approved DSL, rendered document coverage against DSL paths, generated code test results, uncovered generated-test acceptance criteria, and can be invoked from the TypeScript runtime.
- `packages/dsl-runtime` creates sessions, evaluates policies, asks simple clarification questions, handles one-side Office confirmation, computes a plan hash, stores a canonical Intent/Contract snapshot hash, tracks minimal Human1/Human2 approval records, executes mock actions, and records audit data.
- `packages/cli` exposes plan, validate, inspect, answer, confirm, reject, execute, and history commands, plus a `well-manifest-intent` entry point with canonical Intent/Contract commands (`plan`, `plan-file`, `render`, `testgen`, `codegen`, `verify`, `approve`, `chat`, `example`, `recruitment`) and cross-platform Windows/Linux path normalization.
- `apps/backend` exposes the same runtime through HTTP endpoints.
- `apps/web` provides a static demo UI.
- `verifier` contains a Python package with mock verification and an optional LiteLLM/OpenRouter path.
- `examples` contains six office examples with `scenario.json`, `in/`, `out/`, and legacy fixture files.
- `examples-chat` contains four executable Human1/Human2 negotiation scenarios with `scenario.json`, `chat.txt`, and expected outcomes.
- `tests` cover the current TypeScript runtime, canonical approval records, DSL model, security checks, E2E mock flow, Python verifier behavior, example runners, chat/recruitment negotiation runners, NL <-> DSL round-trip utilities, contract/legal document rendering, DSL-driven test-generation spec and coverage verification, approved-DSL JS/Node.js code generation, and TypeScript-to-Python semantic verifier integration.

PARTIAL:

- OpenRouter and LiteLLM code paths exist, and the planner now has a controlled OpenRouter response schema boundary, but the validated flow is still mock/offline mode.
- Clarifying questions exist only as `user.ask` workflow steps, not as a general field-status model.
- Document, test, JS/Node.js code generation, and Python semantic verification are implemented as package/runtime boundaries but are not yet wired into the CLI/backend/UI as production surfaces.
- Office action confirmation is still plan-hash based; canonical Intent/Contract approval records exist in runtime APIs but are not yet exposed through CLI/backend/UI flows.

MOCK:

- Planner semantic understanding is deterministic and heuristic in mock mode.
- The verifier uses heuristics in mock mode.
- Data sources and email operations use local mock data and dry-run behavior.
- The frontend is a demo surface.

NOT IMPLEMENTED:

- CLI/backend/UI integration of canonical Intent/Contract approval flows.
- Production OpenRouter validation for arbitrary conversation history and guideline files.
- Runtime/CLI/backend/UI wiring for contract/legal document rendering, test generation, JS/Node.js code generation, and semantic verification as production flows.
- Live OpenRouter/LiteLLM semantic verifier validation in the default test suite.

## Example Uses

Current MVP examples:

- read-only unpaid invoice report,
- ambiguous sales report that requires a period question,
- reminder drafts without sending,
- confirmed mock send,
- policy denial for unsafe delete/shell-like requests,
- log analysis over mock activity data.

Target examples:

- single chat to DSL,
- two-party conversation to service agreement,
- guideline file to employment agreement,
- task delegation with recipient review,
- bilateral approval of the same DSL hash,
- DSL to document/code/tests with semantic verification.

## Requirements

Validated or declared by the repository:

- Node.js compatible with the pinned workspace dependencies.
- pnpm `9.12.0` through Corepack.
- TypeScript `5.7.3`.
- Vitest `3.0.4`.
- Python `>=3.11` for the verifier package.
- Windows is the currently validated workspace. Linux compatibility is expected but not verified in the current release notes.

## Install

```powershell
corepack pnpm install --frozen-lockfile
```

## CLI

Plan from natural language:

```powershell
corepack pnpm cli -- plan "Przygotuj raport niezaplaconych faktur starszych niz 30 dni." --json
```

Validate an example DSL:

```powershell
corepack pnpm cli -- validate examples/01-read-only-report/expected.json --json
```

Inspect, answer, confirm, reject, execute, and show history:

```powershell
corepack pnpm cli -- inspect TASK_ID --json
corepack pnpm cli -- answer TASK_ID period "ostatnie 30 dni" --json
corepack pnpm cli -- confirm TASK_ID send-reminders PLAN_HASH --json
corepack pnpm cli -- reject TASK_ID --json
corepack pnpm cli -- execute TASK_ID --json
corepack pnpm cli -- history --json
```

Execution is dry-run by default. Use `--execute` only when intentionally writing mock output files such as the local outbox or exports.

## Backend And Web Demo

```powershell
corepack pnpm run dev:backend
```

Open:

```text
http://127.0.0.1:3000
```

Useful endpoints:

- `GET /openapi.json`
- `GET /api/actions`
- `GET /api/connectors`
- `POST /api/tasks`
- `GET /api/tasks/{id}`
- `POST /api/tasks/{id}/answers`
- `POST /api/tasks/{id}/confirm`
- `POST /api/tasks/{id}/reject`
- `POST /api/tasks/{id}/execute`
- `GET /api/tasks/{id}/audit`

## Intent/Contract Model

The canonical model currently lives in `packages/intent-contract-model`. The Office DSL runtime stores a migrated canonical snapshot hash for approval records, while the model package still owns the DSL structure and hashing helpers. It provides:

- `intent-contract.dsl.v1`,
- core constructs for documents, contracts, parties, obligations, deliverables, deadlines, payments, conflicts, questions, approvals, render directives, and execution directives,
- field statuses such as `CONFIRMED`, `MISSING`, `AMBIGUOUS`, `CONFLICTING`, and `ASSUMED`,
- source references for message, conversation, file, human, system, and derived inputs,
- canonical JSON serialization and stable SHA-256 hashing.

Validate the model through the regular TypeScript test suite:

```powershell
corepack pnpm test
```

## Example Runner

Current examples now have canonical `scenario.json` manifests plus mirrored `in/` and `out/` folders. The runner writes generated artifacts to `examples/<scenario>/generated/` and compares them with expected outputs.

Run one example:

```powershell
corepack pnpm run example:run -- 01-read-only-report
```

Run all examples:

```powershell
corepack pnpm run examples:run
```

The current manifests use a fixture DSL source because the existing expected DSL files are stable, while the mock planner still produces random task IDs. The manifest format also reserves planner modes for future `mock` and `openrouter` scenarios.

### Chat Negotiation Examples

`examples-chat` scenarios are executable regression fixtures, not static samples. Each scenario has `scenario.json`, `chat.txt`, and `out/expected.summary.json`. The chat runner processes each `@user1`/`@user2` line in order, writes deterministic artifacts after every utterance, validates generated `.dsl.hcl` files as HCL-highlighted project DSL, compares the generated summary with the expected outcome, and ends as either `AGREED` or `CANCELLED`.

Run one chat scenario:

```powershell
corepack pnpm run example-chat:run -- 01-short-agreement
```

Run all chat scenarios:

```powershell
corepack pnpm run examples-chat:run
```

Generated DSL artifacts use `*.dsl.hcl`: HCL-like syntax for automatic editor highlighting, with project-specific blocks such as `document`, `field`, `conflict`, and `change`. They are not JSON and are not Terraform files; HCL is only the host shape for coloring and manual editing. The runner validates the project-specific DSL/HCL structure before writing artifacts. By default, generated chat outputs are written as flat files next to each scenario under `examples-chat/<scenario>/generated/`, which is ignored by Git.

For agreed scenarios, `final-contract.dsl.hcl`, `contract.pdf`, and `approvals.dsl.hcl` are created only when both parties approve the same current merged contract hash. A one-side approval cannot create final artifacts, and a later contract change invalidates the earlier approval. Cancelled scenarios never create final contract or PDF artifacts.

### Recruitment Examples

`examples-recruitment` contains executable multi-candidate recruitment fixtures. The runner ingests `oferta.md`, `cv.md`, and `cv.pdf`, uses deterministic mock OCR fallback for scanned fixture PDFs, generates sourced proposal DSL, reuses chat negotiation scenarios per candidate, and compares accepted/rejected summaries with expected outputs.

Run one recruitment scenario:

```powershell
corepack pnpm run example-recruitment:run -- 01-multi-candidate
```

Run all recruitment scenarios:

```powershell
corepack pnpm run examples-recruitment:run
```

Generated recruitment artifacts are written under `examples-recruitment/<scenario>/generated/` and per-candidate `out/` files. These generated outputs are ignored by Git.

## Tests And Checks

Install:

```powershell
corepack pnpm install --frozen-lockfile
```

Typecheck:

```powershell
corepack pnpm run typecheck
```

Lint:

```powershell
corepack pnpm run lint
```

Format check:

```powershell
corepack pnpm run format
```

TypeScript tests:

```powershell
corepack pnpm test
```

Python verifier tests:

```powershell
$env:PYTHONPATH='verifier'
python -m pytest verifier/tests -q
```

Python verifier tests:

```powershell
corepack pnpm run python:test
```

Full repository verification:

```powershell
corepack pnpm run verify
```

The same operations are available through `project.sh`, for example `bash project.sh verify`, `bash project.sh examples`, `bash project.sh example 01-read-only-report`, `bash project.sh examples-chat`, and `bash project.sh example-chat 01-short-agreement`.

Whitespace check:

```powershell
git diff --check
```

## Mock Mode

Mock mode is the validated default:

```text
OFFICE_DSL_LLM_MODE=mock
OFFICE_DSL_VERIFIER_MODE=mock
OFFICE_DSL_DATA_DIR=mock-data
OFFICE_DSL_TASK_DIR=.office-dsl/tasks
OFFICE_DSL_AUDIT_DIR=.office-dsl/audit
OFFICE_DSL_EXPORT_DIR=.office-dsl/exports
```

OpenRouter planner mode requires `OPENROUTER_API_KEY`. Python LiteLLM/OpenRouter verifier mode requires installing the verifier with the optional `openrouter` extra. These online paths are not the validated MVP path.

## Documentation

- [docs/system-purpose-and-runtime-flow.md](docs/system-purpose-and-runtime-flow.md) - target purpose, runtime flow, diagrams, current-vs-target state.
- [docs/architecture.md](docs/architecture.md) - earlier MVP architecture notes.
- [docs/research-migration-audit.md](docs/research-migration-audit.md) - research migration audit.
- [docs/office-to-intent-contract-mapping.md](docs/office-to-intent-contract-mapping.md) - mapping from office requests to Intent/Contract DSL.
- [docs/document-renderers.md](docs/document-renderers.md) - contract/legal document renderer responsibilities, legal disclaimers, and the document-to-DSL traceability map.
- [docs/test-generation.md](docs/test-generation.md) - test-generation DSL inputs, spec generation, and coverage verification against acceptance criteria.
- [docs/code-generation.md](docs/code-generation.md) - bounded JS/Node.js code-generation target, approved DSL gate, generated artifacts, and verifier input.
- [docs/semantic-verifier.md](docs/semantic-verifier.md) - Python semantic verifier inputs, reports, mock checks, TypeScript runtime bridge, and OpenRouter/LiteLLM boundary.
- [docs/cli-cross-platform.md](docs/cli-cross-platform.md) - cross-platform Windows/Linux CLI surface, canonical Intent/Contract commands, and path normalization.
- [TODO.md](TODO.md) - staged implementation roadmap.
- [HANDOFF.md](HANDOFF.md) - next-agent handoff notes.
- [VERSION](VERSION) - version scope and validation notes.
- [CHANGELOG.md](CHANGELOG.md) - release history.
