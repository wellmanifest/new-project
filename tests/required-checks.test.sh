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

echo "required-checks tests: PASS"
