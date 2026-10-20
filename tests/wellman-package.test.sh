#!/usr/bin/env bash
# ticket-266: the installed wellman wheel must run the complete governance
# checker through every documented invocation, not only build successfully.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "== installed build prerequisites (no downloads from candidate tests) =="
python3 - <<'PYBUILD'
from importlib.metadata import PackageNotFoundError, version

try:
    setuptools_version = version("setuptools")
    wheel_version = version("wheel")
    if int(setuptools_version.split(".", 1)[0]) < 68:
        raise ValueError("setuptools>=68.0 required")
except (PackageNotFoundError, ValueError) as error:
    raise SystemExit(
        "WELLMAN-BUILD-TOOLS-MISSING: preinstall setuptools>=68.0 and wheel "
        "in the CI runtime before running this offline regression"
    ) from error
print(f"Using installed setuptools {setuptools_version}, wheel {wheel_version}")
PYBUILD

echo "== bundled modules match scripts/ =="
python3 packages/wellman/sync_bundled.py --check

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

echo "== build and install the wheel into a clean venv =="
# Build from a copy so setuptools leaves no build/ or egg-info changes behind.
cp -R packages/wellman "$TMP/src"
# The independently provisioned runtime already owns these build tools. Build
# isolation would create a fresh environment and try PyPI inside network-none
# candidate execution, even when the approved tools are installed here.
python3 -m pip wheel --quiet --no-index --no-deps --no-build-isolation \
  --wheel-dir "$TMP/wheel" "$TMP/src"
python3 -m venv "$TMP/venv"
if [[ -x "$TMP/venv/bin/python" ]]; then
  PY="$TMP/venv/bin/python"
else
  PY="$TMP/venv/Scripts/python.exe"
fi
"$PY" -m pip install --quiet --no-index --no-deps --disable-pip-version-check "$TMP"/wheel/*.whl

echo "== package owns only its governance namespace and command =="
"$PY" -I - <<'PYIDENTITY'
from importlib.metadata import distribution
from pathlib import Path
import sysconfig

installed = distribution("wellmanifest-governance")
entries = {(entry.name, entry.value) for entry in installed.entry_points
           if entry.group == "console_scripts"}
assert entries == {("wellman-governance", "wellmanifest_governance_runtime.check:main")}
assert not any(str(path).startswith("wellman/") for path in installed.files)
assert not any(str(path).startswith("wellmanifest_governance/") for path in installed.files)
site = Path(sysconfig.get_path("purelib"))
# An unrelated full CLI namespace must coexist without being shadowed by this
# distribution. This marker is a fixture, not a production CLI qualification.
foreign = site / "wellman"
foreign.mkdir()
(foreign / "__init__.py").write_text("MARKER = 'unrelated-full-cli'\n")
(site / "wellmanifest_governance.py").write_text("MARKER = 'existing-pytest-plugin'\n")
import wellman
assert wellman.MARKER == "unrelated-full-cli"
import wellmanifest_governance
assert wellmanifest_governance.MARKER == "existing-pytest-plugin"
PYIDENTITY

echo "== governance CLI reports its own standard version =="
expected="wellman-governance $(tr -d '[:space:]' < VERSION)"
actual="$(cd "$TMP" && "$PY" -I -m wellmanifest_governance_runtime --version)"
if [[ "$actual" != "$expected" ]]; then
  echo "expected '$expected', got '$actual'" >&2
  exit 1
fi

echo "== governance check --json runs the bundle outside the source tree =="
status=0
(cd "$TMP" && "$PY" -I -m wellmanifest_governance_runtime check --root "$ROOT" \
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
assert report["validation_scope"] == "static-governance"
assert report["runtime_enforcement"] == "not_checked"
assert report["grants_execution_authority"] is False
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

runtime_refs = {
    "template/files/new-project-governance.workflow.yml": 'PROTECTED_RUNTIME_SHA: ${{ vars.NEW_PROJECT_RUNTIME_SHA }}',
    ".github/workflows/governance-gate-reusable.yml": 'PROTECTED_RUNTIME_SHA: ${{ vars.NEW_PROJECT_RUNTIME_SHA }}',
}
for workflow, expected_ref in runtime_refs.items():
    text = Path(workflow).read_text(encoding="utf-8")
    calls = re.findall(r'\-m "\$runtime_module" check\b(?:[^\n]*\\\n)*[^\n]*', text)
    if not calls or any("--actor ci" not in call for call in calls):
        raise SystemExit(f"{workflow}: every installed governance invocation must pass --actor ci")
    if expected_ref not in text:
        raise SystemExit(f"{workflow}: install Wellman from a trusted immutable source revision")
PY3

echo "== isolated CI runtime installation regression =="
"$PY" "$ROOT/tests/ci-runtime-isolation.test.py"

echo "== detached PR workflow regression with the installed runtime =="
"$PY" "$ROOT/tests/ci-pr-range.test.py"

echo "wellman package: PASS"
