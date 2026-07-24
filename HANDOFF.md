# Handoff

## Real Project Goal

This repository is the beginning of a DSL Runtime for formalizing human intent. The target system should convert natural language, conversations, and guideline files into an explicit Intent/Contract DSL, diagnose missing or conflicting communication, ask Human1/Human2 clarifying questions, require approvals for the same DSL hash, and only then render documents, generate code/tests, execute actions, or verify artifacts.

Do not treat the current Office DSL MVP as the complete project.

## Current Implemented State

DONE:

- pnpm workspace, TypeScript config, Vitest, ESLint, Prettier, Python verifier package config.
- `packages/dsl-model`: `office.dsl.v1`, parser, structural validator, JSON schema object, and human-readable token renderer.
- `packages/llm-planner`: deterministic mock planner for selected single-message office commands plus optional OpenRouter path.
- `packages/dsl-runtime`: simple state machine, deterministic policy engine, action registry, mock data operations, dry-run execution, `user.ask`, one-side confirmation, plan hash, audit persistence, and file task store.
- `packages/cli`: plan/run, validate, inspect, answer, confirm, reject, execute, and history.
- `apps/backend`: HTTP API using the same runtime.
- `apps/web`: static demo UI.
- `verifier`: Python mock verifier with Pydantic report model and optional LiteLLM/OpenRouter path.
- `examples`: six flat static office examples.
- `tests`: TypeScript and Python tests for current scope.
- Documentation alignment pass: README, TODO, VERSION, CHANGELOG, this handoff, and `docs/system-purpose-and-runtime-flow.md`.

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
- Hashing is plan-based, not a canonical immutable DSL snapshot hash.
- Audit exists for office-task sessions, not the full target lifecycle.

NOT IMPLEMENTED:

- Canonical Intent/Contract DSL.
- Human1/Human2 bilateral approval.
- Conversation-history ingestion.
- Guideline-file ingestion.
- Field-level source traceability.
- Conflict and assumption model.
- Contract/legal renderers.
- Example runner with regeneration and diffs.
- JS/Node.js code generation.
- Test generation from DSL.
- Runtime invocation of the Python verifier as a gating step.

## Priority For The Next Agent

Start with repeatability before expanding semantics:

1. Add a root `verify` script for typecheck, lint, format, TypeScript tests, Python tests, and `git diff --check`.
2. Define `scenario.json` for the current six examples.
3. Build `example:run <name>` that regenerates artifacts and compares them with expected outputs.
4. Build `examples:run` for all examples.
5. Only then start adding canonical field statuses and source-reference types.

Reason: without an example runner, the richer Intent/Contract DSL can drift without clear regression feedback.

## What Not To Misread As Done

- `renderHumanDsl` is not a legal document generator.
- Current confirmation is not Human1/Human2 approval.
- `hashPlan` is not a canonical DSL hash.
- The mock planner is not semantic NL understanding.
- The Python verifier does not prove NL/DSL/document/code/test equivalence.
- Static examples are not executable regression scenarios yet.
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

Python tests:

```powershell
$env:PYTHONPATH='verifier'
python -m pytest verifier/tests -q
```

Backend and UI:

```powershell
corepack pnpm run dev:backend
```

Open `http://127.0.0.1:3000`.

Validate one example DSL:

```powershell
corepack pnpm cli -- validate examples/01-read-only-report/expected.json --json
```

## Important Files

- `docs/system-purpose-and-runtime-flow.md` - main purpose and runtime-flow architecture.
- `TODO.md` - staged roadmap and implementation priorities.
- `README.md` - current status, target architecture, commands, and limitations.
- `CHANGELOG.md` - release history.
- `VERSION.md` - current version metadata.
- `packages/dsl-model/src/index.ts` - current DSL model.
- `packages/dsl-runtime/src/index.ts` - current runtime/state/policy/action implementation.
- `packages/llm-planner/src/index.ts` - current mock/OpenRouter planner.
- `verifier/office_dsl_verifier/core.py` - current Python verifier.
- `examples/` - static fixtures that should become runner-driven scenarios.

## Validation Notes

Run validation again after any change. If a command fails because of environment state, report the exact command, error, and whether it appears to be project code or environment/dependency setup.
