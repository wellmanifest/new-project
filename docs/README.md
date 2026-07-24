# Documentation Index

## Sources Of Truth

- `README.md` - project purpose, current implementation status, target architecture, commands, and limitations.
- `TODO.md` - staged implementation roadmap with completion criteria.
- `docs/system-purpose-and-runtime-flow.md` - primary architecture document for intent formalization, H2M/H2H, runtime flow, approvals, traceability, documents, code, tests, verifier, examples, and current-vs-target state.
- `docs/architecture.md` - earlier MVP architecture notes for the offline Office DSL implementation.
- `POLICY.md` - repository safety and evidence rules.
- `CONTRIBUTING.md` - procedural workflow for repository changes.
- `HANDOFF.md` - next-agent handoff and immediate priorities.
- `VERSION.md` - current version and validation notes.
- `CHANGELOG.md` - release history.
- `docs/research-migration-audit.md` - audit of historical research migration.
- `docs/office-to-intent-contract-migration.md` - Office DSL to Intent/Contract compatibility mapping.
- `project.sh` - historical script; not the active MVP bootstrap.

## Research Materials

Historical research folders live under `research/` and should not be moved back to their old root locations:

- `research/GPT56Luna/`
- `research/Opus48Medium/`
- `research/SWE17/`
- `research/perplexity/22.07/`
- `research/perplexity/23.07/`

## Current Working Structure

- `packages/dsl-model/` - current executable `office.dsl.v1` model, parser, validator, and renderer.
- `packages/intent-contract-model/` - standalone canonical `intent-contract.dsl.v1` model, status semantics, source references, stable hashing, and Office DSL adapter.
- `packages/dsl-runtime/` - current TypeScript runtime, state machine, policies, actions, hashing, audit, and file store.
- `packages/llm-planner/` - mock planner and optional OpenRouter path.
- `packages/cli/` - CLI entrypoint.
- `apps/backend/` - demo HTTP API.
- `apps/web/` - static demo UI.
- `verifier/` - Python verifier package.
- `examples/` - current office fixtures with `scenario.json`, `in/`, `out/`, and legacy flat files.
- `tests/` - TypeScript tests.
- `mock-data/` - local offline data.

## Recommended Reading Order For Agents

1. `README.md`
2. `docs/system-purpose-and-runtime-flow.md`
3. `TODO.md`
4. `HANDOFF.md`
5. `POLICY.md`
6. `CONTRIBUTING.md`
7. Current code in `packages/`, `apps/`, `verifier/`, `examples/`, `tests/`, and `mock-data/`
8. `docs/architecture.md` for earlier MVP context
9. `research/` only when historical project intent or prior analysis matters

## Current Boundary

The validated repository is an offline Office DSL MVP with a repeatable example runner, a standalone Intent/Contract model package, and a deterministic Office DSL compatibility adapter. The target Intent/Contract DSL, Human1/Human2 approvals, field traceability, legal renderers, code generation, test generation, and semantic verifier orchestration are roadmap items, not completed features.
