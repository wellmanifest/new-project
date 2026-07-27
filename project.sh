#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

export PIP_DISABLE_PIP_VERSION_CHECK=1

usage() {
  cat <<'USAGE'
Usage: ./project.sh <command> [args]

On Windows run project.bat with the same commands.

Project commands:
  install             Install workspace dependencies from pnpm lockfile
  typecheck           Run TypeScript project references check
  lint                Run ESLint on source and tests
  format              Check formatting with Prettier
  test                Run TypeScript tests
  python-test         Run Python verifier tests
  example <name>      Run one example scenario
  examples            Run all example scenarios
  example-chat <name> Run one chat negotiation example
  examples-chat       Run all chat negotiation examples
  example-recruitment <name> Run one recruitment example
  examples-recruitment Run all recruitment examples
  examples-index [file] Build one Markdown index for all example inputs, expected files and outputs
  makedocs           Generate README include menu and documentation indexes
  verify              Run typecheck, lint, format, tests, examples, and git diff check
  system-check        Run the full functional system test suite
  dev-backend         Start backend and static web demo
  legacy-analyze      Run the historical network-heavy analysis workflow

Notes:
  The default command prints this help. The old network-installing workflow is
  intentionally behind 'legacy-analyze' so routine validation stays explicit.
USAGE
}

pnpm_run() {
  corepack pnpm run "$@"
}

case "${1:-help}" in
  help|-h|--help)
    usage
    ;;
  install)
    corepack pnpm install --frozen-lockfile
    ;;
  typecheck)
    pnpm_run typecheck
    ;;
  lint)
    pnpm_run lint
    ;;
  format|format-check)
    pnpm_run format
    ;;
  test)
    pnpm_run test
    ;;
  python-test)
    pnpm_run python:test
    ;;
  example)
    shift
    pnpm_run example:run -- "$@"
    ;;
  examples)
    pnpm_run examples:run
    ;;
  example-chat)
    shift
    pnpm_run example-chat:run -- "$@"
    ;;
  examples-chat)
    pnpm_run examples-chat:run
    ;;
  example-recruitment)
    shift
    pnpm_run example-recruitment:run -- "$@"
    ;;
  examples-recruitment)
    pnpm_run examples-recruitment:run
    ;;
  examples-index)
    shift
    pnpm_run examples:index -- "$@"
    ;;
  makedocs)
    pnpm_run docs:generate
    ;;
  verify)
    pnpm_run verify
    ;;
  system-check|functional-test|functional-tests)
    pnpm_run system:check
    ;;
  dev-backend)
    pnpm_run dev:backend
    ;;
  legacy-analyze)
    VENV="venv"
    PIP="$VENV/bin/pip"

    if [ ! -f "$PIP" ]; then
      echo "Creating virtual environment..."
      python3 -m venv "$VENV"
    fi

    "$PIP" install --upgrade pip -q 2>/dev/null || true
    "$PIP" install regix --upgrade --quiet
    "$PIP" install prefact --upgrade --quiet
    "$PIP" install vallm --upgrade --quiet
    "$PIP" install redup --upgrade --quiet
    "$PIP" install glon --upgrade --quiet
    "$PIP" install code2logic --upgrade --quiet
    "$PIP" install code2llm --upgrade --quiet
    "$VENV/bin/code2llm" ./ -f all -o ./project --no-chunk --exclude '*.md'
    "$VENV/bin/redup" scan . --format toon --output ./project --ext .mjs,.js,.php,.sh
    "$VENV/bin/prefact" -a -e "examples/**"

    "$PIP" install doql --upgrade --quiet
    "$VENV/bin/doql" adopt . --format less --output app.doql.less --force

    "$PIP" install sumd --upgrade --quiet
    "$VENV/bin/sumd" .
    "$VENV/bin/sumr" .

    if [ -d "../goal/goal" ] && [ -f "../goal/pyproject.toml" ]; then
      pip install -e ../goal
      "$PIP" install -e ../goal --quiet
    else
      pip install -U goal
      "$PIP" install goal --upgrade --quiet
    fi

    if [ -x "./tree.sh" ]; then
      bash ./tree.sh
    elif command -v tree >/dev/null 2>&1; then
      tree -L 2
    else
      echo "Skipping tree snapshot: ./tree.sh not found and 'tree' is not installed."
    fi
    ;;
  *)
    echo "Unknown project command: $1" >&2
    usage >&2
    exit 2
    ;;
esac
