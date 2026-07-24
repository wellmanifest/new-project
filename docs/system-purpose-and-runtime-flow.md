# System Purpose And Runtime Flow

## 1. Business Problem

The project is not meant to be only a small workflow language for office actions. Its long-term purpose is to formalize human intent before execution, document generation, code generation, or contract approval happens.

The problem is communication loss:

- a human writes an imprecise request,
- an LLM silently fills gaps,
- execution happens too early,
- the human discovers later that the system understood a different task.

The target system prevents this by turning natural language into an explicit, inspectable DSL. The DSL must show what is known, what is missing, what is ambiguous, what conflicts, and what was assumed.

## 2. Formalizing Intent

Formalizing intent means converting natural language, conversation history, or written guidelines into a structured representation that can be reviewed by humans and processed by machines.

The DSL is the source of truth. It should capture:

- parties and roles,
- intent and subject,
- obligations and deliverables,
- deadlines and payment,
- dependencies and exclusions,
- acceptance criteria,
- missing, ambiguous, conflicting, and assumed information,
- approvals tied to a specific DSL version,
- source references for each material field.

Current implementation status: the repository currently implements a narrow `office.dsl.v1` for office tasks. It does not yet implement the full intent/contract DSL described above.

## 3. H2M And H2H

Human-to-Machine (H2M) starts with one human asking the system to do something, for example preparing an unpaid invoice report. The system should generate DSL, ask for missing details, show a readable representation, require confirmation when risk is high, and only then execute or generate artifacts.

Human-to-Human (H2H) starts with communication between two sides:

- Human1: requester, employer, client, or author of the intent.
- Human2: assignee, employee, contractor, or other approving party.

In H2H, Human1 approval alone is not enough. Human2 must be able to say whether the DSL is sufficient to perform the work or accept the agreement. Both sides must approve the same DSL hash. Any DSL change invalidates previous approvals.

Current implementation status: only one-side confirmation exists. Human2, bilateral approval, and contract reopening are not implemented.

## 4. Target Architecture

```mermaid
flowchart LR
  H1["Human1 input"] --> Planner["LLM planner via OpenRouter"]
  H2["Human2 input or conversation"] --> Planner
  Files["Guideline files"] --> Planner
  Planner --> DSL["Canonical Intent/Contract DSL"]
  DSL --> Runtime["TypeScript runtime"]
  Runtime --> Validator["Structural and completeness validation"]
  Runtime --> Questions["Clarifying questions"]
  Runtime --> Approvals["Hash-based approvals"]
  Runtime --> Renderer["DSL to NL/document renderers"]
  Runtime --> Codegen["JS/Node.js code generator"]
  Runtime --> Testgen["DSL-based test generator"]
  Renderer --> Verifier["Python semantic verifier"]
  Codegen --> Verifier
  Testgen --> Verifier
  Verifier --> Audit["Audit and machine-readable verdict"]
```

Boundary note: today the TypeScript runtime does not call the Python verifier. The CLI and backend attach mock verifier objects. The Python verifier package can be run separately.

## 5. Role Of The DSL

The target DSL must formalize meaning, not only workflow steps. A future canonical DSL should support constructs such as:

```text
DOCUMENT
CONTRACT
PARTY
ROLE
INTENT
SUBJECT
OBLIGATION
DELIVERABLE
DEADLINE
PAYMENT
CONDITION
DEPENDENCY
ACCEPTANCE_CRITERIA
EXCLUSION
ASSUMPTION
RISK
CONFLICT
QUESTION
APPROVAL
SOURCE_REFERENCE
RENDER
EXECUTION
```

Every important field should be able to carry a status:

```text
CONFIRMED
MISSING
INCOMPLETE
AMBIGUOUS
CONFLICTING
ASSUMED
REJECTED
NOT_APPLICABLE
```

Current implementation status: `packages/dsl-model` defines `office.dsl.v1` with `task`, `sources`, `steps`, `output`, `policies`, `expectedResults`, and `errorHandling`. Supported actions are `database.query`, `report.generate`, `file.export`, `email.prepare`, `email.send`, `user.ask`, `user.confirm`, and `log.search`.

## 6. Role Of The LLM

The target LLM planner should:

- receive controlled context,
- generate DSL conforming to the canonical schema,
- mark missing fields instead of inventing values,
- preserve source references,
- identify assumptions,
- generate questions for unresolved fields,
- support single messages, conversations, and guideline files.

