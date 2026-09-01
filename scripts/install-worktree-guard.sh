#!/usr/bin/env bash
# Install the worktree overlap guard.
#
# Two installation shapes, because the failure they catch lives at two levels:
#
#   --target DIR     per-repository, fail-closed at the moment of writing
#                    (pre-commit chain hook + .governance copies + pyqual stage)
#   --workspace DIR  per-workspace, scheduled, catches agents that overlap long
#                    before anyone reaches a commit (systemd --user timer +
#                    .worktrees path unit)
#
# Never rewrites package-manifest.json or an existing .githooks/pre-commit.

set -euo pipefail

DATA_HOME="${XDG_DATA_HOME:-$HOME/.local/share}/worktree-guard"
STATE_HOME="${XDG_STATE_HOME:-$HOME/.local/state}/worktree-guard"
UNIT_HOME="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user"

usage() {
  cat <<'EOF'
Usage: ./scripts/install-worktree-guard.sh [options]

  --source DIR       Hub or populated checkout (default: this script's repo)
  --target DIR       Git clone that should receive the in-repo guard
  --workspace DIR    Workspace root to scan on a schedule (e.g. ~/github/subactor)
  --pyqual FILE      pyqual.yaml to extend with the worktree-overlap stage
  --wire-hook        Chain the fragment into the target's pre-commit hook
  --interval SECONDS Timer period for --workspace (default 300)
  --enable           systemctl --user enable --now the generated units
  --watch            Print the foreground watch command for the target
  -h, --help         Show this help

--target installs:
  worktree-guard.yaml
  .governance/worktree_path_check.py
  .governance/worktree_overlap_check.py
  .governance/ticket_activity.py
  .governance/worktree_guard.py
  .governance/error/GOV-WORKTREE-OVERLAP.md
  <effective hooks dir>/pre-commit-worktree-guard
      The directory comes from `git rev-parse --git-path hooks`, so it honours
      core.hooksPath. Chainable; an existing pre-commit is never replaced.
      With --wire-hook the call is added to pre-commit (created if absent).

--workspace installs:
  $XDG_DATA_HOME/worktree-guard/{worktree_path_check.py,worktree_overlap_check.py,ticket_activity.py,worktree_guard.py,worktree-guard.yaml}
  $XDG_CONFIG_HOME/systemd/user/worktree-guard@.{service,timer,path}
  reports under $XDG_STATE_HOME/worktree-guard/
EOF
}

SOURCE=""
TARGET=""
WORKSPACE=""
PYQUAL=""
INTERVAL=300
ENABLE=false
WATCH=false
WIRE_HOOK=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --source|--target|--workspace|--pyqual|--interval)
      [[ $# -ge 2 && -n "${2:-}" ]] || { echo "Missing value for $1" >&2; exit 2; }
      case "$1" in
        --source) SOURCE="$2" ;;
        --target) TARGET="$2" ;;
        --workspace) WORKSPACE="$2" ;;
        --pyqual) PYQUAL="$2" ;;
        --interval) INTERVAL="$2" ;;
      esac
      shift 2
      ;;
    --enable) ENABLE=true; shift ;;
    --wire-hook) WIRE_HOOK=true; shift ;;
    --watch) WATCH=true; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
[[ -n "$SOURCE" ]] || SOURCE="$(cd "$script_dir/.." && pwd)"
SOURCE="$(cd "$SOURCE" && pwd)"

if [[ -z "$TARGET" && -z "$WORKSPACE" && -z "$PYQUAL" ]]; then
  echo "One of --target, --workspace or --pyqual is required" >&2
  usage >&2
  exit 2
fi

if ! [[ "$INTERVAL" =~ ^[0-9]+$ ]] || (( INTERVAL < 5 )); then
  echo "--interval must be an integer of at least 5 seconds" >&2
  exit 2
fi

require() {
  [[ -f "$SOURCE/$1" ]] || { echo "Source file missing: $SOURCE/$1" >&2; exit 1; }
}
require scripts/worktree_overlap_check.py
require subprojects/worktrees/conformance.py
require scripts/ticket_activity.py
require scripts/worktree_guard.py
require worktree-guard.yaml
require error/GOV-WORKTREE-OVERLAP.md

