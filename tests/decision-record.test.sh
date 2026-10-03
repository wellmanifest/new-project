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

echo "== unsupported policy cannot masquerade as a check gate =="
sed 's/APPLIED_RULE P-CORE-015/APPLIED_RULE P-CORE-010/' "$good" > "$TMP/unsupported.dsl"
if $PY $SCRIPT validate-dsl "$TMP/unsupported.dsl" > "$TMP/unsupported.out" 2>&1; then
  echo "unsupported policy unexpectedly replayed" >&2
  exit 1
fi
grep -q 'GOV-DECISION-002' "$TMP/unsupported.out"

# Unsupported policy ids and author-supplied verdicts are not deterministic replay.
python3 - "$ROOT" <<'PY_REPLAY_BOUNDARY'
import copy
import importlib.util
import json
import os
import sys
import tempfile
from pathlib import Path

root = Path(sys.argv[1])
violations = []
for name, source in (
    ("managed", root / "scripts/decision_record.py"),
    ("bundled", root / "packages/wellman/src/wellman/_bundled/decision_record.py"),
):
    spec = importlib.util.spec_from_file_location("decision_replay_" + name, source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    record = {
        "schema": module.SCHEMA, "verdictAuthority": "DETERMINISTIC",
        "verdict": "APPROVE", "appliedRule": "P-CORE-015",
        "inputs": {"required_checks": ["gate"], "observed_checks": ["gate=PASS"]},
    }
    for rule in ("P-CORE-015", "C-CI-001", "C-DECISION-GATE"):
        assert module.validate_record({**record, "appliedRule": rule}) == []
    for number in range(10, 20):
        if number == 15:
            continue
        rule = "P-CORE-0" + str(number)
        if not module.validate_record({**record, "appliedRule": rule}):
            violations.append((name, "unsupported-prefix-rule", rule))
    custom = {**record, "appliedRule": "CUSTOM-UNIMPLEMENTED", "inputs": {"expected_verdict_from_rule": "APPROVE"}}
    if not module.validate_record(custom):
        violations.append((name, "caller-supplied-replay-verdict"))
    for required in ([], [""], ["gate", "gate"], [True]):
        altered = copy.deepcopy(record)
        altered["inputs"]["required_checks"] = required
        if not module.validate_record(altered):
            violations.append((name, "invalid-required-checks", required))
    altered = copy.deepcopy(record)
    altered["inputs"]["observed_checks"] = ["gate=FAIL", "gate=PASS"]
    if not module.validate_record(altered):
        violations.append((name, "contradictory-observation"))
    altered["inputs"]["observed_checks"] = ["gate=PASS", "gate=PASS"]
    assert not module.validate_record(altered), "consistent repeated observations remain valid"
    old = Path.cwd()
    try:
        with tempfile.TemporaryDirectory(prefix="decision-derivation-") as tmp:
            os.chdir(tmp)
            evaluation = {"schemaVersion": "t2c.change-evaluation/v1", "subject": {"headSha": "a" * 40}, "contract": {"ticket": "ticket-001"}, "verdict": "allow", "gates": {"gate": "PASS"}}
            meta = {"decisionId": "D-001-0001", "correlationId": "isolated-regression"}
            for candidate in ("governance/required-checks.json", ".governance/required-checks.json"):
                file = Path(candidate)
                file.parent.mkdir(exist_ok=True)
                file.write_text(json.dumps({"requiredCheckNames": ["gate"]}), encoding="utf-8")
                try:
                    derived = module.from_change_evaluation(evaluation, **meta)
                except FileNotFoundError:
                    violations.append((name, "adopter-metadata-path"))
                else:
                    assert not module.validate_record(derived), (name, candidate, derived)
                    denied = module.from_change_evaluation({**evaluation, "verdict": "deny"}, **meta)
                    if module.replay_verdict(denied) != "REQUEST_CHANGES":
                        violations.append((name, "denied-evaluation-replayed-as-approval", candidate))
                    empty = module.from_change_evaluation({**evaluation, "gates": {}}, **meta)
                    if empty["inputs"]["observed_checks"] or module.replay_verdict(empty) != "REQUEST_CHANGES":
                        violations.append((name, "invented-observation", candidate))
                file.unlink()
            try:
                module.from_change_evaluation(evaluation, **meta)
            except ValueError as error:
                assert "GOV-DECISION-002" in str(error)
            else:
                raise AssertionError("missing required-check metadata must fail")
            file = Path(".governance/required-checks.json")
            file.write_text(json.dumps({"requiredCheckNames": []}), encoding="utf-8")
            try:
                module.from_change_evaluation(evaluation, **meta)
            except ValueError as error:
                assert "GOV-DECISION-002" in str(error)
            else:
                raise AssertionError("empty default required checks must fail")
            file.unlink()
            derived = module.from_change_evaluation(evaluation, **meta, required_checks=["gate"])
            assert not module.validate_record(derived), "explicit required-check metadata remains supported"
    finally:
        os.chdir(old)
if violations:
    raise AssertionError("Incorrect decision replay or derivation: " + repr(violations))
print("PASS: exact rule replay, check input validation and hub/adopter derivation")
PY_REPLAY_BOUNDARY

echo "decision-record tests: PASS"
