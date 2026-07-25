# Handoff

## Real Project Goal

This repository is the beginning of a DSL Runtime for formalizing human intent. The target system should convert natural language, conversations, and guideline files into an explicit Intent/Contract DSL, diagnose missing or conflicting communication, ask Human1/Human2 clarifying questions, require approvals for the same DSL hash, and only then render documents, generate code/tests, execute actions, or verify artifacts.

Do not treat the current Office DSL MVP as the complete project.

## Current Implemented State

DONE:

- pnpm workspace, TypeScript config, Vitest, ESLint, Prettier, Python verifier package config.
- `packages/dsl-model`: `office.dsl.v1`, parser, structural validator, JSON schema object, and human-readable token renderer.
- `packages/intent-contract-model`: standalone `intent-contract.dsl.v1` model, formal fields, statuses, source references, canonical serialization, stable hashing, and Office DSL compatibility adapter.
- `packages/llm-planner`: deterministic mock planner for selected single-message office commands plus optional OpenRouter path.
- `packages/dsl-runtime`: simple state machine, deterministic policy engine, action registry, mock data operations, dry-run execution, `user.ask`, one-side Office confirmation, plan hash, canonical Intent/Contract snapshot hash, minimal Human1/Human2 approval records, approval invalidation, audit persistence, and file task store.
- `packages/cli`: plan/run, validate, inspect, answer, confirm, reject, execute, and history.
- `apps/backend`: HTTP API using the same runtime.
- `apps/web`: static demo UI.
- `verifier`: Python mock verifier with Pydantic report model and optional LiteLLM/OpenRouter path.
- `examples`: six office examples with legacy flat fixtures plus canonical `scenario.json`, `in/`, and `out/` structure.
- `examples-chat`: four executable Human1/Human2 negotiation scenarios with line-by-line artifacts, expected outcomes, bilateral current-hash approval finalization, approval invalidation, cancellation coverage, and generated `*.dsl.hcl` files rendered as HCL-highlighted project DSL rather than JSON.
- `tests`: TypeScript and Python tests for current scope, including example runner, chat negotiation runner, CLI, backend, store, security, runtime, and Intent/Contract model coverage.
- Documentation alignment pass: README, TODO, VERSION, CHANGELOG, this handoff, and `docs/system-purpose-and-runtime-flow.md`.
- Example runner pass: `@office-dsl/example-runner`, `example:run`, `examples:run`, root `verify`, and safe `project.sh` command dispatch.
- GitHub Actions workflow: `.github/workflows/verify.yml` runs `bash project.sh install` and `bash project.sh verify` on Ubuntu and Windows.

## Mock Or Partial Areas

MOCK:

- Planner semantic understanding is pattern matching in mock mode.
- Python verifier is heuristic in mock mode.
- Mock data replaces real connectors.
- Email sending is dry-run/local mock behavior by default.

PARTIAL:

- OpenRouter/LiteLLM code paths exist but are not validated as the default flow.
- Clarification exists only as workflow `user.ask`, not field-level missing/ambiguous/conflicting statuses.
- Rendering is a readable office DSL listing, not formal contract/legal documents.
- Office action confirmation is plan-based; runtime canonical approval records are hash-based, but they are not wired into CLI/backend/UI flows yet.
- Codex Windows sandbox blocks Vitest/Vite process creation with `spawn EPERM`; see `docs/codex-sandbox-vitest.md`.
- Audit exists for office-task sessions, not the full target lifecycle.

NOT IMPLEMENTED:

- CLI/backend/UI exposure for canonical Intent/Contract approval flows.
- Conversation-history ingestion.
- Guideline-file ingestion.
- Runtime/planner population of field-level source traceability.
- Runtime conflict and assumption diagnosis.
- Contract/legal renderers.
- JS/Node.js code generation.
- Test generation from DSL.
- Runtime invocation of the Python verifier as a gating step.

## Priority For The Next Agent

Continue from verifier and exposure work before expanding rendering or code generation:

1. Add runtime-to-Python verifier invocation behind a mock-safe interface.
2. Expose canonical approval records through CLI/backend flows.
3. Promote fixture-level chat negotiation semantics into runtime/planner-backed Intent/Contract workflow after the current runner stays stable.
4. Add the first target Intent/Contract scenario fixture after the current runner stays stable.

Reason: runtime approval records now exist, but they are still not available through user-facing workflows or verifier gates.

## What Not To Misread As Done

- `renderHumanDsl` is not a legal document generator.
- Current Office action confirmation is separate from Human1/Human2 canonical approval records.
- `hashPlan` is still only the Office execution-plan confirmation hash; canonical approval records use the Intent/Contract snapshot hash.
- The mock planner is not semantic NL understanding.
- The Python verifier does not prove NL/DSL/document/code/test equivalence.
- Current office examples are executable regression scenarios, but they use fixture DSL input rather than planner-regenerated DSL because mock planner IDs are still non-deterministic.
- Current chat examples are executable regression scenarios for deterministic negotiation behavior, not arbitrary production conversation understanding.
- The backend/web demo is not a production workflow UI.

## How To Run

Install dependencies when needed:

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
corepack pnpm run python:test
```

All examples:

```powershell
corepack pnpm run examples:run
```

Full verification:

```powershell
corepack pnpm run verify
```

`project.sh` exposes the same commands for Bash-capable environments. In the local Codex Windows sandbox, Bash/WSL can fail with `E_ACCESS_DENIED`; use the equivalent `corepack pnpm ...` commands there.

## Recent Stable Milestones

- `0.7.2`: generated `examples-chat` artifacts use scenario-local ignored `generated/` folders and `*.dsl.hcl` editable project DSL for automatic HCL-style highlighting.
- `0.7.1`: generated `examples-chat` `.dsl` artifacts use editable line-oriented DSL text and are validated before writing.
- `0.7.0`: minimal runtime Human1/Human2 canonical approval records and invalidation after snapshot changes.
- `0.6.0`: executable Human1/Human2 chat negotiation examples and bilateral current-hash finalization checks.
- `0.5.0`: GitHub Actions verify workflow plus Codex sandbox Vitest limitation documentation.
- `0.4.0`: Office DSL to Intent/Contract adapter and expanded regression coverage.
- `0.3.0`: canonical Intent/Contract model boundary.
- `0.2.0`: deterministic example runner and root verification command.
- `0.1.1`: documentation alignment with current-versus-target status.
- `0.1.0`: offline Office DSL MVP.

## Key Files To Read First

- `TODO.md` - staged roadmap and implementation priorities.
- `README.md` - current status, target architecture, commands, and limitations.
- `CHANGELOG.md` - release history.
- `VERSION` - current version scope and validation notes.
- `docs/system-purpose-and-runtime-flow.md` - target system architecture and runtime flow.
- `docs/office-to-intent-contract-migration.md` - Office DSL compatibility adapter notes.
- `docs/codex-sandbox-vitest.md` - local sandbox Vitest/Vite limitation.
- `packages/intent-contract-model/src/index.ts` - canonical model and adapter.
- `packages/dsl-runtime/src/index.ts` - current runtime and approval limitations.
- `packages/example-runner/src/chat.ts` - deterministic chat negotiation example runner and generated `*.dsl.hcl` text validator.
- `examples-chat/` - executable chat negotiation scenarios.
- `.github/workflows/verify.yml` - CI verification workflow.
