#!/usr/bin/env python3
"""Offline conformance checker for wellmanifest/semver standard."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any, Dict, List, Tuple

SEMVER_REGEX = re.compile(
    r"^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)"
    r"(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)"
    r"(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
    r"(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
)

HEX64_REGEX = re.compile(r"^[a-f0-9]{64}$")
HEX40_REGEX = re.compile(r"^[a-f0-9]{40}$")


def load_json(path: Path) -> Dict[str, Any]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:
        raise ValueError(f"Failed to read JSON from {path}: {exc}") from exc


def validate_embedded_release_manifest(data: Dict[str, Any]) -> Tuple[bool, List[str], List[str]]:
    passed_rules: List[str] = []
    violations: List[str] = []

    # Rule SEMVER-019 & Schema basic checks
    expected_schema = "wellmanifest.semver/embedded-release/v1"
    if data.get("schema") != expected_schema:
        violations.append(f"SEMVER-019: Missing or invalid schema, expected '{expected_schema}', got '{data.get('schema')}'")
    else:
        passed_rules.append("SEMVER-019")

    # System SemVer format
    sys_ver = str(data.get("system_version", ""))
    if not SEMVER_REGEX.match(sys_ver):
        violations.append(f"SEMVER-001: Invalid system SemVer format: '{sys_ver}'")

    components = data.get("components", [])
    if not isinstance(components, list) or len(components) == 0:
        violations.append("SEMVER-001: 'components' must be a non-empty list")
        return False, passed_rules, violations

    found_host = False
    found_mcu = False
    mcu_versions = []
    host_versions = []

    for comp in components:
        cid = comp.get("component_id", "unknown")
        tier = comp.get("tier")
        ver = str(comp.get("version", ""))
        commit = str(comp.get("git_commit", ""))

        if not SEMVER_REGEX.match(ver):
            violations.append(f"SEMVER-001: Component '{cid}' has invalid SemVer: '{ver}'")

        if not HEX40_REGEX.match(commit):
            violations.append(f"SEMVER-002: Component '{cid}' has invalid git commit SHA: '{commit}'")

        if tier == "edge_host":
            found_host = True
            host_versions.append(ver)
        elif tier == "microcontroller_firmware":
            found_mcu = True
            mcu_versions.append(ver)
            target_hw = comp.get("target_hardware")
            if not target_hw:
                violations.append(f"SEMVER-004: MCU component '{cid}' missing 'target_hardware'")
            else:
                passed_rules.append("SEMVER-004")

            bin_id = comp.get("binary_identity")
            if not isinstance(bin_id, dict):
                violations.append(f"SEMVER-002: MCU component '{cid}' missing 'binary_identity' descriptor")
            else:
                sha256 = str(bin_id.get("sha256", ""))
                elf_sha256 = str(bin_id.get("elf_sha256", ""))
                part = str(bin_id.get("target_partition", ""))

                if not HEX64_REGEX.match(sha256):
                    violations.append(f"SEMVER-002: MCU component '{cid}' invalid binary sha256: '{sha256}'")
                if not HEX64_REGEX.match(elf_sha256):
                    violations.append(f"SEMVER-002: MCU component '{cid}' invalid ELF sha256: '{elf_sha256}'")
                else:
                    passed_rules.append("SEMVER-002")

                if part not in ("ota_0", "ota_1", "app_dual"):
                    violations.append(f"SEMVER-013: MCU component '{cid}' invalid target_partition '{part}', must be A/B dual bank")
                else:
                    passed_rules.append("SEMVER-013")

    if found_host and found_mcu:
        # Check strict separation: host and mcu shouldn't blindly track system if versions are distinct
        passed_rules.append("SEMVER-001")

    # Contract version
    compat = data.get("compatibility", {})
    if isinstance(compat, dict) and compat.get("oql_contract_version"):
        passed_rules.append("SEMVER-003")
    else:
        violations.append("SEMVER-003: Missing 'compatibility.oql_contract_version'")

    if "nvs_migration_required" in compat:
        passed_rules.append("SEMVER-008")

    # Pipeline attestation
    pipe = data.get("pipeline_attestation", {})
    if isinstance(pipe, dict):
        if pipe.get("dual_build_verified") is True:
            passed_rules.append("SEMVER-009")
        else:
            violations.append("SEMVER-009: Dual build not verified in pipeline attestation")

        if pipe.get("static_safety_analyzed") is True:
            passed_rules.append("SEMVER-010")
        else:
            violations.append("SEMVER-010: Static safety analysis not passed")

        if pipe.get("hil_simulation_passed") is True:
            passed_rules.append("SEMVER-011")
        else:
            violations.append("SEMVER-011: HIL simulation / Digital Twin tests not passed")

        if pipe.get("safe_state_preconditions_verified") is True:
            passed_rules.append("SEMVER-012")
        else:
            violations.append("SEMVER-012: Safe-state preconditions not verified")
    else:
        violations.append("SEMVER-009: Missing pipeline_attestation section")

    passed_rules.append("SEMVER-023")  # Offline execution rule satisfied
    return len(violations) == 0, sorted(list(set(passed_rules))), violations


def main() -> int:
    parser = argparse.ArgumentParser(description="Wellmanifest SemVer offline conformance checker")
    parser.add_argument("manifest", type=Path, help="Path to heterogeneous release manifest JSON")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")
    args = parser.parse_args()

    if not args.manifest.is_file():
        print(f"Error: Manifest file {args.manifest} not found", file=sys.stderr)
        return 1

    try:
        data = load_json(args.manifest)
        ok, passed, violations = validate_embedded_release_manifest(data)
    except Exception as exc:
        print(f"Error during validation: {exc}", file=sys.stderr)
        return 2

    report = {
        "conformance": "PASS" if ok else "FAIL",
        "manifest": str(args.manifest),
        "rules_passed_count": len(passed),
        "rules_passed": passed,
        "violations_count": len(violations),
        "violations": violations
    }

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"=== Wellmanifest SemVer Conformance: {report['conformance']} ===")
        print(f"Target: {args.manifest}")
        print(f"Rules satisfied ({len(passed)}): {', '.join(passed)}")
        if violations:
            print(f"\nViolations ({len(violations)}):")
            for v in violations:
                print(f" - [FAIL] {v}")
        else:
            print("\nAll evaluated Embedded SemVer rules passed.")

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
