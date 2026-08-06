#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
work="$(mktemp -d "${TMPDIR:-/tmp}/new-project-rule-enforcement.XXXXXX")"
trap 'rm -rf "$work"' EXIT INT TERM

# The live contract must hold: no mapping may name a code the validator does not
# define, and no mapping may survive the rule it describes.
python3 "$repo_root/scripts/audit_rule_enforcement.py" --root "$repo_root" > "$work/live.txt"
grep -Eq '^rule-enforcement: [0-9]+ rules' "$work/live.txt"

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

# The rule set must never shrink silently. wellm's looks_like_policy() rejects a
# block whose first line is data, which hid 30 rules; the tool uses probe()
# instead, and this pins the count so a parser regression is visible.
count="$(python3 "$repo_root/scripts/audit_rule_enforcement.py" --root "$repo_root" --format json | python3 -c 'import json,sys; print(json.load(sys.stdin)["rules"])')"
test "$count" -ge 144

echo 'rule enforcement traceability: PASS'
