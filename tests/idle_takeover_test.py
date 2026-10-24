#!/usr/bin/env python3
"""Idle takeover: manifest policy, lease layout roots, activity, refusal states, CAS, snapshot and board."""
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


runtime = load("idle_takeover_runtime", ROOT / "scripts/idle_takeover.py")
BRANCH = "ticket/001-fixture"
WORKTREE_ID = "ticket-001--fixture"


def git(cwd, *args):
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    env.update(GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@example.invalid",
               GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@example.invalid")
    return subprocess.run(["git", "-C", str(cwd), *args], env=env, check=True,
                          capture_output=True, text=True).stdout.strip()


def stamp(moment):
    return moment.strftime("%Y-%m-%dT%H:%M:%SZ")


class IdleTakeoverTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.primary = Path(self.temporary.name).resolve() / "repo"
        self.primary.mkdir()
        git(self.primary, "init", "-q", "-b", "main")
        git(self.primary, "remote", "add", "origin", "git@github.com:example/fixture.git")
        (self.primary / "README.md").write_text("fixture\n")
        git(self.primary, "add", "README.md")
        git(self.primary, "commit", "-q", "-m", "base")
        self.worktree = self.primary / ".worktrees" / WORKTREE_ID
        git(self.primary, "worktree", "add", "-q", "-b", BRANCH, str(self.worktree))
        (self.worktree / "work.txt").write_text("work\n")
        git(self.worktree, "add", "work.txt")
        git(self.worktree, "commit", "-q", "-m", "ticket work")
        self.now = datetime.now(timezone.utc) + timedelta(minutes=20)
        self.lease_path = self.primary / ".subactor/leases" / f"{WORKTREE_ID}.json"
        self.write_lease()
        self.write_policy(enabled=True, idleMinutes=15, leaseMinutes=120)

    def tearDown(self):
        self.temporary.cleanup()

    def write_lease(self, **changes):
        issued = datetime.now(timezone.utc) - timedelta(hours=1)
        lease = {"schema": "wellmanifest.change-lease/v1", "leaseId": "allocation-ticket-001-fixture",
                 "repositoryRef": "example/fixture", "targetBranch": "main", "ticketId": "ticket-001",
                 "workstream": "governance", "scopeHash": "1" * 64, "branchRef": f"refs/heads/{BRANCH}",
                 "worktreeId": WORKTREE_ID, "ownerActor": "agent:previous", "ownerSession": "session-previous",
                 "phase": "claimed", "leaseRevision": 1, "fencingToken": 1, "issuedAt": stamp(issued),
                 "expiresAt": stamp(issued + timedelta(hours=2)), "heartbeatAt": stamp(issued),
                 "headSha": None, "pullRequest": None, "validatorRunId": None, "publicationFrozen": False,
                 "planHash": "2" * 64, "previousReceiptRef": None, "eventSequence": 1}
        lease.update(changes)
        self.lease_path.parent.mkdir(parents=True, exist_ok=True)
        self.lease_path.write_text(json.dumps(lease))

    def write_policy(self, **policy):
        manifest = self.primary / ".governance/manifest.json"
        manifest.parent.mkdir(exist_ok=True)
        manifest.write_text(json.dumps({"coordination": {"idleTakeover": policy}}))

    def entry(self, now=None):
        board = runtime.observe(self.primary, now or self.now)
        return next(item for item in board["tickets"] if item["ticket"] == "ticket-001")

    def test_recent_activity_is_active_and_refused(self):
        self.assertEqual(self.entry(datetime.now(timezone.utc))["state"], "ACTIVE")
        with self.assertRaises(PermissionError):
            runtime.takeover(self.primary, "ticket-001", "agent:next", "session-next", datetime.now(timezone.utc))

    def test_recent_dirty_edit_counts_as_activity(self):
        (self.worktree / "work.txt").write_text("edited\n")
        future = datetime.fromtimestamp((self.worktree / "work.txt").stat().st_mtime, timezone.utc) + timedelta(minutes=5)
        entry = self.entry(future)
        self.assertEqual((entry["state"], entry["lastActivitySource"]), ("ACTIVE", "dirtyFile"))

    def test_live_process_in_worktree_is_active(self):
        process = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"], cwd=self.worktree)
        try:
            entry = self.entry()
            self.assertEqual(entry["state"], "ACTIVE")
            self.assertIn(process.pid, entry["livePids"])
        finally:
            process.kill()
            process.wait()

    def test_idle_takeover_moves_lease_through_cas_and_writes_board(self):
        self.assertEqual(self.entry()["state"], "IDLE_TAKEOVER_ELIGIBLE")
        record = runtime.takeover(self.primary, "ticket-001", "agent:next", "session-next", self.now)
        lease = json.loads(self.lease_path.read_text())
        self.assertEqual((lease["ownerActor"], lease["ownerSession"], lease["phase"]), ("agent:next", "session-next", "claimed"))
        self.assertEqual((lease["leaseRevision"], lease["fencingToken"]), (4, 4))
        self.assertEqual([receipt["action"] for receipt in record["receipts"]], ["expire", "release"])
        self.assertEqual(lease["previousReceiptRef"], record["receipts"][-1]["receiptRef"])
        self.assertEqual(lease["headSha"], git(self.worktree, "rev-parse", "HEAD"))
        self.assertIn("policy:new-project.idle-takeover/v1", record["authorityRef"])
        self.assertEqual((record["branch"], record["worktreePath"], record["leasePath"]),
                         (BRANCH, str(self.worktree), str(self.lease_path)))
        self.assertEqual(record["writerEnvironment"]["NEW_PROJECT_FENCING_TOKEN"], "4")
        trace = self.primary / ".subactor/receipts/idle-takeover/ticket-001.jsonl"
        self.assertEqual(json.loads(trace.read_text())["previousOwner"]["actor"], "agent:previous")
        board = (self.primary / ".subactor/cache/autonomy-board.md").read_text()
        self.assertIn(f"`.worktrees/{WORKTREE_ID}`", board)
        self.assertIn("https://github.com/example/fixture/issues", board)
        self.assertIn("https://github.com/example/fixture/tree/ticket/001-fixture", board)
        self.assertIn("agent:next", board)
        self.assertEqual(self.entry(self.now)["state"], "ACTIVE")

    def test_dirty_work_is_snapshotted_and_left_in_place(self):
        (self.worktree / "work.txt").write_text("unsaved\n")
        (self.worktree / "new.txt").write_text("untracked\n")
        later = self.now + timedelta(minutes=30)
        record = runtime.takeover(self.primary, "ticket-001", "agent:next", "session-next", later)
        snapshot = Path(record["snapshot"]["path"])
        self.assertTrue(snapshot.is_file())
        self.assertEqual(snapshot.stem, record["snapshot"]["sha256"])
        self.assertEqual(sorted(record["snapshot"]["paths"]), ["new.txt", "work.txt"])
        self.assertEqual((self.worktree / "work.txt").read_text(), "unsaved\n")

    def test_frozen_publication_is_reported_not_taken_over(self):
        self.write_lease(phase="publication_frozen", publicationFrozen=True, headSha=git(self.worktree, "rev-parse", "HEAD"))
        self.assertEqual(self.entry()["state"], "IDLE_FROZEN")
        with self.assertRaises(PermissionError):
            runtime.takeover(self.primary, "ticket-001", "agent:next", "session-next", self.now)

    def test_integrated_clean_ticket_needs_release_not_takeover(self):
        git(self.primary, "merge", "-q", "--ff-only", BRANCH)
        self.assertEqual(self.entry()["state"], "IDLE_INTEGRATED")

    def test_disabled_policy_blocks_takeover(self):
        self.write_policy(enabled=False, idleMinutes=15, leaseMinutes=120)
        self.assertEqual(self.entry()["state"], "POLICY_DISABLED")

    def test_missing_policy_disables_takeover(self):
        (self.primary / ".governance/manifest.json").write_text(json.dumps({"coordination": {}}))
        self.assertEqual(self.entry()["state"], "POLICY_DISABLED")

    def test_configured_idle_minutes_are_respected(self):
        self.write_policy(enabled=True, idleMinutes=60, leaseMinutes=120)
        self.assertEqual(self.entry()["state"], "ACTIVE")

    def test_noncanonical_worktree_is_never_taken_over(self):
        outside = Path(self.temporary.name) / "elsewhere"
        git(self.primary, "worktree", "move", str(self.worktree), str(outside))
        entry = self.entry()
        self.assertEqual((entry["state"], entry["layoutProblems"]), ("NONCANONICAL_LAYOUT", ["worktreePath"]))
        with self.assertRaises(PermissionError):
            runtime.takeover(self.primary, "ticket-001", "agent:next", "session-next", self.now)

    def test_lease_binding_must_match_its_worktree(self):
        self.write_lease(branchRef="refs/heads/ticket/001-other")
        self.assertIn("branch", self.entry()["layoutProblems"])

    def test_observe_from_linked_worktree_uses_primary(self):
        board = runtime.observe(self.worktree, self.now)
        self.assertEqual(board["primaryCheckout"], str(self.primary))
        self.assertEqual(board["worktreesRoot"], str(self.primary / ".worktrees"))

    def test_concurrent_lease_change_loses_cas(self):
        original = runtime.snapshot

        def racing_snapshot(primary, entry):
            self.write_lease(heartbeatAt=stamp(datetime.now(timezone.utc)), leaseRevision=2, fencingToken=2)
            return original(primary, entry)

        runtime.snapshot = racing_snapshot
        try:
            with self.assertRaises(PermissionError):
                runtime.takeover(self.primary, "ticket-001", "agent:next", "session-next", self.now)
        finally:
            runtime.snapshot = original
        self.assertEqual(json.loads(self.lease_path.read_text())["ownerActor"], "agent:previous")

    def test_cli_observe_writes_board(self):
        result = subprocess.run([sys.executable, "-I", str(ROOT / "scripts/idle_takeover.py"), "--root", str(self.primary),
                                 "observe", "--format", "json"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["schema"], "new-project.autonomy-board/v1")
        self.assertTrue((self.primary / ".subactor/cache/autonomy-board.json").is_file())

    def test_work_start_refreshes_board(self):
        spec = importlib.util.spec_from_file_location("idle_work_start", ROOT / "scripts/work_start_check.py")
        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            module.refresh_autonomy_board(self.primary)
        finally:
            sys.path.remove(str(ROOT / "scripts"))
        board = json.loads((self.primary / ".subactor/cache/autonomy-board.json").read_text())
        self.assertEqual([(item["ticket"], item["state"]) for item in board["tickets"]], [("ticket-001", "ACTIVE")])

    def test_malformed_policy_values_disable_takeover(self):
        for policy in ({"enabled": "false", "idleMinutes": 15, "leaseMinutes": 120},
                       {"enabled": True, "idleMinutes": -1, "leaseMinutes": 120},
                       {"enabled": True, "idleMinutes": 0, "leaseMinutes": 120},
                       {"enabled": True, "idleMinutes": True, "leaseMinutes": 120},
                       {"enabled": True, "idleMinutes": 15, "leaseMinutes": False},
                       {"enabled": True, "idleMinutes": 60, "leaseMinutes": 30}):
            with self.subTest(policy=policy):
                self.write_policy(**policy)
                self.assertEqual(self.entry()["state"], "POLICY_DISABLED")

    def test_local_target_merge_counts_despite_stale_remote_ref(self):
        git(self.primary, "update-ref", "refs/remotes/origin/main", git(self.primary, "rev-parse", "main"))
        git(self.primary, "merge", "-q", "--ff-only", BRANCH)
        self.assertEqual(self.entry()["state"], "IDLE_INTEGRATED")

    def test_staged_rename_reports_both_paths(self):
        git(self.worktree, "mv", "work.txt", "moved.txt")
        self.assertEqual(runtime.dirty_paths(self.worktree), ["moved.txt", "work.txt"])

    def test_held_lease_lock_refuses_takeover(self):
        with runtime.lease_lock(self.lease_path):
            with self.assertRaises(PermissionError):
                runtime.takeover(self.primary, "ticket-001", "agent:next", "session-next", self.now)
        self.assertEqual(json.loads(self.lease_path.read_text())["ownerActor"], "agent:previous")
        runtime.takeover(self.primary, "ticket-001", "agent:next", "session-next", self.now)
        self.assertEqual(json.loads(self.lease_path.read_text())["ownerActor"], "agent:next")



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
