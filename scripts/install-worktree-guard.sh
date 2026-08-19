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
  --interval SECONDS Timer period for --workspace (default 300)
  --enable           systemctl --user enable --now the generated units
  --watch            Print the foreground watch command for the target
  -h, --help         Show this help

--target installs:
  worktree-guard.yaml
  .governance/worktree_overlap_check.py
  .governance/worktree_guard.py
  .governance/error/GOV-WORKTREE-OVERLAP.md
  .githooks/pre-commit-worktree-guard   (chainable; does not replace pre-commit)

--workspace installs:
  $XDG_DATA_HOME/worktree-guard/{worktree_overlap_check.py,worktree_guard.py,worktree-guard.yaml}
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
require scripts/worktree_guard.py
require worktree-guard.yaml
require error/GOV-WORKTREE-OVERLAP.md

install_repo() {
  local target="$1"
  mkdir -p "$target/.governance/error" "$target/.githooks"
  install -m 0755 "$SOURCE/scripts/worktree_overlap_check.py" "$target/.governance/worktree_overlap_check.py"
  install -m 0755 "$SOURCE/scripts/worktree_guard.py" "$target/.governance/worktree_guard.py"
  install -m 0644 "$SOURCE/worktree-guard.yaml" "$target/worktree-guard.yaml"
  install -m 0644 "$SOURCE/error/GOV-WORKTREE-OVERLAP.md" "$target/.governance/error/GOV-WORKTREE-OVERLAP.md"

  cat > "$target/.githooks/pre-commit-worktree-guard" <<'HOOK'
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
HOOK
  chmod 0755 "$target/.githooks/pre-commit-worktree-guard"
  echo "repo:      installed into $target"
}

install_workspace() {
  local workspace="$1"
  local instance
  instance="$(systemd-escape --path "$workspace")"

  mkdir -p "$DATA_HOME" "$STATE_HOME" "$UNIT_HOME"
  install -m 0755 "$SOURCE/scripts/worktree_overlap_check.py" "$DATA_HOME/worktree_overlap_check.py"
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
Description=Worktree overlap scan when %f/.worktrees changes

[Path]
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
