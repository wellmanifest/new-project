#!/usr/bin/env bash
# ticket-266: the installed wellman wheel must run the complete governance
# checker through every documented invocation, not only build successfully.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "== bundled modules match scripts/ =="
python3 packages/wellman/sync_bundled.py --check

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

echo "== build and install the wheel into a clean venv =="
# Build from a copy so setuptools leaves no build/ or egg-info changes behind.
cp -R packages/wellman "$TMP/src"
python3 -m pip wheel --quiet --no-deps --wheel-dir "$TMP/wheel" "$TMP/src"
python3 -m venv "$TMP/venv"
if [[ -x "$TMP/venv/bin/python" ]]; then
  PY="$TMP/venv/bin/python"
else
  PY="$TMP/venv/Scripts/python.exe"
fi
"$PY" -m pip install --quiet --disable-pip-version-check "$TMP"/wheel/*.whl

echo "== wellman --version reports the standard version =="
expected="wellman $(tr -d '[:space:]' < VERSION)"
actual="$(cd "$TMP" && "$PY" -m wellman --version)"
if [[ "$actual" != "$expected" ]]; then
  echo "expected '$expected', got '$actual'" >&2
  exit 1
fi

echo "== wellman check --json runs the bundled checker outside the source tree =="
status=0
(cd "$TMP" && "$PY" -m wellman check --root "$ROOT" \
  --manifest governance/manifest.hub.json --json) >"$TMP/report.json" 2>"$TMP/stderr.txt" || status=$?
if [[ "$status" -gt 1 ]] || grep -qE 'Traceback|ModuleNotFoundError' "$TMP/stderr.txt"; then
  cat "$TMP/stderr.txt" >&2
  echo "bundled checker crashed (exit $status)" >&2
  exit 1
fi
python3 - "$TMP/report.json" <<'PY'
import json
import sys

report = json.load(open(sys.argv[1], encoding="utf-8"))
missing = {"GOV-SYNC-001", "GOV-DECISION-002"} & {f["code"] for f in report["findings"]}
if missing:
    raise SystemExit(f"bundled checker is missing sibling modules: {sorted(missing)}")
PY

echo "== runtime releases never take the latest standard release =="
python3 - <<'PY2'
import re
from pathlib import Path

text = Path(".github/workflows/wellman-publish.yml").read_text(encoding="utf-8")
if not re.search(r'^\s+make_latest:\s*"?false"?\s*$', text, re.M):
    raise SystemExit("wellman-publish.yml must set make_latest: false on the GitHub Release")
PY2

echo "== adopter workflows run the wellman gate as the ci actor =="
python3 - <<'PY3'
import re
from pathlib import Path

for workflow in (
    "template/files/new-project-governance.workflow.yml",
    ".github/workflows/governance-gate-reusable.yml",
):
    text = Path(workflow).read_text(encoding="utf-8")
    calls = re.findall(r"wellman check\b(?:[^\n]*\\\n)*[^\n]*", text)
    if not calls or any("--actor ci" not in call for call in calls):
        raise SystemExit(f"{workflow}: every 'wellman check' must pass --actor ci")
PY3

echo "wellman package: PASS"
