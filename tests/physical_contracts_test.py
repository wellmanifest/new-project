"""Regression tests for declared physical interface contracts (P-PHYS-001)."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import governance_check as gate

CONTRACTS = {
    "schema": "new-project.physical-contracts/v1",
    "contracts": [
        {
            "id": "tic249-limit-switches",
            "paths": ["contracts/hardware/tic249-*.json"],
            "properties": ["pin-assignment", "active-level", "pull"],
            "hazard": "motion",
            "acceptance": "Each switch reads inactive at rest and active while actuated on the rig.",
        },
        {
            "id": "stacknet-profiles",
            "paths": ["main/hardware_profiles.json"],
            "properties": ["capability-set"],
            "hazard": "pressure",
            "acceptance": "Every capability of the deployed profile is detected after flashing.",
        },
    ],
}

# 2026-09-29: the limit switches moved from SCL/SDA to TX/RX and the active
# level flipped in the same edit; only the move was intended.
PIN_MOVE = {
    "contract": "tic249-limit-switches", "property": "pin-assignment",
    "signal": "limit forward/reverse", "before": "SCL/SDA", "after": "TX/RX",
    "acceptance": ["forward reads inactive at rest and active while pressed",
                   "reverse reads inactive at rest and active while pressed"],
}
POLARITY_FLIP = dict(PIN_MOVE, property="active-level", before="active-low", after="active-high")


class PhysicalContractTests(unittest.TestCase):
    def run_gate(self, changed, physical_changes=None, contracts=CONTRACTS):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            if contracts is not None:
                (root / ".governance").mkdir()
                (root / ".governance/physical-contracts.json").write_text(
                    contracts if isinstance(contracts, str) else json.dumps(contracts))
            intent = {} if physical_changes is None else {"physicalChanges": physical_changes}
            report = gate.Report(root)
            gate.check_physical_contract_changes(root, intent, "ticket-001", changed, report)
            return [item.code for item in report.findings]

    def test_adopters_without_declaration_are_unaffected(self):
        self.assertEqual(self.run_gate(["main/hardware_profiles.json"], contracts=None), [])

    def test_undeclared_change_to_a_physical_contract_fails(self):
        self.assertEqual(self.run_gate(["contracts/hardware/tic249-nvm.json"]), ["GOV-PHYS-001"])

    def test_dropping_a_capability_from_a_profile_needs_declaration(self):
        # 2026-09-29: a new I2C Tic profile silently lost the DRI0050 pump module.
        self.assertEqual(self.run_gate(["main/hardware_profiles.json"], [PIN_MOVE]), ["GOV-PHYS-001"])
        drop = {"contract": "stacknet-profiles", "property": "capability-set",
                "signal": "cores3-i2c-tic modules", "before": "dri0050,tic", "after": "tic",
                "acceptance": ["pump detected after flash or removal confirmed by owner"]}
        self.assertEqual(self.run_gate(["main/hardware_profiles.json"], [drop]), [])

    def test_declared_change_passes_and_unrelated_paths_are_ignored(self):
        self.assertEqual(self.run_gate(["contracts/hardware/tic249-nvm.json"], [PIN_MOVE, POLARITY_FLIP]), [])
        self.assertEqual(self.run_gate(["README.md"]), [])

    def test_invalid_declaration_fails_closed(self):
        self.assertEqual(self.run_gate(["README.md"], contracts="{"), ["GOV-PHYS-002"])
        broken = {"schema": "new-project.physical-contracts/v1",
                  "contracts": [dict(CONTRACTS["contracts"][0], hazard="unknown")]}
        self.assertEqual(self.run_gate(["README.md"], contracts=broken), ["GOV-PHYS-002"])

    def test_declared_property_must_belong_to_the_named_contract(self):
        for prop in ("timing", "capability-set"):
            with self.subTest(property=prop):
                invalid = dict(PIN_MOVE, property=prop)
                self.assertIn("GOV-PHYS-001", self.run_gate(
                    ["contracts/hardware/tic249-nvm.json"], [invalid]))
        self.assertIn("GOV-PHYS-001", self.run_gate(
            ["contracts/hardware/tic249-nvm.json"], [dict(PIN_MOVE, contract="unknown")]))
        self.assertIn("GOV-PHYS-001", self.run_gate(
            ["contracts/hardware/tic249-nvm.json"], [PIN_MOVE, dict(PIN_MOVE, property="timing")]))
        keep = {"contract": "tic249-limit-switches", "property": "none", "rationale": "Reformat only"}
        self.assertEqual(self.run_gate(["contracts/hardware/tic249-nvm.json"], [keep]), [])

    def test_non_string_hazards_and_properties_fail_closed(self):
        for hazard in ([], {}, None, 42):
            with self.subTest(hazard=hazard):
                broken = {"schema": "new-project.physical-contracts/v1",
                          "contracts": [dict(CONTRACTS["contracts"][0], hazard=hazard)]}
                self.assertEqual(self.run_gate(["README.md"], contracts=broken), ["GOV-PHYS-002"])
        for prop in ([], {}, None, 42):
            with self.subTest(property=prop):
                self.assertIsNotNone(gate.physical_changes_error([dict(PIN_MOVE, property=prop)]))

    def test_duplicate_contract_paths_and_properties_match_schema_rejection(self):
        original = CONTRACTS["contracts"][0]
        for field in ("paths", "properties"):
            with self.subTest(field=field):
                broken = {"schema": "new-project.physical-contracts/v1",
                          "contracts": [dict(original, **{field: original[field] + original[field]})]}
                self.assertEqual(self.run_gate(["README.md"], contracts=broken), ["GOV-PHYS-002"])

    def test_each_property_change_is_explicit(self):
        self.assertIsNone(gate.physical_changes_error([PIN_MOVE, POLARITY_FLIP]))
        self.assertIn("differ", gate.physical_changes_error([dict(PIN_MOVE, after="SCL/SDA")]))
        self.assertIn("acceptance", gate.physical_changes_error([dict(PIN_MOVE, acceptance=[])]))
        self.assertIn("property", gate.physical_changes_error([dict(PIN_MOVE, property="wiring")]))
        self.assertIn("non-empty", gate.physical_changes_error([]))

    def test_semantics_preserving_edit_needs_a_rationale(self):
        keep = {"contract": "tic249-limit-switches", "property": "none", "rationale": "Reformat only"}
        self.assertIsNone(gate.physical_changes_error([keep]))
        self.assertIsNotNone(gate.physical_changes_error([dict(keep, rationale=" ")]))
        self.assertIsNotNone(gate.physical_changes_error([dict(keep, before="x")]))

    def test_intent_field_is_optional_for_v2_and_v3_only(self):
        base = {"schema": "new-project.intent/v3", "ticket": "ticket-001", "summary": "s",
                "allowedPaths": ["a"], "forbiddenPaths": [], "stacks": [], "workstream": "w",
                "dependsOn": [], "conflictsWith": [], "integrationTicket": None,
                "classification": {"kind": "BUG", "priority": "P1", "origin": "regression"}}
        self.assertIsNone(gate.intent_fields_error(base))
        self.assertIsNone(gate.intent_fields_error(dict(base, physicalChanges=[PIN_MOVE])))
        v1 = {key: base[key] for key in ("ticket", "summary", "allowedPaths", "forbiddenPaths", "stacks")}
        v1["schema"] = "new-project.intent/v1"
        self.assertIsNotNone(gate.intent_fields_error(dict(v1, physicalChanges=[PIN_MOVE])))


if __name__ == "__main__":
    unittest.main()
