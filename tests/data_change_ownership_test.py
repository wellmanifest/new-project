"""Regression tests for local deployment state versus data ownership changes."""
import copy
import json
from pathlib import Path
import sys
import unittest

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import governance_check as gate


class DataChangeOwnershipTests(unittest.TestCase):
    def setUp(self):
        self.architecture = {
            "status": "accepted", "decision": "Retain component ownership",
            "components": [{"name": "deployment", "paths": ["infra/**"]}],
            "responsibilityChanges": False, "interfaceChanges": [],
            "dataChanges": [], "ui": {"impact": "none", "states": [], "evidence": []},
            "rollback": "Restore retained image and journal",
        }

    def change(self, kind="component-local-state", **updates):
        return {"kind": kind, "component": "deployment",
                "description": "Private deployment journal", **updates}

    def check(self, changes, workstream="infrastructure", responsibility=False):
        a = copy.deepcopy(self.architecture)
        a["dataChanges"] = changes
        a["responsibilityChanges"] = responsibility
        error = gate.delivery_architecture_error(a)
        if error:
            return error
        report = gate.Report(ROOT)
        intent = {"workstream": workstream}
        record = gate.TicketRecord(ROOT, "IN_PROGRESS", "EDIT", intent, None)
        gate.check_integration_ownership(
            {"coordination": {"integration": {"workstream": "integration"}}},
            {"architecture": a}, record, "intent.json", report)
        return report.errors

    def test_local_journal_does_not_require_integration(self):
        self.assertEqual(self.check([self.change()]), 0)

    def test_empty_data_changes_remain_compatible(self):
        self.assertEqual(self.check([]), 0)

    def test_legacy_prose_remains_conservative(self):
        self.assertEqual(self.check(["Private deployment journal"]), 1)
        self.assertEqual(self.check(["Private deployment journal"], "integration"), 0)

    def test_migrations_transfers_and_unknown_require_integration(self):
        for kind in gate.DATA_CHANGE_KINDS - {"component-local-state"}:
            with self.subTest(kind=kind):
                self.assertEqual(self.check([self.change(kind)]), 1)
                self.assertEqual(self.check([self.change(kind)], "integration"), 0)

    def test_mixed_local_state_and_migration_is_not_exempt(self):
        self.assertEqual(self.check([self.change(), self.change("schema-migration")]), 1)

    def test_local_record_does_not_hide_responsibility_transfer(self):
        self.assertEqual(self.check([self.change()], responsibility=True), 1)

    def test_owner_must_exist_and_be_unambiguous(self):
        self.assertIsInstance(self.check([self.change(component="other")]), str)
        self.architecture["components"].append({"name": "deployment", "paths": ["other/**"]})
        self.assertIsInstance(self.check([self.change()]), str)

    def test_invalid_records_fail_without_crashing(self):
        values = [None, True, 1, [], {}, "", " ", self.change(kind="typo"),
                  self.change(kind=[]), self.change(component=[]),
                  self.change(description=" "), self.change(extra="bypass")]
        for value in values:
            with self.subTest(value=value):
                self.assertIsInstance(self.check([value]), str)

    def test_duplicate_records_rejected(self):
        self.assertIsInstance(self.check([self.change(), self.change()]), str)

    def test_json_schema_matches_supported_shapes(self):
        import jsonschema
        schema = json.loads((ROOT / "governance/intent.schema.json").read_text())
        item = schema["properties"]["delivery"]["properties"]["architecture"]["properties"]["dataChanges"]
        for kind in gate.DATA_CHANGE_KINDS:
            jsonschema.validate([self.change(kind)], item)
        jsonschema.validate(["Legacy prose"], item)
        for invalid in [self.change(kind="typo"), self.change(extra=True), {}, None]:
            with self.subTest(invalid=invalid), self.assertRaises(jsonschema.ValidationError):
                jsonschema.validate([invalid], item)


if __name__ == "__main__":
    unittest.main()
