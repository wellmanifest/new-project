# Version

## Current Version

`0.7.1`

## Version Type

Patch artifact-format release over `0.7.0`.

This version changes generated `examples-chat` `.dsl` artifacts from JSON serialization to the project DSL text style used in `POLICY.md` and `CONTRIBUTING.md`. Runtime canonical approval APIs from `0.7.0` remain in place.

## Project Status

The repository contains a working offline Office DSL MVP, a repeatable scenario runner for the current example fixtures, executable chat-negotiation regression scenarios, a standalone canonical Intent/Contract DSL model package, an Office DSL to Intent/Contract migration path, minimal runtime canonical approval records, and CI wiring for the default verification workflow.

Current validated implementation scope:

- single-request Office DSL planning through mock planner,
- `office.dsl.v1` JSON validation,
- TypeScript runtime orchestration,
- deterministic policy checks,
- simple clarification questions,
- one-side Office action confirmation with plan hash,
- per-session canonical Intent/Contract DSL snapshot hash,
- minimal Human1/Human2 runtime approval records with party, hash, timestamp, verdict, active/invalidated status, and invalidation reason,
- bilateral current-hash approval detection in runtime APIs,
- approval invalidation after canonical DSL snapshot changes,
- mock dry-run execution,
- audit output with canonical approval metadata,
- CLI, backend API, static web demo for the current Office DSL flow,
- Python mock verifier package,
- canonical office example manifests with `in/` and `out/` folders,
- deterministic single-example and all-example runner,
- executable `examples-chat` scenarios for Human1/Human2 negotiation regression,
- line-by-line chat artifacts with party contract state, merged contract state, diffs, status, approvals, conflicts, and cancellation summaries,
- generated `.dsl` chat artifacts rendered as line-oriented editable DSL text, not JSON,
- final chat DSL/PDF/approval artifacts only after both parties approve the same current merged contract hash,
- root verification command,
- GitHub Actions workflow for `project.sh install` and `project.sh verify` on Windows and Linux,
- `intent-contract.dsl.v1` model package with formal fields, statuses, source references, canonical serialization, and stable hashing,
- deterministic `officeDslToIntentContractDsl` compatibility adapter with migration notes,
- expanded regression coverage for DSL validation, runtime controls, security policy, canonical approval records, CLI workflows, backend API workflows, file-backed store behavior, example runners, and chat negotiation behavior,
- documented Codex Windows sandbox `spawn EPERM` limitation for Vitest/Vite startup,
- TypeScript and Python tests for the current scope.

Target scope documented but not implemented:

- CLI/backend/web exposure for canonical Intent/Contract approval flows,
- production Human1/Human2 conversation workflow,
- planner population of field-level source traceability,
- contract and legal document renderers,
- JS/Node.js code generation,
- DSL-based test generation,
- TypeScript runtime integration with the Python verifier as a normal gating step.

## Included In 0.7.1

- Changed `intent-contract.dsl`, `party-contract.dsl`, `merged-contract.dsl`, `final-contract.dsl`, and `annex.dsl` outputs to line-oriented DSL text.
- Added `validateChatDslText` to reject JSON object/array syntax and unsupported DSL commands before `.dsl` artifacts are written.
- Documented the highlighting recommendation: keep `.dsl` as the project format and map it in editors to HCL/Terraform or generic config highlighting when useful.
- Kept machine comparison files as JSON: `scenario.json`, `summary.json`, `status.json`, expected summaries, and `approvals.json`.
- Updated package, app, verifier, and OpenAPI version metadata to `0.7.1`.

## Not Included In 0.7.1

- No CLI commands for canonical approvals.
- No backend/web Human1/Human2 approval UI.
- No production planner support for arbitrary conversation history.
- No legal contract renderer beyond the deterministic example PDF artifact.
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

- TypeScript runtime tests for canonical approval records and invalidation.
- Existing TypeScript and Python checks listed in the final task report.
- Office and chat example runners.
- Intent/Contract model and adapter tests.
- Reproduced the Codex Windows sandbox `spawn EPERM` limitation and used the approved escalated path for commands that require Node/Vite process creation in this environment.

Expected but not yet fully validated as release criteria:

- Online OpenRouter planner mode.
- Online LiteLLM/OpenRouter verifier mode.

## Versioning Policy Note

This pass uses a minor bump from `0.6.0` to `0.7.1` because it adds runtime-level canonical approval records and current-hash approval invalidation semantics.

A future production hardening task should define how root package metadata, package versions, OpenAPI metadata, `VERSION.md`, and `CHANGELOG.md` are kept in sync.
