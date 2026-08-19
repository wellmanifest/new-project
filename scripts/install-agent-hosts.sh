#!/usr/bin/env bash
# Materialize the host-agnostic new-project contract into a clone and/or
# user-level LLM host directories. Does not change package-manifest.json.

set -euo pipefail

usage() {
  cat <<'EOF'
Usage: ./scripts/install-agent-hosts.sh [options]

  --source DIR    Hub or already-populated checkout (default: this script's repo)
  --target DIR    Git clone that should receive host files and hooksPath
  --user          Also install user-level Cursor / Gemini / Claude pointers
  -h, --help      Show this help

At least one of --target or --user is required. --target defaults to the
current directory when it is a git work tree and --user was not the only
request.
EOF
}

SOURCE=""
TARGET=""
USER_INSTALL=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --source)
      [[ $# -ge 2 && -n "${2:-}" ]] || { echo "Missing value for --source" >&2; exit 2; }
      SOURCE="$2"
      shift 2
      ;;
    --target)
      [[ $# -ge 2 && -n "${2:-}" ]] || { echo "Missing value for --target" >&2; exit 2; }
      TARGET="$2"
      shift 2
      ;;
    --user)
      USER_INSTALL=true
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -z "$SOURCE" ]]; then
  SOURCE="$(cd "$script_dir/.." && pwd)"
fi
SOURCE="$(cd "$SOURCE" && pwd)"

if [[ -z "$TARGET" && "$USER_INSTALL" == false ]]; then
  if git rev-parse --show-toplevel >/dev/null 2>&1; then
    TARGET="$(git rev-parse --show-toplevel)"
  else
    echo "No --target and current directory is not a git work tree." >&2
    usage >&2
    exit 2
  fi
fi

require_source_file() {
  local rel="$1"
  if [[ ! -f "$SOURCE/$rel" ]]; then
    echo "Source file missing: $SOURCE/$rel" >&2
    exit 1
  fi
}

install_repo_files() {
  local dest="$1"
  dest="$(cd "$dest" && pwd)"
  if ! git -C "$dest" rev-parse --show-toplevel >/dev/null 2>&1; then
    echo "Target is not a git work tree: $dest" >&2
    exit 1
  fi

  require_source_file "GEMINI.md"
  require_source_file "CLAUDE.md"
  require_source_file ".cursor/rules/new-project-standard.mdc"
  require_source_file ".githooks/pre-commit"

  mkdir -p "$dest/.cursor/rules" "$dest/.githooks"
  cp -f "$SOURCE/GEMINI.md" "$dest/GEMINI.md"
  cp -f "$SOURCE/CLAUDE.md" "$dest/CLAUDE.md"
  cp -f "$SOURCE/.cursor/rules/new-project-standard.mdc" \
    "$dest/.cursor/rules/new-project-standard.mdc"
  cp -f "$SOURCE/.githooks/pre-commit" "$dest/.githooks/pre-commit"
  chmod +x "$dest/.githooks/pre-commit"
  git -C "$dest" config core.hooksPath .githooks
  echo "Installed host files and core.hooksPath=.githooks in $dest"
}

install_user_files() {
  local home="${HOME:-}"
  if [[ -z "$home" || ! -d "$home" ]]; then
    echo "HOME is not a directory; skipping --user" >&2
    return 1
  fi
  require_source_file "GEMINI.md"
  require_source_file "CLAUDE.md"
  require_source_file ".cursor/rules/new-project-standard.mdc"

  mkdir -p "$home/.cursor/rules" "$home/.gemini" "$home/.claude"
  cp -f "$SOURCE/.cursor/rules/new-project-standard.mdc" \
    "$home/.cursor/rules/new-project-standard.mdc"

  local marker="wellmanifest/new-project host contract"
  if [[ ! -f "$home/.gemini/GEMINI.md" ]] || ! grep -Fq "$marker" "$home/.gemini/GEMINI.md"; then
    cat > "$home/.gemini/GEMINI.md" <<EOF
# $marker

When the current repository has \`./project/new-ticket.sh\`, follow that
repository's \`GEMINI.md\` and \`AGENTS.md\`. Allocate tickets only through
that script. Never commit on main or a dirty primary checkout.
EOF
  fi
  if [[ ! -f "$home/.claude/CLAUDE.md" ]] || ! grep -Fq "$marker" "$home/.claude/CLAUDE.md"; then
    cat > "$home/.claude/CLAUDE.md" <<EOF
# $marker

When the current repository has \`./project/new-ticket.sh\`, follow that
repository's \`CLAUDE.md\` and \`AGENTS.md\`. Allocate tickets only through
that script. Never commit on main or a dirty primary checkout.
EOF
  fi
  echo "Installed user-level host pointers under $home/.cursor $home/.gemini $home/.claude"
}

if [[ -n "$TARGET" ]]; then
  install_repo_files "$TARGET"
fi
if [[ "$USER_INSTALL" == true ]]; then
  install_user_files
fi
