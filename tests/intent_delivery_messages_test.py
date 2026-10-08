#!/usr/bin/env python3
"""GOV-INTENT-002 delivery messages name what is expected and what was received."""
from __future__ import annotations

from pathlib import Path
import sys
import unittest

sys.dont_write_bytecode = True
SOURCE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SOURCE / "scripts"))
import governance_check as gc


class DeliveryMessageTests(unittest.TestCase):
    def test_incomplete_ui_names_missing_fields_and_the_non_ui_shape(self):
        message = gc.delivery_ui_error({"impact": "none"})
        self.assertTrue(message.startswith("delivery UI decision is incomplete"))
        self.assertIn("missing: evidence, states", message)
        self.assertIn('{"impact": "none", "states": [], "evidence": []}', message)

    def test_invalid_ui_impact_lists_allowed_values(self):
        message = gc.delivery_ui_error({"impact": "minor", "states": [], "evidence": []})
        self.assertIn("got 'minor'", message)
        self.assertIn("allowed: none, single-state, multi-state", message)

    def test_invalid_ui_states_lists_allowed_values(self):
        message = gc.delivery_ui_error({"impact": "single-state", "states": ["ready"], "evidence": ["x"]})
        self.assertIn("loading, empty, error, success", message)

    def test_impact_none_with_states_says_how_to_fix(self):
        message = gc.delivery_ui_error({"impact": "none", "states": ["success"], "evidence": []})
        self.assertTrue(message.startswith("delivery UI states/evidence must be empty when impact is none"))
        self.assertIn("set both to []", message)

    def test_valid_non_ui_decision_still_passes(self):
        self.assertIsNone(gc.delivery_ui_error({"impact": "none", "states": [], "evidence": []}))

    def test_budget_and_architecture_name_missing_and_unexpected_keys(self):
        budgets = {"maxImplementationFiles": 2, "maxAffectedComponents": 1, "maxFiles": 3}
        message = gc.delivery_budgets_error(budgets)
        self.assertIn("missing: maxPublicInterfaceChanges, maxRuntimeDependencies", message)
        self.assertIn("unexpected: maxFiles", message)
        self.assertIn("missing:", gc.delivery_architecture_error({"status": "accepted"}))

    def test_delivery_fields_hint_ignores_allowed_optional_fields(self):
        message = gc.delivery_intent_error({"standardAdoption": {}, "outcome": "x"})
        self.assertIn("missing: acceptedBaseSha", message)
        self.assertNotIn("standardAdoption", message.split("unexpected:")[-1] if "unexpected:" in message else "")

    def test_bundled_copy_is_identical(self):
        bundled = SOURCE / "packages/wellman/src/wellman/_bundled/governance_check.py"
        self.assertEqual(bundled.read_bytes(), (SOURCE / "scripts/governance_check.py").read_bytes())


if __name__ == "__main__":
    unittest.main()
