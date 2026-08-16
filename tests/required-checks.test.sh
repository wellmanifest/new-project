#!/usr/bin/env bash
# AC-02/AC-03 for ticket-030: gate matches workflow jobs; mutation is detected.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "== positive: source matches ci.yml =="
python3 scripts/check_required_checks.py

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

echo "== mutation: drop windows-governance job from a copy of ci.yml =="
cp .github/workflows/ci.yml "$TMP/ci.yml"
# windows-governance is the last job; truncate from its key to EOF
python3 - <<'PY' "$TMP/ci.yml"
from pathlib import Path
import sys
path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
marker = "\n  windows-governance:"
idx = text.find(marker)
if idx < 0:
    raise SystemExit("windows-governance job not found in ci.yml copy")
path.write_text(text[:idx] + "\n", encoding="utf-8")
PY

if python3 scripts/check_required_checks.py --workflow "$TMP/ci.yml"; then
  echo "expected gate to fail after removing windows-governance" >&2
  exit 1
fi
echo "mutation correctly failed"

echo "== mutation: remove one name from source copy =="
python3 - <<'PY' "$TMP"
import json
from pathlib import Path
import sys
tmp = Path(sys.argv[1])
src = json.loads(Path("governance/required-checks.json").read_text(encoding="utf-8"))
src["requiredCheckNames"] = ["test"]  # drop windows-governance
path = tmp / "required-checks.json"
path.write_text(json.dumps(src, indent=2) + "\n", encoding="utf-8")
PY
if python3 scripts/check_required_checks.py --source "$TMP/required-checks.json"; then
  echo "expected gate to fail when source omits a published job" >&2
  exit 1
fi
echo "source mutation correctly failed"

ADOPTER="$TMP/adopter"
mkdir -p "$ADOPTER/.governance" "$ADOPTER/.github/workflows"
cp scripts/check_required_checks.py "$ADOPTER/.governance/check_required_checks.py"
cat > "$ADOPTER/.github/workflows/new-project-governance.yml" <<'YAML'
name: new-project-governance
on: [push]
jobs:
  remote-lifecycle:
    name: governance / remote lifecycle
    runs-on: ubuntu-latest
    steps:
      - run: true
YAML
cat > "$ADOPTER/.github/workflows/standard-conformance.yml" <<'YAML'
name: standard-conformance
on: [push]
jobs:
  conformance:
    name: standards / autonomy conformance
    runs-on: ubuntu-latest
    steps:
      - run: true
YAML
python3 - "$ADOPTER/.governance/required-checks.json" <<'PY'
import json
from pathlib import Path
import sys
Path(sys.argv[1]).write_text(json.dumps({
    "schema": "new-project.required-checks/v1",
    "version": 1,
    "repository": "wellmanifest/autonomy",
    "requiredChecks": [
        {
            "name": "governance / remote lifecycle",
            "workflowFile": ".github/workflows/new-project-governance.yml",
        },
        {
            "name": "standards / autonomy conformance",
            "workflowFile": ".github/workflows/standard-conformance.yml",
        },
    ],
}, indent=2) + "\n", encoding="utf-8")
PY

echo "== adopter .governance/ layout with display-name jobs =="
python3 "$ADOPTER/.governance/check_required_checks.py" --root "$ADOPTER"

echo "== mutation: job key instead of display name is rejected =="
python3 - "$ADOPTER/.governance/required-checks.json" <<'PY'
import json
from pathlib import Path
import sys
path = Path(sys.argv[1])
data = json.loads(path.read_text(encoding="utf-8"))
data["requiredChecks"][0]["name"] = "remote-lifecycle"
path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
PY
if python3 "$ADOPTER/.governance/check_required_checks.py" --root "$ADOPTER"; then
  echo "expected gate to fail when declaration uses the job key" >&2
  exit 1
fi
echo "job-key declaration correctly failed"

echo "== mutation: inherited hub values are rejected in the adopter =="
python3 - "$ADOPTER/.governance/required-checks.json" <<'PY'
import json
from pathlib import Path
import sys
Path(sys.argv[1]).write_text(json.dumps({
    "schema": "new-project.required-checks/v1",
    "version": 1,
    "repository": "wellmanifest/new-project",
    "workflowFile": ".github/workflows/ci.yml",
    "requiredCheckNames": ["test", "windows-governance"],
}, indent=2) + "\n", encoding="utf-8")
PY
if python3 "$ADOPTER/.governance/check_required_checks.py" --root "$ADOPTER"; then
  echo "expected gate to fail when the adopter still declares hub checks" >&2
  exit 1
fi
echo "inherited hub values correctly failed"

echo "== missing source is a gate message, not a traceback =="
MISSING="$TMP/missing-source"
mkdir -p "$MISSING/.governance"
cp scripts/check_required_checks.py "$MISSING/.governance/check_required_checks.py"
if python3 "$MISSING/.governance/check_required_checks.py" --root "$MISSING" \
  > "$TMP/missing.out" 2> "$TMP/missing.err"; then
  echo "expected missing source to fail the gate" >&2
  exit 1
fi
if grep -q 'Traceback' "$TMP/missing.err"; then
  echo "missing source raised a traceback instead of a gate message" >&2
  cat "$TMP/missing.err" >&2
  exit 1
fi
grep -q 'source file not found' "$TMP/missing.err"
grep -q 'required-checks.json' "$TMP/missing.err"
echo "missing source correctly reported looked-in paths"

echo "required-checks tests: PASS"
