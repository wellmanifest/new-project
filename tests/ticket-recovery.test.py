#!/usr/bin/env python3
"""Real allocator recovery in disposable local Git/controller fixtures only."""
from datetime import datetime, timedelta, timezone
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
import work_start_check as start

spec = importlib.util.spec_from_file_location("start_fixtures", ROOT / "tests/work_start_test.py")
fixtures = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixtures)


class RecoveryTest(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.WorkStartTest()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.primary = self.fixture.root
        self.git = self.fixture.git
        self.git(self.primary, "remote", "add", "origin", "https://github.com/example/project.git")
        self.root = self.primary / ".worktrees/ticket-001--fixture"
        self.git(self.primary, "worktree", "add", "--relative-paths", "-b", "ticket/001-fixture", str(self.root))
        (self.root / "api/a.txt").write_text("existing material work\n")
        self.git(self.root, "commit", "-am", "pre-adoption material")
        # Deliver the managed helper and dependencies before observing dirty CAS.
        for name in ("ticket_recovery.py", "ticket_allocation.py", "repository_policy.py"):
            shutil.copy2(ROOT / "scripts" / name, self.root / ".governance" / name)
        manifest_path = self.root / ".governance/manifest.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["coordination"]["workstreams"]["api"]["ownedPaths"].append(".governance/**")
        manifest_path.write_text(json.dumps(manifest))
        (self.root / ".governance/ticket-allocation.json").write_text(json.dumps({
            "$schema": "ticket-allocation.schema.json", "schema": "new-project.ticket-allocation/v1",
            "mode": "local-single-clone"}))
        self.head = self.git(self.root, "rev-parse", "HEAD")
        self.intent = {
            "schema": "new-project.intent/v3", "ticket": "ticket-001", "summary": "Recover fixture",
            "classification": {"kind": "BUG", "priority": "P1", "origin": "health"},
            "workstream": "api", "allowedPaths": ["api/**", ".governance/**", "project/ticket-001/**"],
            "forbiddenPaths": ["project/ticket-*/user-*.md"], "stacks": [],
            "dependsOn": [], "conflictsWith": [], "integrationTicket": None,
            "delivery": {
                "acceptedBaseSha": self.fixture.base, "targetBranch": "main", "outcome": "Recover bounded work",
                "nonGoals": ["Merge approval"], "complexity": "S", "estimatedMinutes": 15,
                "budgets": {"maxImplementationFiles": 5, "maxAffectedComponents": 1,
                            "maxPublicInterfaceChanges": 0, "maxRuntimeDependencies": 0},
                "architecture": {"status": "accepted", "decision": "Preserve existing implementation",
                    "components": [{"name": "api", "paths": ["api/**", ".governance/**"]}],
                    "responsibilityChanges": False, "interfaceChanges": [], "dataChanges": [],
                    "ui": {"impact": "none", "states": [], "evidence": []}, "rollback": "Preserve work"},
                "runtimeDependencies": [],
                "validation": [{"criterion": "AC-01", "commands": ["true"], "evidence": "Fixture only"}],
            },
        }
        self.store = Path(self.fixture.temp.name) / "controller"
        self.store.mkdir()
        (self.store / ".lock").touch()
        self.request_path = Path(self.fixture.temp.name) / "request.json"
        self.request = dict(schema="new-project.ticket-recovery-request/v1", intent=self.intent,
                            headSha=self.head, dirtyDigest=start.dirty_observation(self.root)[1],
                            leaseId="lease-fixture", leaseRevision=2, fencingToken=7,
                            ownerActor="fixture", ownerSession="fixture-session")
        self.lease = dict(schema="wellmanifest.change-lease/v1", leaseId="lease-fixture", leaseRevision=2,
                          fencingToken=7, ownerActor="fixture", ownerSession="fixture-session",
                          repositoryRef="example/project", ticketId="ticket-001", targetBranch="main",
                          branchRef="refs/heads/ticket/001-fixture", workstream="api",
                          worktreeId="ticket-001--fixture", scopeHash=start.digest(self.intent["allowedPaths"]),
                          phase="editing", publicationFrozen=False,
                          expiresAt=(datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat())
        self.resource = start.digest({"repositoryRef": "example/project", "targetBranch": "main"})
        self.state = dict(schema="subactor.repository-change-lease-store/v1",
                          leases={"lease-fixture": self.lease}, active={self.resource: "lease-fixture"})
        self.persist()

    def persist(self):
        self.request_path.write_text(json.dumps(self.request))
        (self.store / "state.json").write_text(json.dumps(self.state))

    def run_recovery(self):
        return subprocess.run(["bash", "project/new-ticket.sh", "--workstream", "api",
                               "--recover-request", str(self.request_path), "--recovery-lease-store", str(self.store)],
                              cwd=self.root, capture_output=True, text=True)

    def reject(self):
        self.persist()
        result = self.run_recovery()
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertFalse((self.root / "project/ticket-001").exists())
        self.assertEqual(self.git(self.root, "rev-parse", "HEAD"), self.head)

    def test_end_to_end_preserves_work_and_reserves_identity(self):
        before = (self.root / "api/a.txt").read_bytes()
        result = self.run_recovery()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(json.loads(result.stdout)["grantsMergeAuthority"])
        self.assertEqual(json.loads((self.root / "project/ticket-001/intent.json").read_text()), self.intent)
        self.assertEqual((self.primary / ".git/new-project-ticket-high-water").read_text().strip(), "1")
        self.assertEqual((self.root / "api/a.txt").read_bytes(), before)
        self.assertEqual(self.git(self.root, "rev-parse", "HEAD"), self.head)
        self.assertNotEqual(self.run_recovery().returncode, 0)

    def test_stale_head(self):
        self.request["headSha"] = self.fixture.base
        self.reject()

    def test_dirty_state_changed(self):
        (self.root / "api/a.txt").write_text("concurrent edit\n")
        self.reject()

    def test_change_between_observations_has_no_allocation_effect(self):
        original = recovery.inspect_recovery
        observations = []
        def inspect(*args):
            if observations:
                (self.root / "api/a.txt").write_text("racing edit\n")
            observations.append(True)
            return original(*args)
        with patch.object(recovery, "inspect_recovery", side_effect=inspect):
            with self.assertRaises(recovery.RecoveryError):
                recovery.recover(self.root, self.request_path, self.store, "api")
        self.assertFalse((self.primary / ".git/new-project-ticket-high-water").exists())
        self.assertFalse((self.root / "project/ticket-001").exists())

    def test_lease_bindings_fail_closed(self):
        for field, value in (("leaseRevision", 3), ("fencingToken", 8), ("ownerSession", "foreign"),
                             ("ownerActor", "foreign"), ("phase", "expired"), ("scopeHash", "0" * 64),
                             ("branchRef", "refs/heads/main"), ("repositoryRef", "other/project"),
                             ("ticketId", "ticket-002"), ("publicationFrozen", True)):
            with self.subTest(field=field):
                old = self.lease[field]
                self.lease[field] = value
                self.reject()
                self.lease[field] = old

    def test_expiry_is_not_takeover(self):
        self.lease["expiresAt"] = "2020-01-01T00:00:00Z"
        self.reject()

    def test_revoked_owner(self):
        self.state["active"].clear()
        self.reject()

    def test_scope_must_cover_preexisting_commit(self):
        self.intent["allowedPaths"].remove("api/**")
        self.lease["scopeHash"] = start.digest(self.intent["allowedPaths"])
        self.reject()

    def test_unowned_future_scope_rejected(self):
        self.intent["allowedPaths"].append("ui/**")
        self.lease["scopeHash"] = start.digest(self.intent["allowedPaths"])
        self.reject()

    def test_scope_must_cover_dirty_work(self):
        (self.root / "ui/a.txt").write_text("unowned\n")
        self.request["dirtyDigest"] = start.dirty_observation(self.root)[1]
        self.reject()

    def test_symlink_store_rejected(self):
        link = self.store.with_name("controller-link")
        link.symlink_to(self.store, target_is_directory=True)
        self.store = link
        self.reject()

    def test_reserved_identity_rejected(self):
        (self.primary / ".git/new-project-ticket-high-water").write_text("1\n")
        self.reject()

    def test_duplicate_branch_rejected(self):
        self.git(self.primary, "branch", "ticket/001-other", self.head)
        self.reject()

    def test_peer_writer_rejected(self):
        self.fixture.sibling(number=2)
        self.reject()

    def test_controller_lock_held(self):
        with recovery.controller_lock(self.store):
            self.reject()

    def test_clone_allocator_lock_held(self):
        (self.primary / ".git/new-project-ticket-allocation.lock").mkdir()
        self.reject()
        self.assertTrue((self.primary / ".git/new-project-ticket-allocation.lock").exists())

    def test_boolean_cas_rejected(self):
        self.request["leaseRevision"] = True
        self.reject()

    def test_noncanonical_layout_rejected(self):
        old = self.root
        self.git(self.primary, "worktree", "move", str(old), str(old.with_name("ticket-001--wrong")))
        self.root = old.with_name("ticket-001--wrong")
        self.reject()

    def test_outside_workstream_ownership_rejected(self):
        (self.root / "ui/a.txt").write_text("unowned\n")
        self.intent["allowedPaths"].append("ui/**")
        self.lease["scopeHash"] = start.digest(self.intent["allowedPaths"])
        self.request["dirtyDigest"] = start.dirty_observation(self.root)[1]
        self.reject()

    def test_registered_mode_cannot_use_local_recovery(self):
        (self.root / ".governance/ticket-allocation.json").write_text(json.dumps({
            "$schema": "ticket-allocation.schema.json", "schema": "new-project.ticket-allocation/v1",
            "mode": "registered", "allocator": {"processUri": "process://test/allocate",
                "issuer": "issuer://test", "maxReceiptAgeSeconds": 300}}))
        self.request["dirtyDigest"] = start.dirty_observation(self.root)[1]
        self.reject()

    def test_controller_under_candidate_checkout_rejected(self):
        inside = self.root / "controller"
        shutil.copytree(self.store, inside)
        self.store = inside
        self.reject()

    def test_ordinary_allocation_stays_closed_for_missing_intent(self):
        result = subprocess.run(["bash", "project/new-ticket.sh", "--workstream", "api"],
                                cwd=self.root, capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.root / "project/ticket-001").exists())


if __name__ == "__main__":
    unittest.main()
