#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
work="$(mktemp -d "${TMPDIR:-/tmp}/new-project-rule-enforcement.XXXXXX")"
trap 'rm -rf "$work"' EXIT INT TERM

# The live contract must hold: no mapping may name a code the validator does not
# define, no mapping may survive the rule it describes, and after ticket-034 every
# rule has either a GOV-* claim or an explicit manual reason (no silent gaps).
python3 "$repo_root/scripts/audit_rule_enforcement.py" --root "$repo_root" --require-complete > "$work/live.txt"
grep -Eq '^rule-enforcement: [0-9]+ rules' "$work/live.txt"
grep -Eq '0 unmapped, 0 codes unclaimed' "$work/live.txt"
python3 "$repo_root/scripts/audit_diagnostics.py" --root "$repo_root" > "$work/diagnostics-live.txt"
grep -Eq '^diagnostic-catalog: [0-9]+ codes, 0 findings$' "$work/diagnostics-live.txt"

python3 - "$repo_root/governance/diagnostics.schema.json" "$repo_root/governance/diagnostics.json" <<'PY'
import json
import sys

from jsonschema import Draft202012Validator

schema = json.load(open(sys.argv[1], encoding="utf-8"))
catalog = json.load(open(sys.argv[2], encoding="utf-8"))
Draft202012Validator.check_schema(schema)
Draft202012Validator(schema).validate(catalog)
PY

# Negative cases run against a copy so the checkout is never mutated.
cp -R "$repo_root/governance" "$repo_root/scripts" "$repo_root/POLICY.md" "$repo_root/CONTRIBUTING.md" "$work/"
mkdir -p "$work/repo" && mv "$work/governance" "$work/scripts" "$work/POLICY.md" "$work/CONTRIBUTING.md" "$work/repo/"

mutate() {
  python3 - "$work/repo/governance/rule-enforcement.json" "$1" "$2" <<'PY'
import json, sys
path, mode, value = sys.argv[1], sys.argv[2], sys.argv[3]
document = json.load(open(path, encoding="utf-8"))
rules = document["rules"]
if mode == "code":
    target = next(iter(rules))
    rules[target].setdefault("codes", []).append(value)
else:
    rules[value] = {"codes": [], "enforcement": "manual", "reason": "negative case"}
json.dump(document, open(path, "w", encoding="utf-8"), indent=2)
PY
}

status=0
mutate code GOV-THIS-CODE-IS-NOT-DEFINED
python3 "$repo_root/scripts/audit_rule_enforcement.py" --root "$work/repo" > "$work/bad-code.txt" || status=$?
test "$status" -eq 1
grep -q 'GOV-THIS-CODE-IS-NOT-DEFINED' "$work/bad-code.txt"

cp "$repo_root/governance/rule-enforcement.json" "$work/repo/governance/rule-enforcement.json"
status=0
mutate rule P-THIS-RULE-WAS-DELETED
python3 "$repo_root/scripts/audit_rule_enforcement.py" --root "$work/repo" > "$work/bad-rule.txt" || status=$?
test "$status" -eq 1
grep -q 'P-THIS-RULE-WAS-DELETED' "$work/bad-rule.txt"

# A stable code without a catalog entry and a linked runbook without the
# required safety sections must both fail with their canonical audit codes.
mkdir -p "$work/diagnostic/governance"
cp "$repo_root/project.sh" "$repo_root/project.bat" "$work/diagnostic/"
cp -R "$repo_root/.github" "$repo_root/error" "$repo_root/project" \
  "$repo_root/scripts" "$repo_root/template" "$work/diagnostic/"
cp "$repo_root/governance/diagnostics.json" "$work/diagnostic/governance/"

python3 - "$work/diagnostic/governance/diagnostics.json" <<'PY'
import json
import sys

path = sys.argv[1]
document = json.load(open(path, encoding="utf-8"))
document["codes"].pop("GOV-APPROVAL-001")
json.dump(document, open(path, "w", encoding="utf-8"), indent=2)
PY
status=0
python3 "$repo_root/scripts/audit_diagnostics.py" --root "$work/diagnostic" > "$work/missing-code.txt" || status=$?
test "$status" -eq 1
grep -q 'GOV-DIAGNOSTIC-001' "$work/missing-code.txt"

cp "$repo_root/governance/diagnostics.json" "$work/diagnostic/governance/diagnostics.json"
python3 - "$work/diagnostic/error/GOV-TICKET-001.md" <<'PY'
import sys

path = sys.argv[1]
content = open(path, encoding="utf-8").read()
content = content.replace("## Verification", "## Missing verification")
open(path, "w", encoding="utf-8").write(content)
PY
status=0
python3 "$repo_root/scripts/audit_diagnostics.py" --root "$work/diagnostic" > "$work/bad-runbook.txt" || status=$?
test "$status" -eq 1
grep -q 'GOV-DIAGNOSTIC-002' "$work/bad-runbook.txt"

