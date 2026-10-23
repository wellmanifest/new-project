#!/usr/bin/env python3
"""Manifest idle-takeover policy and the lease contract's worktree layout roots."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


governance = load("idle_policy_governance", ROOT / "scripts/governance_check.py")
lease = load("idle_policy_lease", ROOT / "scripts/change_lease_check.py")


class IdleTakeoverPolicyTest(unittest.TestCase):
    def coordination(self, name):
        return json.loads((ROOT / "governance" / name).read_text())["coordination"]

    def test_shipped_manifests_enable_fifteen_minutes(self):
        for name in ("manifest.default.json", "manifest.hub.json"):
            coordination = self.coordination(name)
            self.assertEqual(coordination["idleTakeover"], {"enabled": True, "idleMinutes": 15, "leaseMinutes": 120})
            self.assertTrue(governance.coordination_policy_valid(coordination), name)
        self.assertEqual(self.coordination("manifest.hub.json")["maxActiveTicketsPerWorkstream"], 2)

    def test_policy_is_optional(self):
        coordination = self.coordination("manifest.default.json")
        del coordination["idleTakeover"]
        self.assertTrue(governance.coordination_policy_valid(coordination))

    def test_invalid_policies_are_rejected(self):
        base = self.coordination("manifest.default.json")
        for policy in ({"enabled": True, "idleMinutes": 4, "leaseMinutes": 120},
                       {"enabled": True, "idleMinutes": 241, "leaseMinutes": 480},
                       {"enabled": True, "idleMinutes": 60, "leaseMinutes": 60},
                       {"enabled": "yes", "idleMinutes": 15, "leaseMinutes": 120},
                       {"enabled": True, "idleMinutes": True, "leaseMinutes": 120},
                       {"enabled": True, "idleMinutes": 15},
                       {"enabled": True, "idleMinutes": 15, "leaseMinutes": 120, "extra": 1}):
            coordination = deepcopy(base)
            coordination["idleTakeover"] = policy
            self.assertFalse(governance.coordination_policy_valid(coordination), policy)
        coordination = deepcopy(base)
        coordination["unknown"] = True
        self.assertFalse(governance.coordination_policy_valid(coordination))

    def test_schema_declares_the_same_closed_policy(self):
        schema = json.loads((ROOT / "governance/manifest.schema.json").read_text())
        policy = schema["properties"]["coordination"]["properties"]["idleTakeover"]
        self.assertFalse(policy["additionalProperties"])
        self.assertEqual(sorted(policy["required"]), ["enabled", "idleMinutes", "leaseMinutes"])
        self.assertEqual((policy["properties"]["idleMinutes"]["minimum"], policy["properties"]["idleMinutes"]["maximum"]), (5, 240))

    def test_lease_contract_exports_worktree_layout(self):
        self.assertEqual((lease.WORKTREES_ROOT, lease.LEASE_ROOT, lease.MAX_LEASE_BYTES),
                         (".worktrees", ".subactor/leases", 65536))
        source = (ROOT / "scripts/change_lease_check.py").read_text()
        self.assertNotIn('primary / ".worktrees"', source)
        self.assertNotIn('".subactor/leases" /', source)
        bundled = ROOT / "packages/wellman/src/wellman/_bundled/change_lease_check.py"
        self.assertEqual(bundled.read_text(), source)


if __name__ == "__main__":
    unittest.main()
