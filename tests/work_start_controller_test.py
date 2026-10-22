#!/usr/bin/env python3
"""Read-only controller availability next to work-start; disposable fixtures only."""
from datetime import datetime, timedelta, timezone
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import work_start_check as start
import jsonschema

spec = importlib.util.spec_from_file_location("start_fixtures", ROOT / "tests/work_start_test.py")
fixtures = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixtures)
SCHEMA = json.loads((ROOT / "governance/work-start-report.schema.json").read_text())


class ControllerObservationTest(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.WorkStartTest()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.store = Path(self.fixture.temp.name) / "controller"
        self.store.mkdir()
        self.resource = start.digest({"repositoryRef": "example/project", "targetBranch": "main"})
        self.lease = {"leaseId": "lease-1", "ticketId": "ticket-001", "phase": "editing",
                      "ownerActor": "agent:other", "ownerSession": "private-session", "planHash": "0" * 64,
                      "expiresAt": (datetime.now(timezone.utc) + timedelta(minutes=10)).isoformat()}
        self.write({"lease-1": self.lease}, {self.resource: "lease-1"})

    def write(self, leases, active, schema="subactor.repository-change-lease-store/v1"):
        (self.store / "state.json").write_text(json.dumps(
            {"schema": schema, "nextFencingToken": 1, "leases": leases, "active": active,
             "acquisitions": {}, "requests": {}, "evidence": {}, "identities": {}}))

    def observe(self, stream="ui", ticket=None):
        report = start.inspect(self.fixture.root, stream, (), ticket,
                               controller=(self.store, "example/project"))
        jsonschema.validate(report, SCHEMA)
        self.assertFalse(report["grantsAuthority"] or report["editingResource"]["grantsAuthority"])
        return report

    def test_disjoint_scope_is_still_serialized_by_the_resource(self):
        self.fixture.sibling(1, "api")
        before = sorted(p.name for p in self.store.iterdir())
        report = self.observe("ui")
        self.assertEqual(report["route"], "NEW_TICKET_CANDIDATE")
        resource = report["editingResource"]
        self.assertEqual((resource["state"], resource["holder"]["ticketId"]), ("HELD_BY_OTHER", "ticket-001"))
        self.assertNotIn("private-session", json.dumps(report))
        self.assertNotIn("agent:other", json.dumps(report))
        self.assertEqual(sorted(p.name for p in self.store.iterdir()), before)

    def test_holder_states(self):
        self.fixture.sibling(1, "api")
        self.assertEqual(self.observe("api", "ticket-001")["editingResource"]["state"], "HELD_BY_TICKET")
        past = (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat()
        for change, expected in (({"expiresAt": past}, "HELD_EXPIRED"), ({"phase": "expired"}, "HELD_EXPIRED"),
                                 ({"phase": "released"}, "AVAILABLE"), ({"phase": "claimed"}, "HELD_BY_OTHER")):
            with self.subTest(change=change):
                self.write({"lease-1": {**self.lease, **change}}, {self.resource: "lease-1"})
                self.assertEqual(self.observe()["editingResource"]["state"], expected)
        self.write({}, {})
        resource = self.observe()["editingResource"]
        self.assertEqual((resource["state"], resource["holder"], resource["reason"]), ("AVAILABLE", None, None))
        self.assertRegex(resource["stateDigest"], "^[0-9a-f]{64}$")

    def test_unavailable_reasons_never_report_availability(self):
        self.write({}, {self.resource: "missing-lease"})
        self.assertEqual(self.observe()["editingResource"]["reason"], "controller-state-invalid")
        self.write({}, {}, schema="other/v1")
        self.assertEqual(self.observe()["editingResource"]["reason"], "controller-state-invalid")
        original = start._controller_bytes
        calls = []
        def racing(store):
            calls.append(True)
            return original(store) + (b" " if len(calls) > 1 else b"")
        self.write({}, {})
        with patch.object(start, "_controller_bytes", side_effect=racing):
            self.assertEqual(self.observe()["editingResource"]["reason"], "controller-state-changed")
        (self.store / "state.json").unlink()
        (self.store / "state.json").symlink_to(self.store / "elsewhere.json")
        self.assertEqual(self.observe()["editingResource"]["reason"], "controller-state-unreadable")
        (self.store / "state.json").unlink()
        resource = self.observe()["editingResource"]
        self.assertEqual((resource["state"], resource["reason"]), ("UNAVAILABLE", "controller-store-missing"))
        self.assertIn("do not infer availability", resource["nextAction"])

    def test_cli_requires_exact_repository_binding(self):
        script = str(self.fixture.root / ".governance/work_start_check.py")
        base = [sys.executable, script, "--root", str(self.fixture.root), "--workstream", "ui"]
        for extra in (["--controller-store", str(self.store)],
                      ["--controller-store", str(self.store), "--controller-repository", "not a ref"]):
            self.assertEqual(subprocess.run(base + extra, capture_output=True).returncode, 2)
        result = subprocess.run(base + ["--controller-store", str(self.store),
                                        "--controller-repository", "example/project"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["editingResource"]["state"], "HELD_BY_OTHER")


if __name__ == "__main__":
    unittest.main()
