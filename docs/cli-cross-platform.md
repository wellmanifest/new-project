# Cross-Platform CLI

The `packages/cli` entry points are designed to run on both Windows and Linux without shell-specific wiring.

## Entry points

- `office-dsl` — existing Office DSL MVP CLI (`packages/cli/src/index.ts`).
- `well-manifest-intent` — canonical Intent/Contract CLI (`packages/cli/src/intent.ts`).

Both are TypeScript source files executed via `node --import tsx <file>`, so the Unix shebang is optional and ignored on Windows.

## Canonical `well-manifest-intent` commands

```bash
node --import tsx packages/cli/src/intent.ts version
node --import tsx packages/cli/src/intent.ts plan "Hire a backend developer for 12000 PLN per month"
node --import tsx packages/cli/src/intent.ts plan-file guidelines.md
node --import tsx packages/cli/src/intent.ts render contract.dsl.json
node --import tsx packages/cli/src/intent.ts testgen contract.dsl.json --write --out-dir generated
node --import tsx packages/cli/src/intent.ts codegen contract.dsl.json --write --out-dir generated
node --import tsx packages/cli/src/intent.ts verify contract.dsl.json
node --import tsx packages/cli/src/intent.ts approve contract.dsl.json Human1
node --import tsx packages/cli/src/intent.ts chat scenario-name-or-path
node --import tsx packages/cli/src/intent.ts example scenario-name-or-path
node --import tsx packages/cli/src/intent.ts recruitment scenario-name-or-path
```

All commands accept POSIX (`/`) and Windows (`\\`) separators, `file://` URLs, absolute paths, and scenario-name shortcuts resolved against the default `examples`, `examples-chat`, and `examples-recruitment` directories.

## Output modes

- `--json` — explicit structured JSON output (default).
- `--human` — key-value text output suitable for terminal review.

## Path normalization

`packages/cli/src/cross-platform.ts` provides helpers used by the canonical CLI:

- `normalizePathArgument` — converts `file://` URLs and mixed-separator paths into platform-correct paths.
- `fileUrlToPath` — decodes Windows file URLs with drive letters.
- `pathToImportUrl` — converts a path into a safe `file://` URL for dynamic imports.

## Windows support

A `project.bat` is provided with the same surface as `./project.sh`:

```cmd
project.bat typecheck
project.bat test
project.bat verify
```

Both scripts run pnpm via corepack and keep validation consistent across operating systems.

## Boundaries

- The CLI is deterministic and read-only over the DSL by default.
- `--write` only produces artifacts in the directory you specify.
- Canonical Intent/Contract commands are implemented in `packages/cli` but are not yet wired into the runtime approval gate or backend/UI flows.
