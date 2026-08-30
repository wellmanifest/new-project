#!/usr/bin/env python3
"""Report which normative rules have deterministic enforcement, and which do not.

`POLICY.md` and `CONTRIBUTING.md` state the contract as `RULE` blocks.
Deterministic governance validators enforce part of it as stable `GOV-*`
diagnostic codes. Nothing connected the two: a rule could lose its check, or a
check could outlive its rule, and no gate would notice.

Both sides are derived, never restated here. Rules come from the documents, codes
come from the validator source. Only the mapping in
`governance/rule-enforcement.json` is written by hand, because that association is
knowledge rather than something a parser can recover - and because it is derived
on both sides, a drift on either immediately fails.

Rules are parsed only with the byte-verified Policy DSL runtime pinned by
`governance/policy-dsl.lock.json`. The audit has no optional parser and no
regular-expression fallback for policy documents.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from governance_check import load_policy_dsl_module

REPO_ROOT = Path(__file__).resolve().parents[1]
POLICY_DOCUMENTS = ("POLICY.md", "CONTRIBUTING.md")
MAPPING_PATH = Path("governance/rule-enforcement.json")
MAPPING_SCHEMA = "new-project.rule-enforcement/v1"
VALIDATOR_PATHS = (
    Path("scripts/audit_diagnostics.py"),
    Path("scripts/governance_check.py"),
    Path("scripts/branch_lifecycle_check.py"),
    Path("scripts/workspace_lifecycle_check.py"),
    Path("scripts/remediation_intent.py"),
    # ticket-108: agent_host_check.py emits GOV-AGENT-HOST-004..006 and
    # GOV-PACKAGING-001..003. Leaving it out of this list meant a deterministic
    # validator existed whose codes no normative rule was required to claim.
    Path("scripts/agent_host_check.py"),
    # The managed change-lease checker is independently loadable by governance;
    # its transition diagnostics must remain claimed by normative rules.
    Path("scripts/change_lease_check.py"),
    # Registered allocation is a managed fail-closed validator. Keep its stable
    # errors in the same rule/code traceability graph as the governance gate.
    Path("scripts/ticket_allocation.py"),
)

GOV_CODE = re.compile(r'"(GOV-[A-Z]+(?:-[A-Z]+)*-[0-9]{3})"')


def declared_rules(root: Path) -> tuple[list[dict[str, Any]], str]:
    policy_dsl = load_policy_dsl_module(root)
    rules: list[dict[str, Any]] = []
    for name in POLICY_DOCUMENTS:
        document = root / name
        if not document.is_file():
            continue
        parsed = policy_dsl.parse_markdown(document.read_text(encoding="utf-8"))
        for rule in parsed["rules"]:
            rules.append({"id": rule["id"], "type": rule.get("type"), "document": name})
    return rules, "policy-dsl"


def enforcement_codes(root: Path) -> list[str]:
    codes: set[str] = set()
    for validator_path in VALIDATOR_PATHS:
        source = (root / validator_path).read_text(encoding="utf-8")
        codes.update(GOV_CODE.findall(source))
    return sorted(codes)


def audit(root: Path = REPO_ROOT) -> dict[str, Any]:
    rules, mode = declared_rules(root)
    codes = enforcement_codes(root)
    rule_ids = [rule["id"] for rule in rules]

    duplicates = sorted({rule_id for rule_id in rule_ids if rule_ids.count(rule_id) > 1})

    mapping_file = root / MAPPING_PATH
    mapping: dict[str, Any] = {"schema": MAPPING_SCHEMA, "rules": {}}
    if mapping_file.is_file():
        mapping = json.loads(mapping_file.read_text(encoding="utf-8"))
    entries = mapping.get("rules", {})

    unmapped = sorted(rule_id for rule_id in set(rule_ids) if rule_id not in entries)
    unknown_rules = sorted(rule_id for rule_id in entries if rule_id not in set(rule_ids))

    mapped_codes: set[str] = set()
    bad_codes: list[str] = []
    manual: list[str] = []
    for rule_id, entry in entries.items():
        declared = entry.get("codes", []) if isinstance(entry, dict) else []
        if isinstance(entry, dict) and entry.get("enforcement") == "manual":
            manual.append(rule_id)
        for code in declared:
            mapped_codes.add(code)
            if code not in codes:
                bad_codes.append(f"{rule_id} -> {code}")

    orphan_codes = sorted(code for code in codes if code not in mapped_codes)

    return {
        "schema": "new-project.rule-enforcement-audit/v1",
        "rule_source": mode,
        "rules": len(set(rule_ids)),
        "codes": len(codes),
        "duplicate_rule_ids": duplicates,
        "rules_without_mapping": unmapped,
        "mapped_rules_that_no_longer_exist": unknown_rules,
        "mappings_naming_an_unknown_code": sorted(bad_codes),
        "codes_no_rule_claims": orphan_codes,
        "rules_declared_manual": sorted(manual),
        "ok": not (duplicates or unknown_rules or bad_codes),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=str(REPO_ROOT))
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument(
        "--require-complete",
        action="store_true",
        help="also fail while any rule is still unmapped",
    )
    args = parser.parse_args()

    report = audit(Path(args.root))
    if args.format == "json":
        print(json.dumps(report, indent=2))
    else:
        print(
            f"rule-enforcement: {report['rules']} rules ({report['rule_source']} parser), "
            f"{report['codes']} codes, {len(report['rules_without_mapping'])} unmapped, "
            f"{len(report['codes_no_rule_claims'])} codes unclaimed"
        )
        for key in (
            "duplicate_rule_ids",
            "mapped_rules_that_no_longer_exist",
            "mappings_naming_an_unknown_code",
        ):
            for item in report[key]:
                print(f"  {key}: {item}")

    complete = report["ok"] and not report["rules_without_mapping"]
    return 0 if (complete if args.require_complete else report["ok"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
