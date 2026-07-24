# Version

## Current Version

`0.6.0`

## Version Type

Minor fixture-and-runner release over `0.5.0`.

This version adds executable Human1/Human2 chat negotiation examples with deterministic line-by-line artifacts, bilateral approval-by-current-hash checks, cancellation coverage, and integration with the root verification workflow. It does not turn the example runner into the production planner/runtime implementation.

## Project Status

The repository contains a working offline Office DSL MVP, a repeatable scenario runner for the current example fixtures, executable chat-negotiation regression scenarios, a standalone canonical Intent/Contract DSL model package, an Office DSL to Intent/Contract migration path, and CI wiring for the default verification workflow.

Current validated implementation scope:

- single-request Office DSL planning through mock planner,
- `office.dsl.v1` JSON validation,
- TypeScript runtime orchestration,
- deterministic policy checks,
- simple clarification questions,
- one-side confirmation with plan hash,
- mock dry-run execution,
- audit output,
- CLI, backend API, static web demo,
- Python mock verifier package,
- canonical office example manifests with `in/` and `out/` folders,
- deterministic single-example and all-example runner,
- executable `examples-chat` scenarios for Human1/Human2 negotiation regression,
- line-by-line chat artifacts with party contract state, merged contract state, diffs, status, approvals, conflicts, and cancellation summaries,
- final chat DSL/PDF/approval artifacts only after both parties approve the same current merged contract hash,
- root verification command,
- GitHub Actions workflow for `project.sh install` and `project.sh verify` on Windows and Linux,
- `intent-contract.dsl.v1` model package with formal fields, statuses, source references, canonical serialization, and stable hashing,
- deterministic `officeDslToIntentContractDsl` compatibility adapter with migration notes,
- expanded regression coverage for DSL validation, runtime controls, security policy, CLI workflows, backend API workflows, file-backed store behavior, example runners, and chat negotiation behavior,
- documented Codex Windows sandbox `spawn EPERM` limitation for Vitest/Vite startup,
- TypeScript and Python tests for the current scope.

Target scope documented but not implemented:

- runtime use of canonical Intent/Contract snapshots for approvals,
- production Human1/Human2 bilateral approval runtime flow,
- planner population of field-level source traceability,
- contract and legal document renderers,
- JS/Node.js code generation,
- DSL-based test generation,
- TypeScript runtime integration with the Python verifier as a normal gating step.

## Included In 0.6.0

- Added `examples-chat/01-short-agreement`.
- Added `examples-chat/02-long-negotiation-agreement`.
- Added `examples-chat/03-short-conversation-cancelled`.
- Added `examples-chat/04-long-negotiation-cancelled`.
- Added `scenario.json`, `chat.txt`, and `out/expected.summary.json` for every chat scenario.
- Added deterministic line-by-line chat processing in `@office-dsl/example-runner`.
- Added generated per-event artifacts: `prompt.txt`, `intent-contract.dsl`, `party-contract.dsl`, `merged-contract.dsl`, `diff.md`, and `status.json`.
- Added final agreed artifacts: `final-contract.dsl`, `contract.md`, `contract.pdf`, `approvals.json`, `diff-summary.md`, and `annex.dsl`.
- Added cancellation behavior that prevents `final-contract.dsl`, `contract.pdf`, and `approvals.json` from being created.
- Added approval invalidation after merged contract hash changes.
- Added `example-chat:run`, `examples-chat:run`, `project.sh example-chat`, and `project.sh examples-chat` commands.
- Added chat example execution to the root `verify` command.
- Added regression tests for parsing, discovery, merging, conflicts, diffs, approval invalidation, finalization, cancellation, and all four scenario outcomes.
- Updated package, app, verifier, and OpenAPI version metadata to `0.6.0`.

## Not Included In 0.6.0

- No production planner support for arbitrary conversation history.
- No backend/web Human1/Human2 approval UI.
- No legal contract renderer beyond the deterministic example PDF artifact.
- No canonical Intent/Contract runtime approval migration from the Office DSL runtime flow.
- No JS/Node.js code generator.
- No DSL-based test generator.

## Runtime Compatibility Notes

Declared by the repository:

- pnpm: `9.12.0` through `packageManager`.
- TypeScript: `5.7.3`.
- Vitest: `3.0.4`.
- Python verifier: `>=3.11`.
- CI Node.js: `22`.
- CI Python: `3.11`.

Validated in this pass:

- Chat example runner over all four `examples-chat` scenarios.
- TypeScript regression tests for chat negotiation semantics.
- Existing TypeScript and Python checks listed in the final task report.
- Intent/Contract model and adapter tests.
- Example runner with Python verifier in mock mode.
- Reproduced the Codex Windows sandbox `spawn EPERM` limitation and used the approved escalated path for commands that require Node/Vite process creation in this environment.

Expected but not yet fully validated as release criteria:

- Online OpenRouter planner mode.
- Online LiteLLM/OpenRouter verifier mode.

## Versioning Policy Note

This pass uses a minor bump from `0.5.0` to `0.6.0` because it adds executable chat negotiation fixture infrastructure, runner commands, approval-hash finalization checks, and verification coverage.

A future production hardening task should define how root package metadata, package versions, OpenAPI metadata, `VERSION.md`, and `CHANGELOG.md` are kept in sync.
