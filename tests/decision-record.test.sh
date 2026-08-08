#!/usr/bin/env bash
# ticket-031: positive replay, divergence, ADVISORY ban, append-only.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
PY=python3
SCRIPT=scripts/decision_record.py

good="$TMP/good.dsl"
cat >"$good" <<'EOF'
DECISION D-031-0007
TICKET ticket-031
HEAD_SHA 4116ae07a1c39f2b8d5e1c0a7b3f9d2e6c8a4b10
CORRELATION_ID new-project-pr-41-ticket-031-4116ae07a1
ACTOR agent:validator
APPLIED_RULE P-CORE-015
INPUT required_checks = ["test","windows-governance"]
INPUT observed_checks = ["test=PASS","windows-governance=PASS"]
INPUT author_login = "tom-sapletta-com"
INPUT reviewer_login = "ifuri-validator-agent[bot]"
VERDICT APPROVE AUTHORITY DETERMINISTIC
REJECTED REQUEST_CHANGES BECAUSE NO_UNSAFE_CHANGE_REASON_FOUND
ADVISORY llm_verdict = "APPROVE" MODEL "openrouter/z-ai/glm-5.2"
ASSERT VERDICT_AUTHORITY != "ADVISORY"
EOF

echo "== positive validate =="
$PY $SCRIPT validate-dsl "$good"
test "$($PY $SCRIPT replay "$good")" = "APPROVE"

echo "== divergence: recorded APPROVE but checks failed =="
bad="$TMP/bad.dsl"
sed 's/windows-governance=PASS/windows-governance=FAIL/' "$good" >"$bad"
if $PY $SCRIPT validate-dsl "$bad"; then
  echo "expected GOV-DECISION-004" >&2
  exit 1
fi
grep -q 'GOV-DECISION-004' < <($PY $SCRIPT validate-dsl "$bad" 2>&1 || true)

echo "== ADVISORY as authority is rejected =="
adv="$TMP/adv.dsl"
sed 's/AUTHORITY DETERMINISTIC/AUTHORITY ADVISORY/' "$good" >"$adv"
if $PY $SCRIPT validate-dsl "$adv"; then
  echo "expected GOV-DECISION-003" >&2
  exit 1
fi

echo "== append-only: mutate earlier entry =="
log1="$TMP/log1.md"
log2="$TMP/log2.md"
{
  echo '# decisions'
  echo
  echo '```dsl'
  cat "$good"
  echo '```'
} >"$log1"
# second record append
{
  cat "$log1"
  echo
  echo '```dsl'
  sed 's/D-031-0007/D-031-0008/; s/4116ae07a1c39f2b8d5e1c0a7b3f9d2e6c8a4b10/aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa/' "$good"
  echo '```'
} >"$log2"
$PY $SCRIPT check-append-only "$log1" "$log2"

# mutate first record in log2
mut="$TMP/log-mut.md"
sed 's/NO_UNSAFE_CHANGE_REASON_FOUND/MUTATED_HISTORY/' "$log2" >"$mut"
if $PY $SCRIPT check-append-only "$log1" "$mut"; then
  echo "expected append-only failure" >&2
  exit 1
fi

echo "== JSON schema smoke =="
$PY - <<'PY'
import json
from pathlib import Path
schema = json.loads(Path("governance/decision-record.schema.json").read_text())
assert schema["properties"]["schema"]["const"] == "new-project.decision-record/v1"
from scripts.decision_record import parse_dsl_record, to_dsl, validate_record
text = Path("/tmp").joinpath  # placate linters
PY
# round-trip
$PY - <<PY
import sys
from pathlib import Path
sys.path.insert(0, "scripts")
from decision_record import parse_dsl_record, to_dsl, validate_record
rec = parse_dsl_record(Path("$good").read_text())
assert validate_record(rec) == []
rec2 = parse_dsl_record(to_dsl(rec))
assert rec["decisionId"] == rec2["decisionId"]
assert rec["inputs"] == rec2["inputs"]
print("round-trip OK")
PY

echo "== parser diagnostics remain exact =="
$PY - <<PY
import sys
from pathlib import Path
sys.path.insert(0, "scripts")
from decision_record import parse_dsl_record

good = Path("$good").read_text()
try:
    parse_dsl_record(good + "\nUNKNOWN value\n")
except ValueError as error:
    assert str(error) == "unrecognized decision-record line: UNKNOWN value"
else:
    raise AssertionError("unknown line was accepted")

try:
    parse_dsl_record("DECISION D-031-0007")
except ValueError as error:
    assert str(error) == "decision record missing fields: ['ticket', 'headSha', 'correlationId', 'actor', 'appliedRule', 'verdict', 'verdictAuthority', 'rejected']"
else:
    raise AssertionError("missing fields were accepted")
print("parser diagnostics OK")
PY

echo "decision-record tests: PASS"
