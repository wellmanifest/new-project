#!/usr/bin/env python3
"""Integration coverage for canonical file-backed ticket allocation."""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class TicketAllocationWorktreeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="new-project-ticket-allocation-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "repository"
        self.root.mkdir()
        self.git("init", "-b", "main")
        self.git("config", "user.name", "Fixture")
        self.git("config", "user.email", "fixture@example.invalid")
        (self.root / "project").mkdir()
        (self.root / ".governance").mkdir()
        shutil.copy2(ROOT / "project/new-ticket.sh", self.root / "project/new-ticket.sh")
        shutil.copy2(ROOT / "project/readme.sh", self.root / "project/readme.sh")
        shutil.copytree(ROOT / "template/files", self.root / "template/files")
        for name in ("manifest.default.json", "work-classification.dsl.json", "ticket-activity.json"):
            source = ROOT / "governance" / name
            target = self.root / ".governance" / ("manifest.json" if name == "manifest.default.json" else name)
            shutil.copy2(source, target)
        for name in ("ticket_activity.py", "ticket_input.py", "work_start_check.py", "worktree_overlap_check.py"):
            shutil.copy2(ROOT / "scripts" / name, self.root / ".governance" / name)
        shutil.copy2(ROOT / "subprojects/worktrees/conformance.py", self.root / ".governance/worktree_path_check.py")
        (self.root / ".gitignore").write_text("/.worktrees/\n/.subactor/leases/\n", encoding="utf-8")
        (self.root / "README.md").write_text("fixture\n", encoding="utf-8")
        self.git("add", ".")
        self.git("commit", "-m", "fixture baseline")

    def git(self, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
        return subprocess.run(["git", *args], cwd=self.root, check=check, text=True,
                              capture_output=True, env={key: value for key, value in os.environ.items()
                                                         if not key.startswith("GIT_")})

    def allocate(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["bash", "project/new-ticket.sh", "--title", "Canonical ticket", "--agent", "codex",
             "--workstream", "application", "--worktree-slug", "canonical-ticket"],
            cwd=self.root, text=True, capture_output=True,
            env={key: value for key, value in os.environ.items() if not key.startswith("GIT_")},
        )

    def test_file_ticket_is_created_only_in_canonical_linked_worktree(self) -> None:
        result = self.allocate()
        self.assertEqual(result.returncode, 0, result.stderr)
        worktree = self.root / ".worktrees/ticket-001--canonical-ticket"
        self.assertTrue(worktree.is_dir())
        self.assertFalse((self.root / "project/ticket-001").exists())
        self.assertTrue((worktree / "project/ticket-001/README.md").is_file())
        intent = json.loads((worktree / "project/ticket-001/intent.json").read_text(encoding="utf-8"))
        self.assertEqual(intent["ticket"], "ticket-001")
        self.assertEqual(self.git("-C", str(worktree), "branch", "--show-current").stdout.strip(),
                         "ticket/001-canonical-ticket")
        registration = (worktree / ".git").read_text(encoding="utf-8")
        self.assertNotIn(str(self.root), registration)
        self.assertEqual((self.root / ".git/new-project-ticket-high-water").read_text().strip(), "1")
        lease = self.root / ".subactor/leases/ticket-001--canonical-ticket.json"
        self.assertTrue(lease.is_file())
        payload = json.loads(lease.read_text(encoding="utf-8"))
        self.assertEqual(payload["ticketId"], "ticket-001")
        self.assertEqual(payload["branchRef"], "refs/heads/ticket/001-canonical-ticket")
        self.assertEqual(payload["worktreeId"], "ticket-001--canonical-ticket")
        verified = subprocess.run([sys.executable, str(ROOT / "scripts/change_lease_check.py"),
                                   "validate", str(lease)], text=True, capture_output=True)
        self.assertEqual(verified.returncode, 0, verified.stderr)
        self.assertEqual(self.git("status", "--porcelain").stdout, "")

    def test_symlinked_canonical_component_fails_before_ticket_reservation(self) -> None:
        outside = Path(self.temp.name) / "outside"
        outside.mkdir()
        (self.root / ".worktrees").symlink_to(outside, target_is_directory=True)
        result = self.allocate()
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.root / "project/ticket-001").exists())
        self.assertFalse((self.root / ".git/new-project-ticket-high-water").exists())
        self.assertFalse((outside / "ticket-001--canonical-ticket").exists())

    def test_linked_checkout_request_still_materializes_only_in_primary_layout(self) -> None:
        first = self.allocate()
        self.assertEqual(first.returncode, 0, first.stderr)
        linked = self.root / ".worktrees/ticket-001--canonical-ticket"
        second = subprocess.run(
            ["bash", "project/new-ticket.sh", "--title", "Second ticket", "--agent", "codex",
             "--workstream", "application", "--worktree-slug", "second-ticket"],
            cwd=linked, text=True, capture_output=True,
            env={key: value for key, value in os.environ.items() if not key.startswith("GIT_")},
        )
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertTrue((self.root / ".worktrees/ticket-002--second-ticket/project/ticket-002").is_dir())
        self.assertFalse((linked / "project/ticket-002").exists())
        self.assertFalse((self.root / "project/ticket-002").exists())
        self.assertEqual((self.root / ".git/new-project-ticket-high-water").read_text().strip(), "2")


if __name__ == "__main__":
    unittest.main()
