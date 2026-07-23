# Office DSL MVP

Office DSL MVP formalizes simple office work requests into a deterministic JSON DSL, validates the DSL, routes it through a TypeScript runtime, and records an audit trail. The current version is an offline MVP: it uses mock data and mock planning by default, and it does not require OpenRouter, LiteLLM, external APIs, email delivery, or internet access at runtime.

## What Works

- Single natural-language office requests can be converted into `office.dsl.v1` JSON by the mock planner.
- The DSL model validates structure, supported mock sources, supported actions, confirmations, and output metadata.
- The runtime builds an execution plan, applies deterministic policy checks, handles clarification questions, handles one-side confirmation, executes mock actions in dry-run mode by default, and records audit JSON.
- The CLI can plan, validate, inspect, answer, confirm, reject, execute, and show task history.
- The backend exposes the same runtime through HTTP endpoints and serves the static demo UI.
- The Python verifier runs in mock mode and returns machine-readable verification reports.
- Six example scenarios are present and their expected DSL artifacts validate offline.

## What Remains Open

- Full Intent/Contract DSL with `CONTRACT`, `PARTY`, `OBLIGATION`, `PAYMENT`, bilateral approval, and contract rendering is not complete.
- Conversation-to-DSL and file-guidelines-to-DSL flows are not implemented beyond documentation and planned scope.
- The examples do not yet have a dedicated runner that regenerates output and diffs `in/` vs `out/` folders.
- OpenRouter and LiteLLM integrations exist as optional code paths, but were not tested because mock/offline mode is the validated MVP path.
- Linux compatibility is expected from the stack but was not verified in this run.

## Requirements

Validated in this workspace:

- Node.js: `24.18.0` during Vitest runs
- pnpm: project pins `pnpm@9.12.0` via `packageManager`
- TypeScript: `5.7.3`
- Vitest: `3.0.4`
- Python: tests ran with Python `3.14`; verifier declares `>=3.11`
- OS: Windows workspace

## Installation

Use Corepack and the pinned pnpm version:

```powershell
corepack pnpm install --frozen-lockfile
```

Do not run install repeatedly when diagnosing pnpm. First inspect `node_modules`, `pnpm-lock.yaml`, `pnpm-workspace.yaml`, `.npmrc`, and `pnpm store path`.

## Mock Mode

Mock mode is the default. `.env.example` documents the available variables:

```text
OFFICE_DSL_LLM_MODE=mock
OPENROUTER_API_KEY=
OPENROUTER_MODEL=openai/gpt-4.1-mini
OFFICE_DSL_DATA_DIR=mock-data
OFFICE_DSL_AUDIT_DIR=.office-dsl/audit
OFFICE_DSL_EXPORT_DIR=.office-dsl/exports
```

The runtime reads mock data from `mock-data/`. Email sending is represented by a mock outbox and is dry-run by default unless execution is explicitly requested.

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

## Backend And Web Demo

Run the backend and static UI:

```powershell
corepack pnpm run dev:backend
```

Open:

```text
http://127.0.0.1:3000
```

Useful API endpoints:

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

## Tests

Typecheck:

```powershell
corepack pnpm exec tsc -b --pretty false
```

Full TypeScript tests:

```powershell
corepack pnpm exec vitest run --reporter=verbose --no-file-parallelism --testTimeout=10000 --hookTimeout=10000
```

Single test files:

```powershell
corepack pnpm exec vitest run tests/dsl.test.ts --reporter=verbose --testTimeout=10000 --hookTimeout=10000
corepack pnpm exec vitest run tests/runtime.test.ts --reporter=verbose --testTimeout=10000 --hookTimeout=10000
corepack pnpm exec vitest run tests/security.test.ts --reporter=verbose --testTimeout=10000 --hookTimeout=10000
corepack pnpm exec vitest run tests/e2e.test.ts --reporter=verbose --testTimeout=10000 --hookTimeout=10000
```

Python verifier tests:

```powershell
$env:PYTHONPATH='verifier'
python -m pytest verifier	ests -q
```

In the Codex sandbox, Vitest worker startup returned `spawn EPERM`; the tests passed when run outside the sandbox with the local `node_modules/.bin` command.

## Examples

Current examples live in `examples/01-read-only-report` through `examples/06-log-analysis`.

Validate all current examples manually:

```powershell
Get-ChildItem examples -Directory | Sort-Object Name | ForEach-Object {
  corepack pnpm cli -- validate "$($_.FullName)\expected.json" --json | Out-Null
  python -c "import json, pathlib; p=pathlib.Path(r'$($_.FullName)'); [json.load(open(p/name, encoding='utf-8')) for name in ['expected.json','expected-plan.json','expected-verification.json']]; print('JSON OK ' + p.name)"
}
```

A dedicated example runner that regenerates output and displays diffs is still open.

## OpenRouter And LiteLLM

OpenRouter/LiteLLM are optional and not required for MVP validation.

TypeScript planner OpenRouter mode requires:

```text
OFFICE_DSL_LLM_MODE=openrouter
OPENROUTER_API_KEY=<secret>
OPENROUTER_MODEL=<model>
```

Python verifier OpenRouter mode requires installing the verifier with the optional `openrouter` extra and setting `OPENROUTER_API_KEY`. This path was not tested in the offline MVP run.

## Documentation

- `docs/architecture.md` describes the MVP architecture, flows, roles, approvals, examples, and the decision not to use `project.sh` as an active bootstrap.
- `docs/research-migration-audit.md` verifies migration of historical research files to `research/`.
- `HANDOFF.md`, `VERSION.md`, and `CHANGELOG.md` describe the current release state and next steps.

## Final Validation Note

Final validation note: an earlier full Vitest run passed 15/15, but a later final rerun in this Codex session failed before test collection because local pnpm links in `node_modules` could not resolve `@vitest/utils`. No install was run after the user requested not to rerun install. Manual relink attempts were not committed because `node_modules` is ignored. The next operator should refresh dependencies with `corepack pnpm install --frozen-lockfile` and rerun the final validation.
