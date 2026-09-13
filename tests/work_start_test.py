#!/usr/bin/env python3
"""Real Git regression fixtures; no network, effect authority or real worktrees."""
import json
import base64
import hashlib
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import work_start_check as start
import jsonschema


class WorkStartTest(unittest.TestCase):
    def git(self, root, *args):
        env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
        return subprocess.run(["git", "-C", str(root), *args], env=env, check=True,
                              capture_output=True, text=True).stdout.strip()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "repo"
        self.root.mkdir()
        self.git(self.root, "init", "-b", "main")
        self.git(self.root, "config", "user.name", "Fixture")
        self.git(self.root, "config", "user.email", "fixture@example.invalid")
        (self.root / ".gitignore").write_text("/.worktrees/\n")
        self.manifest = {
            "schema": "new-project.governance/v2",
            "ticket": {"activeStatuses": ["IN_PROGRESS"]},
            "coordination": {"maxActiveTicketsPerWorkstream": 1, "workstreams": {
                "api": {"ownedPaths": ["api/**"]}, "ui": {"ownedPaths": ["ui/**"]}}},
            "delivery": {"targetBranches": ["main"]},
        }
        for rel in ("api/a.txt", "ui/a.txt"):
            p = self.root / rel
            p.parent.mkdir(exist_ok=True)
            p.write_text("base\n")
        adopted = self.root / ".governance"
        adopted.mkdir()
        (adopted / "manifest.json").write_text(json.dumps(self.manifest))
        for filename in ("work_start_check.py", "ticket_activity.py", "worktree_overlap_check.py", "ticket_input.py"):
            shutil.copy2(ROOT / "scripts" / filename, adopted / filename)
        for filename in ("work-classification.dsl.json", "ticket-activity.json"):
            shutil.copy2(ROOT / "governance" / filename, adopted / filename)
        project = self.root / "project"
        project.mkdir()
        shutil.copy2(ROOT / "project/new-ticket.sh", project / "new-ticket.sh")
        self.git(self.root, "add", ".")
        self.git(self.root, "commit", "-m", "fixture")
        self.base = self.git(self.root, "rev-parse", "HEAD")

    def sibling(self, number=1, stream="api", paths=None, status="IN_PROGRESS"):
        ticket = f"ticket-{number:03d}"
        path = self.root / ".worktrees" / (ticket + "--fixture")
        self.git(self.root, "worktree", "add", "-b", f"ticket/{number:03d}-fixture", str(path))
        directory = path / "project" / ticket
        directory.mkdir()
        (directory / "README.md").write_text(f"- **Status**: {status}\n")
        intent = {"schema": "new-project.intent/v3", "ticket": ticket,
                  "workstream": stream, "allowedPaths": paths or [stream + "/**"]}
        (directory / "intent.json").write_text(json.dumps(intent))
        return path

    def report(self, root=None, stream="api", paths=(), ticket=None):
        result = start.inspect(root or self.root, stream, paths, ticket)
        jsonschema.validate(result, json.loads((ROOT / "governance/work-start-report.schema.json").read_text()))
        self.assertFalse(result["grantsAuthority"])
        self.assertFalse(result["createsWorktree"])
        return result

    def cli(self, *args):
        return subprocess.run([sys.executable, str(ROOT / "scripts/work_start_check.py"),
                               "--root", str(self.root), "--workstream", "api", *args],
                              capture_output=True, text=True)

    def test_clean_primary_is_candidate_not_authority(self):
        self.assertEqual(self.report()["route"], "NEW_TICKET_CANDIDATE")

    def test_sibling_active_scope_before_first_source_edit(self):
        peer = self.sibling()
        report = self.report()
        self.assertEqual(report["route"], "ASSIST_READ_ONLY")
        self.assertEqual(report["blockers"][0]["path"], str(peer))

    def test_resume_from_primary_resolves_existing_checkout(self):
        peer = self.sibling()
        report = self.report(ticket="ticket-001")
        self.assertEqual(report["route"], "REUSE_EXISTING")
        self.assertEqual(report, self.report(peer, ticket="ticket-001"))

    def test_resume_does_not_expand_existing_intent(self):
        self.sibling()
        with self.assertRaises(start.ObservationError):
            self.report(paths=["ui/**"], ticket="ticket-001")

    def test_blocked_dirty_peer_needs_handoff_not_second_writer(self):
        peer = self.sibling(status="BLOCKED")
        (peer / "api/a.txt").write_text("pending implementation\n")
        report = self.report()
        self.assertEqual(report["route"], "HANDOFF_REQUIRED")
        self.assertEqual(report["activeTicketCount"], 0)

    def test_blocked_peer_does_not_reserve_unrelated_work(self):
        peer = self.sibling(status="BLOCKED")
        (peer / "api/a.txt").write_text("pending\n")
        self.assertEqual(self.report(stream="ui")["route"], "NEW_TICKET_CANDIDATE")

    def test_same_workstream_disjoint_scope_respects_wip(self):
        self.sibling(paths=["api/old/**"])
        self.assertEqual(self.report(paths=["api/new/**"])["route"], "SERIALIZE")

    def test_disjoint_workstreams_can_progress(self):
        self.sibling()
        self.assertEqual(self.report(stream="ui")["route"], "NEW_TICKET_CANDIDATE")

    def test_two_pending_writers_cannot_claim_resume(self):
        self.sibling()
        self.sibling(number=2)
        self.assertEqual(self.report(ticket="ticket-001")["route"], "ASSIST_READ_ONLY")

    def test_phase_branch_with_dirty_primary_requires_reconciliation(self):
        self.git(self.root, "switch", "-c", "refactor/phase-a")
        peer = self.sibling()
        (self.root / "api/a.txt").write_text("primary staged content\n")
        self.git(self.root, "add", "api/a.txt")
        self.assertEqual(self.report(peer, ticket="ticket-001")["route"], "RECONCILE")

    def test_shared_committed_history_is_not_competing_delta(self):
        self.git(self.root, "switch", "-c", "refactor/phase-a")
        (self.root / "api/a.txt").write_text("shared history\n")
        self.git(self.root, "commit", "-am", "shared")
        peer = self.sibling()
        self.assertEqual(self.report(peer, ticket="ticket-001")["route"], "REUSE_EXISTING")

    def test_unchecked_branch_with_unique_delta_is_not_lost(self):
        self.git(self.root, "switch", "-c", "refactor/unassigned")
        (self.root / "api/a.txt").write_text("unique\n")
        self.git(self.root, "commit", "-am", "unique")
        self.git(self.root, "switch", "main")
        report = self.report()
        self.assertEqual(report["route"], "RECONCILE")
        self.assertEqual(report["blockers"][0]["reason"], "unassigned-branch-delta")

    def test_read_only_and_digest_invalidated_by_dirty_content(self):
        peer = self.sibling()
        before = (self.root / ".git/index").read_bytes()
        refs = self.git(self.root, "show-ref")
        one = self.report()
        two = self.report()
        self.assertEqual(one, two)
        self.assertEqual(before, (self.root / ".git/index").read_bytes())
        self.assertEqual(refs, self.git(self.root, "show-ref"))
        self.assertFalse(list(self.root.rglob("__pycache__")))
        (peer / "api/a.txt").write_text("one\n")
        first = self.report()["observationDigest"]
        (peer / "api/a.txt").write_text("two\n")
        self.assertNotEqual(first, self.report()["observationDigest"])

    def test_stale_hook_git_environment_does_not_hide_sibling(self):
        peer = self.sibling()
        with patch.dict(os.environ, {"GIT_DIR": str(self.root / ".git"),
                                     "GIT_WORK_TREE": str(self.root),
                                     "GIT_INDEX_FILE": str(self.root / ".git/index")}):
            self.assertEqual(self.report(peer)["route"], "ASSIST_READ_ONLY")

    def test_missing_target_fails_closed(self):
        self.git(self.root, "branch", "-m", "unrecognized")
        result = self.cli()
        self.assertEqual(result.returncode, 3)
        report = json.loads(result.stdout)
        jsonschema.validate(report, json.loads((ROOT / "governance/work-start-report.schema.json").read_text()))
        self.assertEqual(report["diagnostic"], start.CODE)

    def test_invalid_intent_fails_closed_without_content_disclosure(self):
        peer = self.sibling()
        (peer / "project/ticket-001/intent.json").write_text("PRIVATE-FIXTURE-MARKER")
        result = self.cli()
        self.assertEqual(result.returncode, 3)
        self.assertNotIn("PRIVATE-FIXTURE-MARKER", result.stdout + result.stderr)

    def test_unknown_worktree_cannot_disappear_from_inventory(self):
        peer = self.sibling()
        peer.rename(peer.with_name("preserved-unregistered"))
        self.assertEqual(self.cli().returncode, 3)

    def test_allocator_force_new_cannot_bypass_or_reserve_number(self):
        self.sibling()
        before = self.git(self.root, "worktree", "list", "--porcelain")
        result = subprocess.run(["bash", "project/new-ticket.sh", "--workstream", "api", "--force-new"],
                                cwd=self.root, capture_output=True, text=True)
        self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
        self.assertIn(start.CODE, result.stderr)
        self.assertFalse((self.root / ".git/new-project-ticket-high-water").exists())
        self.assertFalse((self.root / ".git/new-project-ticket-allocation.lock").exists())
        self.assertFalse((self.root / "project/ticket-001").exists())
        self.assertEqual(before, self.git(self.root, "worktree", "list", "--porcelain"))

    def test_allocator_clean_clone_allocates_once(self):
        result = subprocess.run(["bash", "project/new-ticket.sh", "--workstream", "api"],
                                cwd=self.root, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue((self.root / "project/ticket-001/intent.json").exists())
        repeat = subprocess.run(["bash", "project/new-ticket.sh", "--workstream", "api"],
                                cwd=self.root, capture_output=True, text=True)
        self.assertEqual(repeat.returncode, 3)
        self.assertFalse((self.root / "project/ticket-002").exists())

    def test_closed_report_schema_and_package_binding(self):
        report = self.report()
        report["allowWrite"] = True
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(report, json.loads((ROOT / "governance/work-start-report.schema.json").read_text()))
        package = json.loads((ROOT / "governance/package-manifest.json").read_text())
        mapping = {entry["source"]: entry for entry in package["files"]}
        self.assertEqual(mapping["scripts/work_start_check.py"]["target"], ".governance/work_start_check.py")
        self.assertIn("governance/work-start-report.schema.json", mapping)
        self.assertIn("error/GOV-WORK-START.md", mapping)

    def test_sqlite_pending_ticket_without_files_is_not_ignored(self):
        import ticket_input
        self.git(self.root, "config", "new-project.ticketStorage", "sqlite")
        exclude = self.root / ".git/info/exclude"
        exclude.write_text(exclude.read_text() + "\n/project.sqlite*\n")
        database = self.root / "project.sqlite"
        database.touch(mode=0o600)
        intent = {"schema": "new-project.intent/v3", "ticket": "ticket-001",
                  "workstream": "api", "allowedPaths": ["api/**"]}
        files = {"README.md": b"- **Status**: IN_PROGRESS\n", "intent.json": json.dumps(intent).encode()}
        document = json.dumps({"schema": "registry.ticket-content/v1", "ticket": "ticket-001",
                               "execution_authorized": False, "merge_authorized": False,
                               "files": {name: {"encoding": "base64", "mode": "100644",
                                                "sha256": hashlib.sha256(raw).hexdigest(),
                                                "content": base64.b64encode(raw).decode()}
                                         for name, raw in files.items()}})
        with sqlite3.connect(database) as connection:
            connection.executescript(f"PRAGMA application_id={ticket_input.APPLICATION_ID}; PRAGMA user_version=1; CREATE TABLE ticket_versions(ticket TEXT,revision INTEGER,document_sha256 TEXT,document_json TEXT);")
            connection.execute("INSERT INTO ticket_versions VALUES(?,?,?,?)",
                               ("ticket-001", 1, hashlib.sha256(document.encode()).hexdigest(), document))
        before = database.read_bytes()
        report = self.report()
        self.assertEqual(report["route"], "RECONCILE")
        self.assertEqual(report["blockers"][0]["ticket"], "ticket-001")
        self.assertEqual(before, database.read_bytes())
        self.assertFalse((self.root / "project/ticket-001").exists())

    def test_state_change_during_observation_requires_retry(self):
        original = start.dirty_observation
        counter = 0
        def observe(path):
            nonlocal counter
            counter += 1
            if counter == 2:
                (self.root / "api/a.txt").write_text("concurrent change\n")
            return original(path)
        with patch.object(start, "dirty_observation", side_effect=observe):
            with self.assertRaises(start.ObservationError):
                self.report()


if __name__ == "__main__":
    unittest.main()