# The rule set must never shrink silently. wellm's looks_like_policy() rejects a
# block whose first line is data, which hid 30 rules; the tool uses probe()
# instead, and this pins the count so a parser regression is visible.
count="$(python3 "$repo_root/scripts/audit_rule_enforcement.py" --root "$repo_root" --format json | python3 -c 'import json,sys; print(json.load(sys.stdin)["rules"])')"
test "$count" -ge 144

# Governed publication must use the phase-specific Goal full workflow. These
# checks intentionally validate semantics, not a version string: two Goal
# builds with the same version may expose different capabilities.
python3 - "$repo_root/CONTRIBUTING.md" "$repo_root/governance/rule-enforcement.json" <<'PY'
import json
import re
import sys

policy_path, mapping_path = sys.argv[1:]
policy = open(policy_path, encoding="utf-8").read()
mapping = json.load(open(mapping_path, encoding="utf-8"))["rules"]

def rule_body(rule_id: str) -> str:
    match = re.search(
        rf"^RULE {re.escape(rule_id)}(?: [^\n]*)?\n(.*?)(?=^RULE |^```)",
        policy,
        flags=re.MULTILINE | re.DOTALL,
    )
    assert match, f"missing {rule_id}"
    return match.group(1)

expected = {
    "C-PUBLISH-005": ["goal.yaml", "--delivery-mode", "SOLE_CAPABILITY_EVIDENCE"],
    "C-PUBLISH-006": [
        "goal --delivery-mode pull-request --no-publish -a push --ticket {TICKET_ID}",
        "FORBID RAW_GIT_PUSH",
        "IMPLEMENTATION_PUBLICATION_STOPS_AT_REVIEWABLE_PULL_REQUEST",
        "NEXT PUBLICATION OR BLOCKED",
    ],
    "C-PUBLISH-007": [
        "goal -a --delivery-mode publish-only",
        "goal -a --delivery-mode direct-main",
        "CLEAN_RETESTED_DEFAULT_BRANCH_AT_EXACT_APPROVED_MERGE_SHA",
        "MOVING_EXISTING_TAG",
    ],
    "C-PUBLISH-008": [
        "HEAD_NOT_INTEGRATED",
        "FORBID TREAT_LOCAL_HOOK_OR_DELIVERY_EVENT_AS_TRUSTED_APPROVAL",
        "SERVER_SIDE_TRUST_BOUNDARY",
    ],
}
for rule_id, fragments in expected.items():
    body = rule_body(rule_id)
    for fragment in fragments:
        assert fragment in body, f"{rule_id} missing {fragment!r}"
    entry = mapping.get(rule_id)
    assert entry and entry["enforcement"] == "manual" and entry.get("reason")

implementation = rule_body("C-PUBLISH-006")
assert "PUBLISH_ONLY" in implementation and "TAG_OR_RELEASE_CREATION" in implementation
release = rule_body("C-PUBLISH-007")
assert "PULL_REQUEST_HEAD" in release and "UNAPPROVED_HEAD" in release

implementation_pr = rule_body("C-PUBLISH-003")
for fragment in (
    "IN_PROGRESS AND WORKFLOW_STATE = PUBLICATION UNTIL TRUSTED_MERGE_INTEGRATES_HEAD",
    "NEXT PUBLICATION OR BLOCKED",
):
    assert fragment in implementation_pr
assert "NEXT DONE" not in implementation_pr
assert mapping["C-PUBLISH-003"] == {
    "codes": ["GOV-TICKET-001"],
    "enforcement": "deterministic",
}

goal_pr = rule_body("C-PUBLISH-006")
assert "NEXT DONE" not in goal_pr
goal_record = rule_body("C-PUBLISH-008")
assert "NEXT PUBLICATION OR DONE OR BLOCKED" in goal_record

closure = rule_body("C-PUBLISH-009")
for fragment in (
    "GOVERNANCE_ONLY_CLOSURE_FROM_CURRENT_DEFAULT_BRANCH",
    "TICKET_STATUS = DONE AND WORKFLOW_STATE = DONE",
    "FORBID CARRY_UNMERGED_IMPLEMENTATION_DIFF_IN_CLOSURE",
):
    assert fragment in closure
assert mapping["C-PUBLISH-009"]["enforcement"] == "manual"

allocation = rule_body("C-CONCURRENCY-002")
for fragment in (
    'MANAGED_ALLOCATOR "project/new-ticket.sh"',
    "CLONE_WIDE_TICKET_ALLOCATION_LOCK",
    "FORBID MANUAL_MKDIR_OR_TEMPLATE_COPY",
):
    assert fragment in allocation
assert {"GOV-TICKET-ALLOCATION-001", "GOV-TICKET-ALLOCATION-002"} <= set(
    mapping["C-CONCURRENCY-002"]["codes"]
)
print("governed Goal publication contract: PASS")
PY

echo 'rule enforcement traceability: PASS'
