#!/usr/bin/env python3
"""Integration coverage for canonical file-backed ticket allocation."""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


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
        self.git("config", "core.excludesFile", os.devnull)
        (self.root / "project").mkdir()
        (self.root / ".governance").mkdir()
        shutil.copy2(ROOT / "project/new-ticket.sh", self.root / "project/new-ticket.sh")
        shutil.copy2(ROOT / "project/readme.sh", self.root / "project/readme.sh")
        shutil.copytree(ROOT / "template/files", self.root / "template/files")
        for name in ("manifest.default.json", "work-classification.dsl.json", "ticket-activity.json"):
            source = ROOT / "governance" / name
            target = self.root / ".governance" / ("manifest.json" if name == "manifest.default.json" else name)
            shutil.copy2(source, target)
        for name in ("ticket_activity.py", "ticket_input.py", "work_start_check.py", "worktree_overlap_check.py",
                     "ticket_storage.py", "governance_check.py", "repository_policy.py"):
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

    def allocate(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["bash", "project/new-ticket.sh", "--title", "Canonical ticket", "--agent", "codex",
             "--workstream", "application", "--worktree-slug", "canonical-ticket", *args],
            cwd=self.root, text=True, capture_output=True,
            env={key: value for key, value in os.environ.items() if not key.startswith("GIT_")},
        )

    def test_file_ticket_is_created_only_in_canonical_linked_worktree(self) -> None:
        result = self.allocate()
        self.assertEqual(result.returncode, 0, result.stderr)
        receipts = [json.loads(line) for line in result.stdout.splitlines()
                    if line.startswith('{')]
        self.assertEqual(len(receipts), 1, result.stdout)
        receipt = receipts[0]
        self.assertEqual(receipt['schema'], 'new-project.ticket-allocation-result/v1')
        self.assertEqual(receipt['ticket'], 'ticket-001')
        self.assertEqual(receipt['branch'], 'ticket/001-canonical-ticket')
        self.assertEqual(receipt['worktreePath'], str(self.root / '.worktrees/ticket-001--canonical-ticket'))
        self.assertEqual(receipt['leasePath'], str(self.root / '.subactor/leases/ticket-001--canonical-ticket.json'))
        self.assertEqual(receipt['storage'], 'files')
        self.assertEqual(receipt['kind'], 'delivery')
        self.assertFalse(receipt['executionAuthorized'])
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
        self.assertNotIn('new-project.ticket-allocation-result/v1', result.stdout)
        self.assertFalse((self.root / "project/ticket-001").exists())
        self.assertFalse((self.root / ".git/new-project-ticket-high-water").exists())
        self.assertFalse((outside / "ticket-001--canonical-ticket").exists())

    def dirty_primary(self) -> dict[str, bytes]:
        (self.root / "src").mkdir()
        (self.root / "src/other.py").write_text("original\n")
        self.git("add", "src/other.py")
        self.git("commit", "-m", "tracked unrelated source")
        (self.root / "src/other.py").write_text("staged change\n")
        self.git("add", "src/other.py")
        (self.root / "src/other.py").write_text("unstaged change\n")
        (self.root / ".planfile").mkdir()
        (self.root / ".planfile/current.yaml").write_text("operational: unchanged\n")
        return {name: (self.root / name).read_bytes()
                for name in ("src/other.py", ".planfile/current.yaml", ".git/index")}

    def test_scoped_allocation_preserves_unrelated_dirty_primary(self) -> None:
        before = self.dirty_primary()
        status = self.git("status", "--porcelain=v1", "--untracked-files=all").stdout
        head = self.git("rev-parse", "HEAD").stdout.strip()
        result = self.allocate("--path", "src/fix.py")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        for name, content in before.items():
            self.assertEqual((self.root / name).read_bytes(), content, name)
        self.assertEqual(self.git("status", "--porcelain=v1", "--untracked-files=all").stdout, status)
        self.assertEqual(self.git("rev-parse", "HEAD").stdout.strip(), head)
        self.assertEqual(self.git("branch", "--show-current").stdout.strip(), "main")
        worktree = self.root / ".worktrees/ticket-001--canonical-ticket"
        self.assertEqual(self.git("-C", str(worktree), "rev-parse", "HEAD").stdout.strip(), head)
        self.assertEqual((worktree / "src/other.py").read_text(), "original\n")
        self.assertFalse((worktree / ".planfile/current.yaml").exists())

    def test_overlapping_dirty_primary_refused_without_reservation(self) -> None:
        before = self.dirty_primary()
        result = self.allocate("--path", "src/other.py")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("pending-delta", result.stdout + result.stderr)
        self.assertFalse((self.root / ".git/new-project-ticket-high-water").exists())
        self.assertEqual(self.git("branch", "--list", "ticket/*").stdout, "")
        for name, content in before.items():
            self.assertEqual((self.root / name).read_bytes(), content, name)

    def test_unscoped_dirty_primary_refused_without_reservation(self) -> None:
        (self.root / ".planfile").mkdir()
        (self.root / ".planfile/current.yaml").write_text("operational: unchanged\n")
        result = self.allocate()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("explicit", result.stderr)
        self.assertFalse((self.root / ".git/new-project-ticket-high-water").exists())
        self.assertEqual(self.git("branch", "--list", "ticket/*").stdout, "")
        self.assertEqual((self.root / ".planfile/current.yaml").read_text(), "operational: unchanged\n")

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


ALLOCATOR = ROOT / "project/new-ticket.sh"
SOURCE = ALLOCATOR.read_text()
LEASE_WRITER = SOURCE.split('from datetime import datetime, timedelta, timezone\n', 1)[1].split('\nPY\n', 1)[0]
LEASE_WRITER = 'from datetime import datetime, timedelta, timezone\n' + LEASE_WRITER


