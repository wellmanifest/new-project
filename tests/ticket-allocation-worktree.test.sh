#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
fixture_cache="$(mktemp -d "${TMPDIR:-/tmp}/new-project-ticket-allocation-worktree.test.XXXXXX")"
trap 'rm -rf "$fixture_cache"' EXIT INT TERM
fixture_cache="$(cd "$fixture_cache" && pwd -P)"
export TMPDIR="$fixture_cache"
export GIT_CEILING_DIRECTORIES="$fixture_cache${GIT_CEILING_DIRECTORIES:+:$GIT_CEILING_DIRECTORIES}"
python3 "$repo_root/tests/ticket-allocation-worktree.test.py"
