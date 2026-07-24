# Codex Sandbox Vitest Limitation

## Status

The default test suite is valid and passes outside the restricted Codex filesystem sandbox with:

```powershell
corepack pnpm run verify
```

Inside the current Codex Windows sandbox, direct Vitest startup can fail before test collection because the sandbox denies process creation from Node/Vite internals.

## Reproduction

Command:

```powershell
corepack pnpm test
```

Observed failure in the managed Codex sandbox:

```text
Error: spawn EPERM
  at ChildProcess.spawn node:internal/child_process
  at Object.execFile node:child_process
  at optimizeSafeRealPathSync .../vite/dist/node/chunks/...
```

A TypeScript or ESM `vitest.config.*` file makes startup fail even earlier because Vite bundles the config through esbuild, which also attempts process creation and receives `spawn EPERM`.

Changing Vitest pools does not remove the sandbox dependency in this environment:

```powershell
vitest run --dir tests --pool vmThreads
```

This still reaches Vite path resolution that calls `child_process.execFile` on Windows.

## Repository Mitigation

The root test scripts avoid project-wide scanning and generated/cache directories:

```json
{
  "test": "vitest run --dir tests --exclude **/.pytest_cache/** --exclude verifier/**",
  "test:e2e": "vitest run tests/e2e.test.ts --exclude **/.pytest_cache/** --exclude verifier/**"
}
```

This prevents the earlier `.pytest_cache` scandir failure and keeps normal verification deterministic outside the restricted sandbox.

## Operational Rule

When running inside this Codex sandbox, use escalated execution for the full verification command:

```powershell
corepack pnpm run verify
```

The command still performs the same repository checks: typecheck, lint, format, Vitest, Python verifier tests, example runner, and `git diff --check`.