@unittest.skipUnless(hasattr(os, "O_NOFOLLOW") and hasattr(os, "O_DIRECTORY"),
                     "POSIX directory-descriptor fixture")
class LeaseRaceTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='allocator-lease-race-')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name) / 'repository'
        self.root.mkdir()
        self.intent = self.root / 'intent.json'
        self.intent.write_text(json.dumps({'allowedPaths': ['src/fix.py']}))
        self.lease = self.root / '.subactor/leases/ticket-001--fixture.json'
        self.outside = Path(temporary.name) / 'outside'
        self.outside.mkdir()
        self.arguments = ['allocator-lease-writer', str(self.intent), str(self.lease),
                          'ticket-001', 'application', 'ticket/001-fixture', 'fixture',
                          'fixture/repository', 'main', 'a' * 40, 'fixture',
                          '2026-10-11T21:00:00Z']

    def execute(self):
        with patch.object(sys, 'argv', self.arguments):
            exec(compile(LEASE_WRITER, str(ALLOCATOR), 'exec'), {})

    def captured_execution(self):
        try:
            self.execute()
        except (OSError, SystemExit) as error:
            return error
        return None

    def test_normal_write_creates_private_valid_lease(self):
        self.execute()
        data = json.loads(self.lease.read_text())
        self.assertEqual(data['ticketId'], 'ticket-001')
        self.assertEqual(data['fencingToken'], 1)
        self.assertEqual(stat.S_IMODE(self.lease.stat().st_mode), 0o600)

    def test_existing_lease_is_never_overwritten(self):
        self.lease.parent.mkdir(parents=True)
        self.lease.write_bytes(b'original lease')
        self.assertIsNotNone(self.captured_execution())
        self.assertEqual(self.lease.read_bytes(), b'original lease')

    def test_existing_parent_symlink_creates_nothing_outside(self):
        (self.root / '.subactor').symlink_to(self.outside, target_is_directory=True)
        self.assertIsNotNone(self.captured_execution())
        self.assertEqual(list(self.outside.iterdir()), [])

    def test_parent_replacement_before_final_open_cannot_redirect_write(self):
        self.lease.parent.mkdir(parents=True)
        saved = self.lease.parent.with_name('leases-original')
        original_open = os.open
        attacked = []

        def racing_open(path, flags, *args, **kwargs):
            if flags & os.O_CREAT:
                self.lease.parent.rename(saved)
                self.lease.parent.symlink_to(self.outside, target_is_directory=True)
                attacked.append(True)
            return original_open(path, flags, *args, **kwargs)

        supported = (os.supports_dir_fd - {original_open}) | {racing_open}
        with patch.object(os, 'open', racing_open), patch.object(os, 'supports_dir_fd', supported):
            self.execute()
        self.assertEqual(attacked, [True])
        self.assertFalse((self.outside / self.lease.name).exists())
        self.assertTrue((saved / self.lease.name).is_file())

    def test_new_directory_replaced_before_traversal_is_rejected(self):
        (self.root / '.subactor').mkdir()
        saved = self.lease.parent.with_name('leases-original')
        original_mkdir = os.mkdir
        attacked = []

        def racing_mkdir(path, *args, **kwargs):
            result = original_mkdir(path, *args, **kwargs)
            if os.fspath(path) in {'leases', str(self.lease.parent)}:
                self.lease.parent.rename(saved)
                self.lease.parent.symlink_to(self.outside, target_is_directory=True)
                attacked.append(True)
            return result

        supported = (os.supports_dir_fd - {original_mkdir}) | {racing_mkdir}
        with patch.object(os, 'mkdir', racing_mkdir), patch.object(os, 'supports_dir_fd', supported):
            self.assertIsNotNone(self.captured_execution())
        self.assertEqual(attacked, [True])
        self.assertEqual(list(self.outside.iterdir()), [])

    def test_unsupported_host_fails_before_ticket_reservation(self):
        fixture = TicketAllocationWorktreeTest()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        shim = self.root / "shim"
        shim.mkdir()
        interpreter = shim / "python3"
        interpreter.write_text("#!" + sys.executable + "\n" + "\n".join([
            "import os, sys",
            "if sys.argv[1:] == ['-']:",
            "    code = sys.stdin.read()",
            "    if 'race-resistant lease creation is unsupported on this host' in code:",
            "        os.supports_dir_fd = set()",
            "    exec(compile(code, '<injected-host-capabilities>', 'exec'), {'__name__': '__main__'})",
            "else:",
            "    os.execv(sys.executable, [sys.executable, *sys.argv[1:]])",
        ]) + "\n")
        interpreter.chmod(0o755)
        before = fixture.git("status", "--porcelain").stdout
        with patch.dict(os.environ, {"PATH": str(shim) + os.pathsep + os.environ["PATH"]}):
            result = fixture.allocate()
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("race-resistant lease creation is unsupported", result.stderr)
        self.assertFalse((fixture.root / ".git/new-project-ticket-high-water").exists())
        self.assertEqual(fixture.git("branch", "--list", "ticket/*").stdout, "")
        self.assertFalse((fixture.root / ".subactor").exists())
        self.assertEqual(fixture.git("status", "--porcelain").stdout, before)

    def test_unsupported_directory_api_fails_before_lease_side_effects(self):
        with patch.object(os, 'supports_dir_fd', set()):
            self.assertIsNotNone(self.captured_execution())
        self.assertFalse((self.root / '.subactor').exists())



if __name__ == "__main__":
    unittest.main()
