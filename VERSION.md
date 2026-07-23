# Version

## Current Version

`0.1.0`

## Project Status

First working offline MVP. The validated scope covers single-request Office DSL planning, JSON DSL validation, TypeScript runtime orchestration, mock execution, audit output, Python mock verification, CLI, backend API, static web demo, and static example validation.

## Version Scope

Included in `0.1.0`:

- Offline mock planner for single natural-language office commands.
- `office.dsl.v1` JSON DSL model.
- Parser, structural validator, and human-readable DSL renderer.
- TypeScript runtime with state machine, policy engine, action registry, dry-run execution, confirmation handling, answer handling, plan hashing, and audit records.
- CLI, backend API, and static web demo.
- Python verifier in mock mode.
- Mock data and six example scenarios.
- TypeScript and Python tests.

Not included in `0.1.0`:

- Full Intent/Contract DSL.
- Bilateral contract approval.
- Contract document generation.
- Conversation/file-guidelines planner modes.
- Dedicated example diff runner.
- Verified OpenRouter/LiteLLM execution.

## Runtime Compatibility

Validated in this workspace:

- Windows: validated.
- Node.js: `24.18.0` during Vitest runs.
- pnpm: `9.12.0` through Corepack, matching `packageManager`.
- TypeScript: `5.7.3`.
- Vitest: `3.0.4`.
- Python: tests ran on Python `3.14`; verifier package declares `>=3.11`.

Expected but not validated in this run:

- Linux.
- Other supported Node.js versions.
- Python 3.11-3.13.

## Test Results

Latest validated results in this task:

- Targeted Vitest runtime: 6 tests passed in 10.11 s.
- Targeted Vitest security: 3 tests passed in 7.07 s.
- Targeted Vitest E2E: 2 tests passed in 9.12 s.
- Full Vitest: 15 tests passed across 4 files in 18.18 s.
- Python verifier: 3 tests passed in 10.84 s, with one pytest cache warning.
- Example validation: 6 example folders validated through CLI expected DSL plus JSON parsing of expected plan and verification files.
- Typecheck: confirmed by user before this pass and re-run during final validation.

## Known Limitations

- Validated planner behavior is mock-based and pattern-based.
- The Python verifier is a mock semantic verifier, not a full proof of NL/DSL equivalence.
- The web UI is a demo surface, not a complete production frontend.
- Runtime confirmation is one-side confirmation, not bilateral contract approval.
- Example validation does not yet regenerate and diff actual outputs.

## Next Stage

Continue with TODO Etap 1 and Etap 2 for the full Intent/Contract DSL scope:

1. Define the complete MVP use-case requirements for single-command, two-party conversation, and text-guidelines flows.
2. Specify the full Contract/Intent DSL model and status semantics.
3. Extend examples into the planned `scenario.json` plus `in/` and `out/` folder format.
4. Build an example runner that regenerates outputs and reports diffs.

## Final Validation Note

Final validation note: an earlier full Vitest run passed 15/15, but a later final rerun in this Codex session failed before test collection because local pnpm links in `node_modules` could not resolve `@vitest/utils`. No install was run after the user requested not to rerun install. Manual relink attempts were not committed because `node_modules` is ignored. The next operator should refresh dependencies with `corepack pnpm install --frozen-lockfile` and rerun the final validation.