Current implementation status: `packages/llm-planner` has a deterministic mock planner and an optional OpenRouter code path. The validated path is mock mode. The mock planner uses simple text matching and does not perform semantic extraction from arbitrary conversation history.

## 7. Role Of The Runtime

The runtime is the orchestrator, not only an action executor. The target runtime should:

- maintain the current DSL,
- validate structure and completeness,
- detect missing, ambiguous, conflicting, and assumed information,
- manage process states,
- request questions from the LLM,
- route questions to Human1 or Human2,
- update only the relevant DSL fragments,
- recompute the DSL hash after each change,
- invalidate approvals when the DSL changes,
- render DSL to readable summaries or formal documents,
- start code and test generation when allowed,
- call the Python verifier,
- write a complete audit trail.

Current implementation status: `packages/dsl-runtime` validates `office.dsl.v1`, builds an execution plan, applies deterministic policy checks, handles `user.ask`, handles one-side confirmation, computes a plan hash, executes mock actions, and writes audit data through the file store.

## 8. NL To DSL To NL

```mermaid
sequenceDiagram
  participant Human as Human
  participant Planner as LLM Planner
  participant Runtime as Runtime
  participant Renderer as Renderer
  participant Verifier as Verifier

  Human->>Planner: Natural language request
  Planner->>Runtime: Candidate DSL
  Runtime->>Runtime: Structural and completeness checks
  Runtime-->>Human: Readable DSL plus gaps
  Human->>Runtime: Answers or approval
  Runtime->>Renderer: Approved DSL
  Renderer->>Verifier: Rendered NL/document
  Verifier-->>Runtime: PASS, FAIL, or NEEDS_REVIEW
```

The target renderer must never include facts that are absent from the approved DSL.

Current implementation status: the current renderer is `renderHumanDsl`, which produces a readable tokenized representation of the office DSL. It is not a legal document renderer.

## 9. Missing Data Flow

```mermaid
flowchart TD
  Input["Human input: build a website for Adam"] --> Partial["Partial DSL"]
  Partial --> Validate["Runtime validation"]
  Validate --> Missing{"Required fields missing?"}
  Missing -- Yes --> Context["Controlled LLM context with missingFields"]
  Context --> Question["Question: what is the deadline?"]
  Question --> Answer["Human answer"]
  Answer --> Patch["Patch specific DSL field"]
  Patch --> Validate
  Missing -- No --> Approval["Approval gate"]
```

The target runtime should ask focused questions and update specific fields. It must not let the LLM invent deadlines, prices, scope, legal terms, or acceptance criteria.

Current implementation status: missing data is represented only by `user.ask` steps in the office workflow. There is no general field-status model.

## 10. Conflict Diagnosis

Conflict diagnosis should detect when sources disagree. For example, Human1 says payment is 5000 PLN while Human2 says 7000 PLN. The DSL should represent both source references and mark the field as `CONFLICTING` until resolved.

Current implementation status: no general conflict model exists.

## 11. Human1/Human2 Approval

```mermaid
stateDiagram-v2
  [*] --> DSLGenerated
  DSLGenerated --> WaitingHuman1Approval
  WaitingHuman1Approval --> WaitingHuman2Approval: Human1 approves hash A
  WaitingHuman2Approval --> ReadyToRender: Human2 approves hash A
  WaitingHuman2Approval --> Clarification: Human2 rejects or asks questions
  Clarification --> DSLGenerated: DSL changed, approvals invalidated
  ReadyToRender --> Rendered
```

The target rule is simple: both required parties approve the same hash or the document is not final.

Current implementation status: the runtime stores confirmation IDs and a plan hash. It does not store party-specific approvals for a DSL hash.

## 12. Versioning, Hashes, And Traceability

Target behavior:

- DSL versions are immutable snapshots.
- Hashes are computed from canonical DSL content, not from a mutable runtime plan only.
- Approval records include party, hash, timestamp, and scope.
- Every material DSL field links to source text, speaker, message ID, file, or another traceable source.
- A DSL change invalidates approvals for older hashes.

Current implementation status: `hashPlan` hashes the execution plan. It protects confirmation against changed plans, but it is not yet a canonical DSL hash and does not model multi-party approval.

## 13. Document Generation

Target document types include:

- office command summary,
- task delegation,
- service agreement,
- employment agreement,
- contract,
- technical specification,
- implementation plan.

