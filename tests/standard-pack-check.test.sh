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
package = json.loads((root / "governance/package-manifest.json").read_text())
# Every projected .governance/docs copy must be inventoried, or the
# wellmanifest/docs checker treats it as an adopter document (DOCS_LOCATION).
expected_sources = {
    item["target"]: item["source"]
    for item in package["files"]
    if item.get("target", "").startswith(".governance/docs/")
}
assert {
    ".governance/docs/BRANCH_INTENT_RECONCILIATION.md",
    ".governance/docs/LOCAL_CI_PUBLICATION.md",
    ".governance/docs/SNAPSHOT_MIGRATION.md",
    ".governance/docs/information/continuity-namespaces.md",
} <= set(expected_sources)
assert set(inventory) == set(expected_sources), sorted(set(inventory) ^ set(expected_sources))
for target, source in expected_sources.items():
    assert inventory[target] == hashlib.sha256((root / source).read_bytes()).hexdigest(), target
assert any(
    item.get("source") == "governance/managed-copies.json"
    and item.get("target") == ".governance/managed-copies.json"
    and item.get("strategy") == "managed"
    for item in package["files"]
)

# The baseline profile may only demand S3+ (a required CI check) for packs whose
# conformance command the adopter workflow actually runs. Worktree placement is
# checked by local hooks only, and the managed workflow runs neither the docs
# nor the logs checker, so baseline must not demand S3 for them.
catalog = json.loads((root / "governance/standard-packs.json").read_text())
baseline = {item["id"]: item["minimumLevel"] for item in catalog["profiles"]["baseline"]["requirements"]}
workflow = (root / "template/files/new-project-governance.workflow.yml").read_text()
for pack_id, marker in {
    "wellmanifest/worktrees": "worktree_path_check.py",
    "wellmanifest/docs": "docs/standard/check.py",
    "wellmanifest/logs": "logs_check.py",
}.items():
    if marker not in workflow and pack_id in baseline:
        assert int(baseline[pack_id][1]) <= 2, (pack_id, baseline[pack_id])
PY

# Typed execution models and confined artifact reads use the actual strict CLI.
python3 "$root/tests/runtime_safety_test.py" \
  RuntimeSafetyTests.test_catalog_execution_models_are_typed_before_strict_conformance \
  RuntimeSafetyTests.test_adoption_artifacts_stay_in_the_canonical_checkout

python3 "$root/tests/session-recovery-adoption.test.py"
python3 "$root/tests/semver-adoption.test.py"
python3 "$root/tests/standard_pack_evidence_test.py"

echo "standard-pack-check.test.sh OK"
