#!/usr/bin/env python3
"""Real SQLite and complete governance checks without ticket files in Git."""
from contextlib import contextmanager
import base64
import hashlib
import json
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
SOURCE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SOURCE / "scripts"))
import ticket_input


class TicketInputTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.seed_temp = tempfile.TemporaryDirectory(prefix="ticket-input-seed-")
        cls.seed = Path(cls.seed_temp.name)
        paths = subprocess.check_output(["git", "-C", str(SOURCE), "ls-files", "-z"]).decode().split("\0")
        for name in {*paths, "scripts/ticket_input.py"} - {""}:
            if name.startswith("project/ticket-") or name.startswith(".subactor/sessions/"):
                continue
            source = SOURCE / name
            if not source.is_file():
                continue
            target = cls.seed / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)

    @classmethod
    def tearDownClass(cls):
        cls.seed_temp.cleanup()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ticket-input-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "repo"
        shutil.copytree(self.seed, self.root)
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.name", "Fixture")
        self.git("config", "user.email", "fixture@example.invalid")
        self.git("config", "commit.gpgsign", "false")
        self.git("config", "core.autocrlf", "false")
        self.git("add", ".")
        self.git("commit", "-qm", "seed")
        self.base = self.git("rev-parse", "HEAD").strip()
        self.git("update-ref", "refs/remotes/origin/main", self.base)
        self.git("checkout", "-qb", "ticket/001-database")
        (self.root / "src").mkdir(exist_ok=True)
        (self.root / "src/feature.txt").write_text("Material implementation\n")
        self.git("add", "src/feature.txt")
        self.git("commit", "-qm", "material change without Git ticket")
        self.head = self.git("rev-parse", "HEAD").strip()
        self.git("config", "core.hooksPath", ".githooks")
        exclude = self.root / ".git/info/exclude"
        with exclude.open("a") as stream:
            stream.write("\n" + "\n".join("/project.sqlite" + suffix for suffix in ("", "-wal", "-shm", "-journal")) + "\n")
        self.database = self.root / "project.sqlite"
        self.database.touch(mode=0o600)
        with self.connection() as connection:
            connection.executescript(f"PRAGMA application_id={ticket_input.APPLICATION_ID}; PRAGMA user_version=1; CREATE TABLE ticket_versions(ticket TEXT,revision INTEGER,document_sha256 TEXT,document_json TEXT);")
        self.intent = {
            "schema": "new-project.intent/v3", "ticket": "ticket-001", "summary": "Fixture implementation",
            "workstream": "governance", "classification": {"kind": "FEATURE", "priority": "P2", "origin": "requested"},
            "allowedPaths": ["src/**"], "forbiddenPaths": [], "stacks": [], "dependsOn": [], "conflictsWith": [], "integrationTicket": None,
            "delivery": {"acceptedBaseSha": self.base, "targetBranch": "main", "outcome": "Validate source changes",
                "nonGoals": ["No external effects"], "complexity": "S", "estimatedMinutes": 1,
                "budgets": {"maxImplementationFiles": 1, "maxAffectedComponents": 1, "maxPublicInterfaceChanges": 0, "maxRuntimeDependencies": 0},
                "architecture": {"status": "accepted", "decision": "One fixture component", "components": [{"name": "feature", "paths": ["src/**"]}],
                    "responsibilityChanges": False, "interfaceChanges": [], "dataChanges": [],
                    "ui": {"impact": "none", "states": [], "evidence": []}, "rollback": "Revert fixture"},
                "runtimeDependencies": [], "validation": [{"criterion": "AC-01", "commands": ["true"], "evidence": "Fixture"}]},
        }
        self.files = {"README.md": b"# Ticket\n\n- **Status**: IN_PROGRESS\n- **Workflow state**: EDIT\n",
                      "intent.json": json.dumps(self.intent).encode()}
        self.save()

    @contextmanager
    def connection(self):
        connection = sqlite3.connect(self.database)
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def git(self, *args):
        return ticket_input.git(self.root, *args).decode()

    def save(self):
        files = {name: {"encoding": "base64", "mode": "100644", "content": base64.b64encode(value).decode(),
                        "sha256": hashlib.sha256(value).hexdigest()} for name, value in self.files.items()}
        doc = json.dumps({"schema": "registry.ticket-content/v1", "ticket": "ticket-001", "files": files,
                          "execution_authorized": False, "merge_authorized": False}, separators=(",", ":"))
        with self.connection() as connection:
            connection.execute("DELETE FROM ticket_versions")
            connection.execute("INSERT INTO ticket_versions VALUES(?,?,?,?)", ("ticket-001", 1, hashlib.sha256(doc.encode()).hexdigest(), doc))

    def snapshot(self, **changes):
        doc = ticket_input.export_snapshot(self.root, self.database, "example/repo", self.base, self.head)
        doc.update(changes)
        path = Path(self.temp.name) / "snapshot.json"
        path.write_text(json.dumps(doc))
        return str(path), hashlib.sha256(path.read_bytes()).hexdigest()

    def run_gate(self, *args):
        result = subprocess.run([sys.executable, str(SOURCE / "scripts/governance_check.py"),
            "--root", str(self.root), "--manifest", "governance/manifest.hub.json", "--stack-profiles", "governance/stack-profiles.json",
            "--work-classification", "governance/work-classification.dsl.json", "--base", self.base, "--head", self.head,
            "--expected-repository", "example/repo", "--format", "json", *args], capture_output=True, text=True)
        self.assertIn(result.returncode, [0, 1], result.stderr)
        return result.returncode, json.loads(result.stdout)

    def test_full_local_gate_passes_without_materializing_ticket(self):
        index = (self.root / ".git/index").read_bytes()
        before = self.git("status", "--porcelain")
        code, report = self.run_gate("--ticket-database", str(self.database))
        self.assertEqual(code, 0, report)
        self.assertFalse((self.root / "project/ticket-001").exists())
        self.assertEqual(before, self.git("status", "--porcelain"))
        self.assertEqual(index, (self.root / ".git/index").read_bytes())
        code, report = self.run_gate()
        self.assertEqual(code, 1)
        self.assertIn("GOV-TICKET-001", str(report))

    def test_scope_escape_and_missing_content_are_still_rejected(self):
        self.intent["allowedPaths"] = ["other/**"]
        self.files["intent.json"] = json.dumps(self.intent).encode()
        self.save()
        code, report = self.run_gate("--ticket-database", str(self.database))
        self.assertEqual(code, 1)
        self.assertIn("GOV-SCOPE-001", str(report))
        del self.files["intent.json"]
        self.save()
        code, report = self.run_gate("--ticket-database", str(self.database))
        self.assertEqual(code, 1)
        self.assertIn("GOV-TICKET-003", str(report))

    def test_ci_and_approval_mode_reject_candidate_local_database(self):
        for mode in (["--actor", "ci"], ["--enforce-approval"]):
            code, report = self.run_gate("--ticket-database", str(self.database), *mode)
            self.assertEqual(code, 1)
            self.assertIn("untrusted", str(report))

    def test_pinned_ci_snapshot_passes_scope_checks_but_never_grants_approval(self):
        filename, pin = self.snapshot()
        args = ["--ticket-snapshot", filename, "--ticket-snapshot-sha256", pin, "--actor", "ci"]
        code, report = self.run_gate(*args)
        self.assertEqual(code, 0, report)
        code, report = self.run_gate(*args, "--enforce-approval")
        self.assertEqual(code, 1)
        self.assertIn("GOV-APPROVAL", str(report))

    def test_wrong_subject_and_digest_cannot_select_a_ticket(self):
        for changes in ({"repository": "wrong/repo"}, {"base_sha": self.head}, {"head_sha": self.base}, {"execution_authorized": True}):
            filename, pin = self.snapshot(**changes)
            code, report = self.run_gate("--ticket-snapshot", filename, "--ticket-snapshot-sha256", pin)
            self.assertEqual(code, 1, report)
        filename, pin = self.snapshot()
        for wrong in ("0" * 64, ""):
            self.assertEqual(self.run_gate("--ticket-snapshot", filename, "--ticket-snapshot-sha256", wrong)[0], 1)

    def test_snapshot_in_candidate_checkout_is_rejected_even_with_matching_pin(self):
        filename, pin = self.snapshot()
        target = self.root / "ignored-snapshot.json"
        shutil.copyfile(filename, target)
        self.assertEqual(self.run_gate("--ticket-snapshot", str(target), "--ticket-snapshot-sha256", pin)[0], 1)

    def test_duplicate_tickets_and_corrupted_documents_are_rejected(self):
        filename, _ = self.snapshot()
        doc = json.loads(Path(filename).read_text())
        doc["tickets"].append(doc["tickets"][0])
        Path(filename).write_text(json.dumps(doc))
        pin = hashlib.sha256(Path(filename).read_bytes()).hexdigest()
        self.assertEqual(self.run_gate("--ticket-snapshot", filename, "--ticket-snapshot-sha256", pin)[0], 1)
        with self.connection() as connection:
            connection.execute("UPDATE ticket_versions SET document_json='{}'")
        self.assertEqual(self.run_gate("--ticket-database", str(self.database))[0], 1)

    def test_worktree_reader_resolves_primary_database_and_rejects_links(self):
        linked = Path(self.temp.name) / "linked"
        self.git("worktree", "add", "--relative-paths", "-qb", "ticket/002-linked", str(linked))
        records = ticket_input.load_input(linked, database=self.database)
        self.assertEqual(records[0]["ticket"], "ticket-001")
        self.database.rename(self.root / "other.sqlite")
        self.database.symlink_to("other.sqlite")
        with self.assertRaises(ticket_input.TicketInputError):
            ticket_input.load_input(linked, database=self.database)


if __name__ == "__main__":
    unittest.main()