repair_legacy_unreachable_guard() {
  local hook="$1"
  local staged_hook
  local status
  staged_hook="$(mktemp "${hook}.XXXXXX")"
  if awk '
    function normalized(value) {
      sub(/^[[:space:]]+/, "", value)
      sub(/[[:space:]]+$/, "", value)
      return value
    }
    {
      lines[NR] = $0
      text = normalized($0)
      if (text != "" && text !~ /^#/) {
        effective_count += 1
        effective_line[effective_count] = NR
        effective_text[effective_count] = text
        if (index(text, "pre-commit-worktree-guard") > 0) {
          guard_count += 1
          guard_effective = effective_count
          guard_line = NR
        }
      }
    }
    END {
      legacy_comment = "# worktree overlap guard (wellmanifest/new-project) - keep this last"
      if (guard_count != 1 || guard_effective != effective_count || guard_line != NR) exit 3
      if (effective_count < 2 || effective_text[effective_count - 1] != "exit 0") exit 3
      exit_line = effective_line[effective_count - 1]
      comment_count = 0
      for (line = exit_line + 1; line < guard_line; line += 1) {
        text = normalized(lines[line])
        if (text == "") continue
        if (text == legacy_comment) {
          comment_count += 1
          continue
        }
        exit 3
      }
      if (comment_count != 1) exit 3
      for (line = 1; line <= exit_line; line += 1) {
        if (line == exit_line) {
          print ""
          print legacy_comment
          print lines[guard_line]
        }
        print lines[line]
      }
    }
  ' "$hook" > "$staged_hook"; then
    chmod 0755 "$staged_hook"
    mv "$staged_hook" "$hook"
    echo "hooks:     repaired unreachable pre-commit guard call"
    return 0
  else
    status=$?
    rm -f "$staged_hook"
    if [[ "$status" -eq 3 ]]; then
      return 1
    fi
    echo "hooks:     failed to inspect existing pre-commit (awk exit $status)" >&2
    return "$status"
  fi
}

