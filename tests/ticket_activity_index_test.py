#!/usr/bin/env python3
"""A squash or rebase onto a newer base records its receipt although the generated index hunk vanished (issue #524)."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
INDEX_HEAD = "| Ticket ID | Spec |\n| :--- | :--- |\n| **ticket-009** | [`README.md`](./ticket-009/README.md) |\n"


class GeneratedIndexReceiptTest(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="ticket-activity-index-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name) / "repo"
        self.git("init", "-q", "-b", "main", str(self.root), cwd=temp.name)
        for key, value in (("user.name", "fixture"), ("user.email", "f@example.invalid"), ("commit.gpgsign", "false")):
            self.git("config", key, value)
        (self.root / "governance").mkdir()
        shutil.copy2(ROOT / "governance/ticket-activity.json", self.root / "governance/ticket-activity.json")
        self.write("README.md", "# sample\n")
        self.write("project/TICKETS.md", "# index\n")
        self.base = self.commit("base")
        # Two sibling tickets on one base: each regenerates the index with the same lagging row.
        self.a = self.ticket("010", "a.txt")
        self.git("switch", "-q", "--detach", self.base)
        self.b = self.ticket("011", "b.txt")
        self.git("switch", "-q", "-C", "main", self.base)
        self.git("merge", "-q", "--squash", self.a)
        self.commit("squash ticket-010")  # main now carries the index row

    def git(self, *args, cwd=None):
        return subprocess.run(["git", *args], cwd=cwd or self.root, check=True,
                              capture_output=True, text=True).stdout.strip()

    def write(self, rel, text, mode="w"):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open(mode) as handle:
            handle.write(text)

    def commit(self, message):
        self.git("add", "-A")
        self.git("commit", "-qm", message)
        return self.git("rev-parse", "HEAD")

    def ticket(self, number, material):
        self.write(f"project/ticket-{number}/README.md", "- **Status**: IN_PROGRESS\n")
        self.write(material, f"ticket-{number}\n")
        self.write("project/TICKETS.md", INDEX_HEAD, mode="a")
        return self.commit(f"ticket-{number}")

    def record(self, head, terminal, ref):
        receipt = Path(self.root.parent) / f"{ref}.json"
        receipt.write_text(json.dumps({
            "receiptRef": f"receipt:test/index/{ref}", "ticket": "ticket-011", "outcome": "merged",
            "headSha": head, "terminalSha": terminal, "targetBranch": "main",
            "occurredAt": "2026-10-22T15:00:00Z"}))
        return subprocess.run([sys.executable, str(ROOT / "scripts/ticket_activity.py"), "--root", str(self.root),
                               "record", "--receipt", str(receipt)], capture_output=True, text=True)

    def test_squash_onto_newer_base_records_without_the_index_hunk(self):
        self.git("merge", "-q", "--squash", self.b)
        terminal = self.commit("squash ticket-011")
        self.assertEqual(self.git("diff", "--name-only", f"{terminal}^", terminal).split(), ["b.txt", "project/ticket-011/README.md"])
        result = self.record(self.b, terminal, "squash")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_rebase_onto_newer_base_records_without_the_index_hunk(self):
        self.git("cherry-pick", "--allow-empty", self.b)
        terminal = self.git("rev-parse", "HEAD")
        self.assertNotIn("project/TICKETS.md", self.git("diff", "--name-only", f"{terminal}^", terminal))
        result = self.record(self.b, terminal, "rebase")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_any_authored_difference_is_still_refused(self):
        self.git("merge", "-q", "--squash", self.b)
        self.write("b.txt", "tampered\n")
        terminal = self.commit("squash ticket-011 with a different authored change")
        self.assertEqual(self.record(self.b, terminal, "tampered").returncode, 2)

    def test_an_extra_authored_path_is_still_refused(self):
        self.git("merge", "-q", "--squash", self.b)
        self.write("extra.txt", "smuggled\n")
        terminal = self.commit("squash ticket-011 with an extra path")
        self.assertEqual(self.record(self.b, terminal, "extra").returncode, 2)


if __name__ == "__main__":
    unittest.main()
