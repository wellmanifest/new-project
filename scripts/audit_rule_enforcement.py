#!/usr/bin/env python3
"""Report which normative rules have deterministic enforcement, and which do not.

`POLICY.md` and `CONTRIBUTING.md` state the contract as `RULE` blocks.
`scripts/governance_check.py` enforces part of it as stable `GOV-*` diagnostic
codes. Nothing connected the two: a rule could lose its check, or a check could
outlive its rule, and no gate would notice.

Both sides are derived, never restated here. Rules come from the documents, codes
come from the validator source. Only the mapping in
`governance/rule-enforcement.json` is written by hand, because that association is
knowledge rather than something a parser can recover - and because it is derived
on both sides, a drift on either immediately fails.

Rules are parsed with the `policy-sh@1` frontend from `wellm` when it is
importable, so the grammar has one owner. A bounded local reader covers the same
shape when it is not, and the mode is reported so a reader knows which ran.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
POLICY_DOCUMENTS = ("POLICY.md", "CONTRIBUTING.md")
MAPPING_PATH = Path("governance/rule-enforcement.json")
MAPPING_SCHEMA = "new-project.rule-enforcement/v1"
VALIDATOR_PATH = Path("scripts/governance_check.py")

DSL_BLOCK = re.compile(r"```(?:dsl|bash)\n(.*?)```", re.S)
RULE_HEADER = re.compile(r"^RULE\s+([A-Za-z0-9_.:-]+)(?:\s+TYPE\s+(\S+))?\s*$", re.MULTILINE)
GOV_CODE = re.compile(r'"(GOV-[A-Z]+-[0-9]{3})"')


def _wellm_rules(block: str) -> list[dict[str, Any]] | None:
    try:
        from wellmanifest.dialects.policy import PolicyDialect
    except ImportError:
        return None
    dialect = PolicyDialect()
    # probe(), not looks_like_policy(). The latter tests only the first non-empty
    # line, so a block that opens with data before its first RULE is rejected
    # whole - that alone dropped 30 rules here, every C-DOCKER, C-ENV and
    # C-EVALUATION. probe() searches the whole block and scores those 0.98, and
    # parse() reads them correctly.
    if dialect.probe(block) < 0.5:
        return []
    parsed = dialect.parse(block)
    data = parsed.data if hasattr(parsed, "data") else parsed
    return list(data.get("rules", []))


def _local_rules(block: str) -> list[dict[str, Any]]:
    return [{"id": rule_id, "type": rule_type} for rule_id, rule_type in RULE_HEADER.findall(block)]


def declared_rules(root: Path) -> tuple[list[dict[str, Any]], str]:
    mode = "local"
    rules: list[dict[str, Any]] = []
    for name in POLICY_DOCUMENTS:
        document = root / name
        if not document.is_file():
            continue
        for block in DSL_BLOCK.findall(document.read_text(encoding="utf-8")):
            parsed = _wellm_rules(block)
            if parsed is None:
                parsed = _local_rules(block)
            else:
                mode = "wellm"
            for rule in parsed:
                rules.append({"id": rule["id"], "type": rule.get("type"), "document": name})
    return rules, mode


def enforcement_codes(root: Path) -> list[str]:
    source = (root / VALIDATOR_PATH).read_text(encoding="utf-8")
    return sorted(set(GOV_CODE.findall(source)))


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