install_repo() {
  local target="$1"
  # Ask git where it will actually look. Writing to a hard-coded .githooks/
  # installs a hook that never runs whenever core.hooksPath says otherwise.
  local hooks_dir
  hooks_dir="$(cd "$target" && git rev-parse --git-path hooks)"
  [[ "$hooks_dir" == /* ]] || hooks_dir="$target/$hooks_dir"

  mkdir -p "$target/.governance/error" "$hooks_dir"
  install -m 0755 "$SOURCE/subprojects/worktrees/conformance.py" "$target/.governance/worktree_path_check.py"
  install -m 0755 "$SOURCE/scripts/worktree_overlap_check.py" "$target/.governance/worktree_overlap_check.py"
  install -m 0755 "$SOURCE/scripts/ticket_activity.py" "$target/.governance/ticket_activity.py"
  install -m 0755 "$SOURCE/scripts/worktree_guard.py" "$target/.governance/worktree_guard.py"
  install -m 0644 "$SOURCE/worktree-guard.yaml" "$target/worktree-guard.yaml"
  install -m 0644 "$SOURCE/error/GOV-WORKTREE-OVERLAP.md" "$target/.governance/error/GOV-WORKTREE-OVERLAP.md"

  cat > "$hooks_dir/pre-commit-worktree-guard" <<'HOOK'
#!/usr/bin/env bash
# Chainable pre-commit fragment. Call it from .githooks/pre-commit; it is not
# a replacement for that hook and never edits it.
set -euo pipefail
root="$(git rev-parse --show-toplevel)"
for runner in "$root/.governance/worktree_guard.py" "$root/scripts/worktree_guard.py"; do
  if [[ -f "$runner" ]]; then
    exec python3 "$runner" --root "$root" --once
  fi
done
# Reaching here means the hook is wired but its runner is gone. Exiting zero
# would leave a gate that looks installed and enforces nothing - observed twice
# in one day after an untracked copy was cleaned away. Fail closed and say why.
echo "worktree-guard: the hook is wired but worktree_guard.py is missing." >&2
echo "  Reinstall it, or remove this hook if the guard is no longer wanted:" >&2
echo "    ./scripts/install-worktree-guard.sh --target $root --wire-hook" >&2
exit 1
HOOK
  chmod 0755 "$hooks_dir/pre-commit-worktree-guard"
  echo "repo:      installed into $target"
  echo "hooks:     $hooks_dir"
  case "$hooks_dir" in
    */.git/hooks)
      echo "hooks:     WARNING this directory is not tracked, so the hook is"
      echo "hooks:     machine-local. Set core.hooksPath to a tracked directory"
      echo "hooks:     to share it: git -C $target config core.hooksPath .githooks"
      ;;
  esac

  local hook="$hooks_dir/pre-commit"
  if [[ "$WIRE_HOOK" != true ]]; then
    if [[ -f "$hook" ]] && grep -Fq pre-commit-worktree-guard "$hook"; then
      echo "hooks:     pre-commit already calls the guard"
    else
      echo "hooks:     not wired. Re-run with --wire-hook, or add to $hook:"
      echo '             "$(git rev-parse --show-toplevel)"/'"$(basename "$hooks_dir")"'/pre-commit-worktree-guard'
    fi
    return
  fi

  if [[ -f "$hook" ]] && grep -Fq pre-commit-worktree-guard "$hook"; then
    if repair_legacy_unreachable_guard "$hook"; then
      return
    fi
    echo "hooks:     pre-commit already calls the guard, left unchanged"
    return
  fi
  if [[ ! -f "$hook" ]]; then
    cat > "$hook" <<'PRECOMMIT'
#!/usr/bin/env bash
set -euo pipefail
PRECOMMIT
    chmod 0755 "$hook"
    echo "hooks:     created $hook"
  else
    echo "hooks:     appending to the existing $hook"
  fi
  # Keep the fragment last so an earlier `exec` in a hand-written hook is not
  # silently bypassed; the fragment itself execs, so nothing may follow it.
  # A final explicit success is the one safe exception: appending after
  # `exit 0` creates dead code, so insert immediately before that exact final
  # effective command and preserve the exit after the chain.
  local terminal_success_line
  terminal_success_line="$(awk '
    {
      text = $0
      sub(/^[[:space:]]+/, "", text)
      sub(/[[:space:]]+$/, "", text)
      if (text != "" && text !~ /^#/) {
        last_line = NR
        last_text = text
      }
    }
    END {
      if (last_text == "exit 0") print last_line
    }
  ' "$hook")"
  if [[ -n "$terminal_success_line" ]]; then
    local staged_hook
    staged_hook="$(mktemp "${hook}.XXXXXX")"
    awk -v insertion="$terminal_success_line" '
      NR == insertion {
        print ""
        print "# worktree overlap guard (wellmanifest/new-project) - keep this last"
        print "\"$(dirname \"${BASH_SOURCE[0]}\")/pre-commit-worktree-guard\""
      }
      { print }
    ' "$hook" > "$staged_hook"
    chmod 0755 "$staged_hook"
    mv "$staged_hook" "$hook"
  else
    cat >> "$hook" <<'CHAIN'

# worktree overlap guard (wellmanifest/new-project) - keep this last
"$(dirname "${BASH_SOURCE[0]}")/pre-commit-worktree-guard"
CHAIN
  fi
  echo "hooks:     wired $hook"
}

install_workspace() {
  local workspace="$1"
  local instance
  instance="$(systemd-escape --path "$workspace")"

  mkdir -p "$DATA_HOME" "$STATE_HOME" "$UNIT_HOME"
  install -m 0755 "$SOURCE/subprojects/worktrees/conformance.py" "$DATA_HOME/worktree_path_check.py"
  install -m 0755 "$SOURCE/scripts/worktree_overlap_check.py" "$DATA_HOME/worktree_overlap_check.py"
  install -m 0755 "$SOURCE/scripts/ticket_activity.py" "$DATA_HOME/ticket_activity.py"
  install -m 0755 "$SOURCE/scripts/worktree_guard.py" "$DATA_HOME/worktree_guard.py"
  install -m 0644 "$SOURCE/worktree-guard.yaml" "$DATA_HOME/worktree-guard.yaml"
  # A workspace root is usually not a repository, so the units point the runner
  # at the checker explicitly instead of hoping for scripts/ or .governance/.

  cat > "$UNIT_HOME/worktree-guard@.service" <<SERVICE
[Unit]
Description=Worktree overlap scan for %f
Documentation=https://github.com/wellmanifest/new-project/blob/main/docs/WORKTREE_GUARD.md

[Service]
Type=oneshot
# SuccessExitStatus keeps a *finding* from being reported as a unit failure:
# the report file carries the verdict, the unit only carries "did it run".
SuccessExitStatus=0 1
ExecStart=/usr/bin/env python3 $DATA_HOME/worktree_guard.py \\
  --root %f --config $DATA_HOME/worktree-guard.yaml \\
  --checker $DATA_HOME/worktree_overlap_check.py \\
  --once --format json --report $STATE_HOME/%i.json
SERVICE

  cat > "$UNIT_HOME/worktree-guard@.timer" <<TIMER
[Unit]
Description=Periodic worktree overlap scan for %f

[Timer]
OnBootSec=2min
OnUnitActiveSec=${INTERVAL}s
AccuracySec=15s
Unit=worktree-guard@%i.service

[Install]
WantedBy=timers.target
TIMER

  cat > "$UNIT_HOME/worktree-guard@.path" <<PATHUNIT
[Unit]
Description=Worktree overlap scan when %f worktree roots change

[Path]
PathModified=%f/worktrees
PathModified=%f/.worktrees
Unit=worktree-guard@%i.service

[Install]
WantedBy=paths.target
PATHUNIT

  echo "workspace: units written for $workspace (instance $instance)"
  echo "workspace: report path $STATE_HOME/$instance.json"
  if [[ "$ENABLE" == true ]]; then
    systemctl --user daemon-reload
    systemctl --user enable --now "worktree-guard@$instance.timer"
    systemctl --user enable --now "worktree-guard@$instance.path"
    echo "workspace: enabled worktree-guard@$instance.{timer,path}"
  else
    echo "workspace: enable with"
    echo "  systemctl --user daemon-reload"
    echo "  systemctl --user enable --now worktree-guard@$instance.timer"
    echo "  systemctl --user enable --now worktree-guard@$instance.path"
  fi
}

install_pyqual() {
  local config="$1"
  [[ -f "$config" ]] || { echo "pyqual config not found: $config" >&2; exit 1; }
  # Textual insert, then re-parse and diff the parse trees. If the file does not
  # have the expected shape the original is left byte-identical and the snippet
  # is printed instead: silently reshaping someone's pipeline is worse than a
  # manual paste.
  python3 - "$config" "$SOURCE/scripts/worktree_guard.py" <<'PYQUAL'
import copy
import json
import re
import subprocess
import sys
from pathlib import Path

config_path = Path(sys.argv[1])
runner = sys.argv[2]
snippet = json.loads(
    subprocess.run(
        [sys.executable, runner, "--print-pyqual-stage"],
        capture_output=True, text=True, check=True,
    ).stdout
)
tool = snippet["custom_tools"][0]
stage = snippet["stages"][0]

def fallback(reason: str) -> None:
    print(f"pyqual:    not modified ({reason}); add this under pipeline: manually")
    print(json.dumps(snippet, indent=2, sort_keys=True))
    raise SystemExit(0)

try:
    import yaml
except ImportError:
    fallback("PyYAML is not installed")

original = config_path.read_text(encoding="utf-8")
before = yaml.safe_load(original)
pipeline = (before or {}).get("pipeline")
if not isinstance(pipeline, dict):
    fallback("no pipeline: mapping")
if not isinstance(pipeline.get("custom_tools"), list) or not isinstance(pipeline.get("stages"), list):
    fallback("pipeline.custom_tools / pipeline.stages are not both lists")
if any(isinstance(item, dict) and item.get("name") == tool["name"] for item in pipeline["custom_tools"]):
    print("pyqual:    already present, left unchanged")
    raise SystemExit(0)

def block(key: str, value: dict) -> str:
    body = yaml.safe_dump([value], default_flow_style=False, sort_keys=False, indent=2)
    return "".join(f"    {line}\n" if line.strip() else "\n" for line in body.splitlines())

text = original
for key, value in (("custom_tools", tool), ("stages", stage)):
    match = re.search(rf"^(\s*){key}:[ \t]*$", text, re.M)
    if match is None:
        fallback(f"cannot locate the {key}: key")
    insert_at = match.end() + 1
    text = text[:insert_at] + block(key, value) + text[insert_at:]

after = yaml.safe_load(text)
expected = copy.deepcopy(before)
expected["pipeline"]["custom_tools"] = [tool] + expected["pipeline"]["custom_tools"]
expected["pipeline"]["stages"] = [stage] + expected["pipeline"]["stages"]
if after != expected:
    fallback("the edited file did not parse to the expected structure")

config_path.write_text(text, encoding="utf-8")
print(f"pyqual:    added worktree-overlap stage to {config_path}")
PYQUAL
}

[[ -n "$TARGET" ]] && install_repo "$(cd "$TARGET" && pwd)"
[[ -n "$WORKSPACE" ]] && install_workspace "$(cd "$WORKSPACE" && pwd)"
[[ -n "$PYQUAL" ]] && install_pyqual "$PYQUAL"

if [[ -n "$TARGET" ]]; then
  target_abs="$(cd "$TARGET" && pwd)"
  echo "run:       python3 $target_abs/.governance/worktree_guard.py --root $target_abs --once"
  if [[ "$WATCH" == true ]]; then
    echo "watch:     python3 $target_abs/.governance/worktree_guard.py --root $target_abs --watch --interval 60"
  fi
fi
exit 0
