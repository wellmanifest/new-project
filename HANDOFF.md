# Handoff

## Current State

The repository now contains a working offline Office DSL MVP on branch `main`. The latest validated implementation supports single natural-language office commands, mock DSL planning, TypeScript runtime validation/orchestration, dry-run mock actions, one-side confirmation, clarification answers, audit records, CLI usage, backend API, static web demo, Python mock verifier, and six static example scenarios.

## Completed

- Added pnpm workspace, TypeScript config, Vitest tests, ESLint and Prettier config.
- Added DSL model package with parser, validator, JSON schema object, and human-readable renderer.
- Added runtime package with state machine, policy engine, action registry, mock data operations, dry-run execution, confirmation handling, answer handling, plan hashing, and audit persistence.
- Added mock LLM planner and optional OpenRouter planner path.
- Added CLI and backend using the same runtime.
- Added static web demo.
- Added Python verifier package with mock mode and optional LiteLLM/OpenRouter path.
- Added mock data and examples.
- Migrated historical research folders into `research/` and verified byte-identical contents for moved files.
- Added architecture, changelog, version, and handoff documentation.

## Not Completed

- Full Intent/Contract DSL specification and implementation.
- Two-party conversation ingestion.
- Text-guidelines file ingestion.
- Bilateral approval for contracts.
- Contract rendering and final document generation.
- Dedicated example runner with regeneration and diffs.
- CI for Windows/Linux.
- Docker/container workflow.
- Verified OpenRouter/LiteLLM online execution.
- Linux validation.

## How To Run

Install dependencies, only when needed:

```powershell
corepack pnpm install --frozen-lockfile
```

Typecheck:

```powershell
corepack pnpm exec tsc -b --pretty false
```

Run TypeScript tests:

```powershell
corepack pnpm exec vitest run --reporter=verbose --no-file-parallelism --testTimeout=10000 --hookTimeout=10000
```

Run Python tests:

```powershell
$env:PYTHONPATH='verifier'
python -m pytest verifier	ests -q
```

Run backend and UI:

```powershell
corepack pnpm run dev:backend
```

Open `http://127.0.0.1:3000`.

Validate one example:

```powershell
corepack pnpm cli -- validate examples/01-read-only-report/expected.json --json
```

## Current Problems And Limitations

- In the Codex sandbox, Vitest worker startup failed with `spawn EPERM`; tests passed when run outside the sandbox using the local `node_modules/.bin` command.
- Python pytest passed but emitted a cache warning because pytest could not create a cache directory under `verifier/`.
- README and TODO now describe the MVP state, but many TODO items intentionally remain open.
- `project.sh` remains historical and should not be used as MVP bootstrap.

## Next Concrete Step

Implement the full example runner before expanding the DSL further:

1. Define `scenario.json` for the existing six examples.
2. Add `in/` and `out/` structure or a compatibility adapter for current files.
3. Add a runner command that executes planner, runtime, verifier, and compares generated output with expected artifacts.
4. Add tests for the runner.
5. Only then mark example regression TODO items as complete.

## Important Files And Directories

- `TODO.md` - source of planned work and current completion status.
- `README.md` - installation, usage, tests, examples, and limitations.
- `CHANGELOG.md` - release changes.
- `VERSION.md` - current MVP version and validation status.
- `docs/architecture.md` - architecture and process model.
- `docs/research-migration-audit.md` - research migration proof.
- `packages/dsl-model/` - DSL model, parser, validator, renderer.
- `packages/dsl-runtime/` - runtime, policies, actions, audit, persistence.
- `packages/llm-planner/` - mock/OpenRouter planner.
- `packages/cli/` - CLI entrypoint.
- `apps/backend/` - HTTP API.
- `apps/web/` - static demo UI.
- `verifier/` - Python verifier.
- `examples/` - static scenario artifacts.
- `tests/` - Vitest coverage.
- `mock-data/` - offline data.
- `research/` - historical research material.

## Final Validation Note

Final validation note: an earlier full Vitest run passed 15/15, but a later final rerun in this Codex session failed before test collection because local pnpm links in `node_modules` could not resolve `@vitest/utils`. No install was run after the user requested not to rerun install. Manual relink attempts were not committed because `node_modules` is ignored. The next operator should refresh dependencies with `corepack pnpm install --frozen-lockfile` and rerun the final validation.