A final document must be generated only from approved DSL data. It should expose missing fields and conflicts instead of hiding them.

Current implementation status: no contract or legal document renderer is implemented.

## 14. Code And Test Generation

```mermaid
flowchart LR
  DSL["Approved DSL"] --> Requirements["Requirements and invariants"]
  Requirements --> Code["JS/Node.js code generator"]
  Requirements --> Tests["Unit, integration, API, E2E, security tests"]
  Code --> Results["Test results"]
  Tests --> Results
  Results --> Verifier["Python semantic verifier"]
  Verifier --> Decision["PASS / FAIL / NEEDS_REVIEW"]
```

The target system should generate tests from formal DSL elements such as requirements, invariants, acceptance criteria, prohibited behavior, expected output, error handling, and security policy.

Current implementation status: there is no JS/Node.js code generator and no DSL-based test generator. Existing tests cover the runtime, DSL model, security checks, E2E mock flow, and Python verifier package.

## 15. Python Semantic Verifier

The target verifier should compare:

- original NL,
- approved DSL,
- rendered document,
- generated code,
- generated tests,
- test results.

It should return a machine-readable verdict:

```text
PASS
FAIL
NEEDS_REVIEW
```

and include score, missing requirements, contradictions, unauthorized assumptions, uncovered acceptance criteria, code behavior mismatches, document mismatches, and recommended action.

Current implementation status: `verifier/office_dsl_verifier` is a Pydantic package with mock heuristics and an optional LiteLLM/OpenRouter path. The mock verifier checks a few unsafe or unauthorized-action patterns; it is not a full semantic verifier.

## 16. Examples

Target example structure:

```text
examples/
  01-chat-to-dsl/
    in/
    out/
    conversation.md
  02-chat-history-to-service-agreement/
    in/
    out/
    conversation.md
```

Current implementation status: the repository has six office examples: read-only report, clarification, email drafts, confirmed send, policy denial, and log analysis. Each keeps legacy flat fixtures and now also has `scenario.json`, `in/`, and `out/` files. The example runner generates artifacts under `.office-dsl/generated/examples/<scenario-id>/` and compares them with expected outputs. Current manifests use fixture DSL input because the mock planner still emits non-deterministic task IDs.

## 17. End-To-End Target Scenarios

The target system should eventually support:

- single chat to DSL,
- ambiguous chat to questions,
- two-party conversation to service agreement,
- guidelines to employment agreement,
- task delegation with recipient acceptance,
- both parties approving the same hash,
- DSL rendered back to NL without meaning drift,
- code and tests generated from approved DSL,
- verifier checking consistency across all artifacts.

## 18. Component Responsibility Boundaries

Planner:
Converts input into candidate DSL and questions. It does not approve, execute, or silently finalize.

Runtime:
Owns state, validation gates, approvals, hash rules, orchestration, rendering gates, execution, and audit.

DSL model:
Defines canonical structures, field statuses, source references, and validation rules.

Verifier:
Checks semantic consistency across source, DSL, documents, code, tests, and execution results.

UI/CLI/API:
Expose the process to humans. They should not contain separate business logic that contradicts the runtime.

## 19. Current State Versus Target State

DONE:

- offline workspace and pnpm scripts,
- `office.dsl.v1` model and structural validation,
- mock planner for single office commands,
- TypeScript runtime with simple state machine,
- deterministic policy checks,
- one-side confirmation with plan hash,
- mock data actions and dry-run execution,
- CLI, backend API, and static web demo,
- Python mock verifier package,
- static example fixtures plus runner-driven scenario manifests,
- TypeScript and Python tests for current scope.

PARTIAL:

- OpenRouter and LiteLLM paths exist but are not validated as the default flow,
- clarification exists only as workflow `user.ask`,
- DSL to NL exists only as a readable token renderer,
- audit exists for office-task sessions, not full intent/contract lifecycle.

MOCK:

- planner semantic understanding,
- verifier semantic judgment,
- external data and email operations,
- web UI as a demo surface.

NOT IMPLEMENTED:

- canonical Intent/Contract DSL,
- Human1/Human2 bilateral approval,
- field-level source traceability,
- conflict and assumption model,
- contract/legal renderers,
- planner-backed example regeneration for current stable fixtures,
- JS/Node.js code generation,
- DSL-based test generation,
- runtime-to-Python verifier integration,
- production security, auth, persistence, and CI hardening.
