#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
checker="$root/scripts/standard_pack_check.py"
catalog="governance/standard-packs.json"
adoption="governance/standard-adoption.default.json"

python3 "$checker" --root "$root" --catalog "$catalog" --adoption "$adoption" --format json >/dev/null
strict_report="$(mktemp)"
trap ':' EXIT
if python3 "$checker" --root "$root" --catalog "$catalog" --adoption "$adoption" --strict --format json >"$strict_report"; then
  echo "strict standard-pack check unexpectedly accepted audit findings" >&2
  exit 1
fi
grep -q 'GOV-STANDARD-PACK-001' "$strict_report"

# ticket-268: CI honours the adopter's declared mode instead of forcing --strict.
enforce_adoption="$(mktemp)"
python3 - "$root/$adoption" "$enforce_adoption" <<'PY2'
import json
import sys

record = json.load(open(sys.argv[1], encoding="utf-8"))
record["mode"] = "enforce"
json.dump(record, open(sys.argv[2], "w", encoding="utf-8"))
PY2
if python3 "$checker" --root "$root" --catalog "$catalog" --adoption "$enforce_adoption" --format json >/dev/null; then
  echo "enforce-mode adoption unexpectedly accepted missing packs" >&2
  exit 1
fi
if grep -q 'standard_pack_check.py.*--strict' "$root/template/files/new-project-governance.workflow.yml"; then
  echo "adopter workflow must not force --strict; the adoption mode decides" >&2
  exit 1
fi

python3 - "$root" <<'PY'
import hashlib
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
inventory = json.loads((root / "governance/managed-copies.json").read_text())
expected_sources = {
    ".governance/docs/BRANCH_INTENT_RECONCILIATION.md": "docs/BRANCH_INTENT_RECONCILIATION.md",
    ".governance/docs/LOCAL_CI_PUBLICATION.md": "template/files/LOCAL_CI_PUBLICATION.template.md",
    ".governance/docs/SNAPSHOT_MIGRATION.md": "docs/information/snapshot-migration.md",
}
assert set(inventory) == set(expected_sources)
for target, source in expected_sources.items():
    assert inventory[target] == hashlib.sha256((root / source).read_bytes()).hexdigest()
package = json.loads((root / "governance/package-manifest.json").read_text())
assert any(
    item.get("source") == "governance/managed-copies.json"
    and item.get("target") == ".governance/managed-copies.json"
    and item.get("strategy") == "managed"
    for item in package["files"]
)
PY

echo "standard-pack-check.test.sh OK"
