#!/usr/bin/env python3
"""Reserved-ticket restoration in disposable local Git/controller fixtures only."""
from datetime import datetime, timedelta, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import ticket_recovery as recovery
import ticket_restoration as restoration
import work_start_check as start

spec = importlib.util.spec_from_file_location("start_fixtures", ROOT / "tests/work_start_test.py")
fixtures = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixtures)
BRANCH = "refs/heads/ticket/001-fixture"


class RestorationTest(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.WorkStartTest()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.primary = self.fixture.root
        self.git = self.fixture.git
        self.git(self.primary, "remote", "add", "origin", "https://github.com/example/project.git")
        for name in ("ticket_restoration.py", "ticket_recovery.py", "ticket_allocation.py"):
            shutil.copy2(ROOT / "scripts" / name, self.primary / ".governance" / name)
        (self.primary / ".governance/ticket-allocation.json").write_text(json.dumps({
            "$schema": "ticket-allocation.schema.json", "schema": "new-project.ticket-allocation/v1",
            "mode": "local-single-clone"}))
        self.git(self.primary, "add", ".")
        self.git(self.primary, "commit", "-m", "restoration helper")
        self.base = self.git(self.primary, "rev-parse", "HEAD")
        self.temp = Path(self.fixture.temp.name)
        self.checkout = self.primary / ".worktrees/ticket-001--fixture"
        self.git(self.primary, "worktree", "add", "--relative-paths", "-b", "ticket/001-fixture",
                 str(self.checkout), self.base)
        (self.primary / ".git/new-project-ticket-high-water").write_text("1\n")
        self.intent = {
            "schema": "new-project.intent/v3", "ticket": "ticket-001", "summary": "Restore fixture",
            "workstream": "api", "classification": {"kind": "BUG", "priority": "P1", "origin": "health"},
            "allowedPaths": ["project/ticket-001/**", "api/**"],
            "forbiddenPaths": ["project/ticket-*/user-*.md"], "stacks": [],
            "dependsOn": [], "conflictsWith": [], "integrationTicket": None}
        self.files = {"README.md": "# Ticket 001: Restore fixture\n\n- **Status**: IN_PROGRESS\n",
                      "intent.json": json.dumps(self.intent, indent=2) + "\n"}
        record = dict(schema="wellmanifest.change-lease/v1", leaseId="allocation-ticket-001-fixture",
                      ticketId="ticket-001", worktreeId="ticket-001--fixture", workstream="api",
                      branchRef=BRANCH, targetBranch="main", ownerActor="fixture",
                      ownerSession="fixture-session", headSha=self.base, phase="claimed")
        leases = self.primary / ".subactor/leases"
        leases.mkdir(parents=True)
        self.record_path = leases / "ticket-001--fixture.json"
        self.record_path.write_text(json.dumps(record))
        self.store = self.temp / "controller"
        self.store.mkdir()
        (self.store / ".lock").touch()
        self.lease = dict(schema="wellmanifest.change-lease/v1", leaseId="lease-fixture", leaseRevision=2,
                          fencingToken=7, ownerActor="fixture", ownerSession="fixture-session",
                          repositoryRef="example/project", ticketId="ticket-001", targetBranch="main",
                          branchRef=BRANCH, workstream="api", worktreeId="ticket-001--fixture",
                          scopeHash=start.digest(self.intent["allowedPaths"]), phase="claimed",
                          publicationFrozen=False,
                          expiresAt=(datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat())
        resource = start.digest({"repositoryRef": "example/project", "targetBranch": "main"})
        self.state = dict(schema="subactor.repository-change-lease-store/v1",
                          leases={"lease-fixture": self.lease}, active={resource: "lease-fixture"})
        self.snapshot_path = self.temp / "snapshot.json"
        self.request_path = self.temp / "request.json"
        self.request = dict(schema="new-project.ticket-restoration-request/v1", ticket="ticket-001",
                            worktreeId="ticket-001--fixture", headSha=None, snapshotPath=str(self.snapshot_path),
                            snapshotSha256="", leaseId="lease-fixture", leaseRevision=2, fencingToken=7,
                            ownerActor="fixture", ownerSession="fixture-session")
        self.lose(branch=False)

    def lose(self, branch=True):
        self.git(self.primary, "worktree", "remove", "--force", str(self.checkout))
        if branch:
            self.git(self.primary, "branch", "-D", "ticket/001-fixture")

    def persist(self, snapshot=None):
        raw = json.dumps(snapshot or {"schema": "new-project.ticket-metadata-snapshot/v1",
                                      "ticket": "ticket-001", "files": self.files}).encode()
        self.snapshot_path.write_bytes(raw)
        self.request.setdefault("snapshotSha256", "")
        if not self.request.pop("keepDigest", False):
            self.request["snapshotSha256"] = hashlib.sha256(raw).hexdigest()
        self.request_path.write_text(json.dumps(self.request))
        (self.store / "state.json").write_text(json.dumps(self.state))

    def restore(self):
        return restoration.restore(self.primary, self.request_path, self.store, "api")

    def run_allocator(self):
        return subprocess.run(["bash", "project/new-ticket.sh", "--workstream", "api",
                               "--restore-request", str(self.request_path), "--recovery-lease-store", str(self.store)],
                              cwd=self.primary, capture_output=True, text=True)

    def assert_metadata(self):
        for name, content in self.files.items():
            self.assertEqual((self.checkout / "project/ticket-001" / name).read_text(), content)

    def reject(self, snapshot=None):
        self.persist(snapshot)
        heads = self.git(self.primary, "for-each-ref", "refs/heads")
        with self.assertRaises(recovery.RecoveryError):
            self.restore()
        self.assertEqual(self.git(self.primary, "for-each-ref", "refs/heads"), heads)
        self.assertNotIn(str(self.checkout), self.git(self.primary, "worktree", "list"))
        self.assertEqual((self.primary / ".git/new-project-ticket-high-water").read_text(), "1\n")
        self.assertFalse((self.primary / ".git/new-project-ticket-allocation.lock").exists())

    def test_checkout_loss_restores_same_identity_idempotently(self):
        self.persist()
        result = self.restore()
        self.assertEqual((result["outcome"], result["steps"]), ("RESTORED", ["checkout", "README.md", "intent.json"]))
        self.assertFalse(result["grantsEditAuthority"] or result["grantsMergeAuthority"])
        self.assert_metadata()
        self.assertEqual((self.primary / ".git/new-project-ticket-high-water").read_text(), "1\n")
        backlink = Path(self.git(self.checkout, "rev-parse", "--absolute-git-dir")) / "gitdir"
        self.assertFalse(Path(backlink.read_text().strip()).is_absolute())
        again = self.restore()
        self.assertEqual((again["outcome"], again["steps"]), ("ALREADY_RESTORED", []))

    def test_branch_and_metadata_loss_through_allocator(self):
        self.git(self.primary, "branch", "-D", "ticket/001-fixture")
        self.persist()
        result = self.run_allocator()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["steps"], ["branch", "checkout", "README.md", "intent.json"])
        self.assertEqual(self.git(self.primary, "rev-parse", BRANCH), self.base)
        self.assert_metadata()
        self.assertEqual(sorted(p.name for p in (self.primary / ".subactor/leases").iterdir()),
                         ["ticket-001--fixture.json"])

    def test_bound_reachable_head_and_committed_metadata(self):
        self.git(self.primary, "worktree", "add", "--relative-paths", str(self.checkout), "ticket/001-fixture")
        (self.checkout / "project/ticket-001").mkdir(parents=True)
        for name, content in self.files.items():
            (self.checkout / "project/ticket-001" / name).write_text(content)
        (self.checkout / "api/a.txt").write_text("material work\n")
        self.git(self.checkout, "add", ".")
        self.git(self.checkout, "commit", "-m", "work")
        head = self.git(self.checkout, "rev-parse", "HEAD")
        self.lose()
        self.request["headSha"] = head
        self.persist()
        result = self.restore()
        self.assertEqual((result["steps"], result["metadata"]), (["branch", "checkout"], "committed"))
        self.assertEqual(self.git(self.primary, "rev-parse", BRANCH), head)
        self.assertEqual((self.checkout / "api/a.txt").read_text(), "material work\n")

    def test_interrupted_restoration_resumes(self):
        self.persist()
        original = restoration.write_new
        def interrupt(common, path, content):
            if path.name == "intent.json":
                raise OSError("interrupted")
            return original(common, path, content)
        with patch.object(restoration, "write_new", side_effect=interrupt):
            with self.assertRaises(OSError):
                self.restore()
        self.assertFalse((self.primary / ".git/new-project-ticket-allocation.lock").exists())
        result = self.restore()
        self.assertEqual(result["steps"], ["intent.json"])
        self.assert_metadata()
        self.assertEqual(list((self.primary / ".git").glob("new-project-ticket-restore-*")), [])

    def test_mismatched_reservation(self):
        record = json.loads(self.record_path.read_text())
        for field, value in (("ownerSession", "foreign"), ("workstream", "ui"), ("branchRef", "refs/heads/main")):
            with self.subTest(field=field):
                self.record_path.write_text(json.dumps({**record, field: value}))
                self.reject()
        self.record_path.write_text(json.dumps(record))
        (self.primary / ".git/new-project-ticket-high-water").write_text("0\n")
        with self.assertRaises(recovery.RecoveryError):
            self.persist()
            self.restore()
        (self.primary / ".git/new-project-ticket-high-water").write_text("1\n")
        (self.primary / ".subactor/leases/ticket-001--other.json").write_text(json.dumps(record))
        self.reject()

    def test_tampered_or_terminal_snapshot(self):
        self.request["snapshotSha256"] = "0" * 64
        self.request["keepDigest"] = True
        self.reject()
        self.reject({"schema": "new-project.ticket-metadata-snapshot/v1", "ticket": "ticket-001",
                     "files": {**self.files, "../api/a.txt": "source"}})
        self.files["README.md"] = "# Ticket 001\n\n- **Status**: DONE\n"
        self.reject()

    def test_foreign_or_expired_owner(self):
        for field, value in (("ownerSession", "foreign"), ("phase", "validating"), ("fencingToken", 8),
                             ("scopeHash", "0" * 64), ("expiresAt", "2000-01-01T00:00:00+00:00")):
            with self.subTest(field=field):
                self.state["leases"]["lease-fixture"] = {**self.lease, field: value}
                self.reject()
        self.state["leases"]["lease-fixture"] = self.lease
        self.state["active"] = {key: "other-live-lease" for key in self.state["active"]}
        self.reject()

    def test_collisions_are_never_overwritten(self):
        self.checkout.mkdir(parents=True)
        self.reject()
        self.checkout.rmdir()
        self.git(self.primary, "worktree", "add", "--relative-paths", str(self.temp / "elsewhere"), "ticket/001-fixture")
        self.reject()
        self.git(self.primary, "worktree", "remove", "--force", str(self.temp / "elsewhere"))
        self.git(self.primary, "branch", "ticket/001-duplicate", self.base)
        self.reject()
        self.git(self.primary, "branch", "-D", "ticket/001-duplicate")
        self.git(self.primary, "worktree", "add", "--relative-paths", str(self.checkout), "ticket/001-fixture")
        (self.checkout / "project/ticket-001").mkdir(parents=True)
        (self.checkout / "project/ticket-001/intent.json").write_text("{}\n")
        self.persist()
        with self.assertRaises(recovery.RecoveryError):
            self.restore()
        self.assertEqual((self.checkout / "project/ticket-001/intent.json").read_text(), "{}\n")

    def test_symlinked_checkout_and_sqlite_rejected(self):
        (self.temp / "target").mkdir()
        (self.primary / ".worktrees").mkdir(exist_ok=True)
        self.checkout.symlink_to(self.temp / "target")
        self.reject()
        self.checkout.unlink()
        (self.primary / "project.sqlite").touch()
        self.reject()


if __name__ == "__main__":
    unittest.main()
