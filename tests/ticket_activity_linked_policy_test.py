#!/usr/bin/env python3
"""A linked checkout with a newer activity policy stays reserved; the primary still fails closed."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import ticket_activity  # noqa: E402

ACTIVE = {"IN_PROGRESS"}
NEWER = {"verification": "a-future-verification", "releasesReservation": True}


class LinkedCheckoutPolicySkewTest(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="ticket-activity-linked-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name) / "repo"
        self.git("init", "-q", "-b", "main", str(self.root), cwd=temp.name)
        for key, value in (("user.name", "fixture"), ("user.email", "f@example.invalid"), ("commit.gpgsign", "false")):
            self.git("config", key, value)
        (self.root / "governance").mkdir()
        shutil.copy2(ROOT / "governance/ticket-activity.json", self.root / "governance/ticket-activity.json")
        self.status(self.root, "010")
        self.git("add", "-A")
        self.git("commit", "-qm", "base")
        self.linked = self.root / ".worktrees" / "ticket-011--adopt"
        self.git("worktree", "add", "-q", "-b", "ticket/011-adopt", str(self.linked))
        self.status(self.linked, "011")
        self.newer_policy(self.linked)

    def git(self, *args, cwd=None):
        return subprocess.run(["git", *args], cwd=cwd or self.root, check=True,
                              capture_output=True, text=True).stdout.strip()

    @staticmethod
    def status(root, number):
        ticket = root / "project" / f"ticket-{number}"
        ticket.mkdir(parents=True, exist_ok=True)
        (ticket / "README.md").write_text("- **Status**: IN_PROGRESS\n")

    @staticmethod
    def newer_policy(root):
        path = root / "governance/ticket-activity.json"
        value = json.loads(path.read_text())
        value["terminalOutcomes"]["future"] = NEWER
        path.write_text(json.dumps(value, indent=2) + "\n")

    def test_linked_checkout_with_newer_policy_stays_reserved(self):
        result = ticket_activity.resolve(self.linked, self.linked / "project/ticket-011", ACTIVE)
        self.assertTrue(result.active)
        self.assertEqual(result.authority, "status-projection")
        self.assertEqual(result.reason, "checkout-policy-unsupported")

    def test_inactive_projection_is_still_inactive(self):
        (self.linked / "project/ticket-011/README.md").write_text("- **Status**: DONE\n")
        result = ticket_activity.resolve(self.linked, self.linked / "project/ticket-011", ACTIVE)
        self.assertFalse(result.active)

    def test_primary_checkout_policy_still_fails_closed(self):
        self.newer_policy(self.root)
        with self.assertRaises(ticket_activity.ActivityError):
            ticket_activity.resolve(self.root, self.root / "project/ticket-010", ACTIVE)

    def test_supported_policy_in_linked_checkout_is_unchanged(self):
        shutil.copy2(ROOT / "governance/ticket-activity.json", self.linked / "governance/ticket-activity.json")
        result = ticket_activity.resolve(self.linked, self.linked / "project/ticket-011", ACTIVE)
        self.assertNotEqual(result.reason, "checkout-policy-unsupported")


if __name__ == "__main__":
    unittest.main()
