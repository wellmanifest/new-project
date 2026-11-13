#!/usr/bin/env python3
"""Explicit repository namespaces preserve real legacy continuity journals."""
import argparse
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import work_continuity as co
from continuity_storage_test import fixture_event, REPOSITORY

CURRENT = "repository:github.com/example/renamed-continuity"


class NamespaceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve() / "repo"
        self.git("init", "--quiet", "--initial-branch=main", str(self.root), root=self.root.parent)
        self.git("config", "user.email", "namespace@example.invalid")
        self.git("config", "user.name", "namespace fixture")
        self.git("remote", "add", "origin", "https://github.com/example/continuity.git")
        (self.root / ".subactor").mkdir()
        for name in ("manifest.json", ".gitignore"):
            shutil.copyfile(ROOT / ".subactor" / name, self.root / ".subactor" / name)
        ticket = self.root / "project/ticket-002"
        ticket.mkdir(parents=True)
        (ticket / "README.md").write_text("- **Status**: IN_PROGRESS\n")
        (ticket / "intent.json").write_text(json.dumps({
            "schema": "new-project.intent/v3", "ticket": "ticket-002",
            "summary": "namespace fixture", "workstream": "governance",
            "classification": {"kind": "BUG", "priority": "P1", "origin": "requested"},
            "allowedPaths": ["project/ticket-002/**"], "forbiddenPaths": [],
            "stacks": [], "dependsOn": [], "conflictsWith": [], "integrationTicket": None,
            "delivery": {"acceptedBaseSha": "0" * 40, "targetBranch": "main",
                         "outcome": "namespace fixture", "nonGoals": ["no authority"]},
        }))
        self.git("add", ".")
        self.git("commit", "--quiet", "-m", "fixture")
        self.legacy, self.index, _, _ = co.storage_paths(self.root)
        co.commit_event(self.root, fixture_event())
        self.before = self.legacy.read_bytes(), self.index.read_bytes()
        self.digest = hashlib.sha256(self.before[0]).hexdigest()
        self.git("remote", "set-url", "origin", "https://github.com/example/renamed-continuity.git")

    def git(self, *args, root=None):
        return subprocess.check_output(["git", "-C", str(root or self.root), *args], stderr=subprocess.PIPE)

    def cli(self, *args):
        return subprocess.run([sys.executable, str(ROOT / "scripts/work_continuity.py"),
            *args, "--root", str(self.root)], text=True, capture_output=True)

    def init_args(self, apply=True, **updates):
        data = dict(root=self.root, apply=apply, expected_legacy_repository=REPOSITORY,
                    expected_legacy_sha256=self.digest)
        data.update(updates)
        return argparse.Namespace(**data)

    def initialize(self, **updates):
        return co.namespace_module().initialize(self.init_args(**updates), co)

    def unchanged(self):
        self.assertEqual((self.legacy.read_bytes(), self.index.read_bytes()), self.before)

    def test_cli_separates_changed_origin_without_rebinding(self):
        rejected = self.cli("resolve", "--ticket", "ticket-001")
        self.assertNotEqual(rejected.returncode, 0)
        result = self.cli("init-namespace", "--expected-legacy-repository", REPOSITORY,
                          "--expected-legacy-sha256", self.digest, "--apply")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(json.loads(result.stdout)["grantsAuthority"])
        digest = "0" * 64
        result = self.cli("capture", "--ticket", "ticket-002", "--session-id", "new-origin",
            "--phase", "validation", "--worktree-id", "fixture", "--authorization-ref",
            "authorization:fixture/no-authority", "--plan-ref", "artifact:fixture/plan",
            "--plan-sha256", digest, "--slice-ref", "artifact:fixture/slice", "--slice-sha256",
            digest, "--slice-ordinal", "1", "--slice-total", "1", "--remote-account-ref",
            "account:github/example", "--remote-observation-receipt", "receipt:fixture/current",
            "--completed", "AC-01", "--next-action", "observe")
        self.assertEqual(result.returncode, 0, result.stderr)
        event = json.loads(result.stdout)
        self.assertEqual(event["checkpoint"]["repositoryRef"], CURRENT)
        self.assertEqual(event["checkpoint"]["sequence"], 1)
        result = self.cli("resolve", "--ticket", "ticket-002")
        self.assertEqual(result.returncode, 0, result.stderr)
        checkpoint = self.root.parent / "checkpoint.json"
        checkpoint.write_text(result.stdout)
        for command in (("verify", "--checkpoint", str(checkpoint)), ("rebuild-index",)):
            result = self.cli(*command)
            self.assertEqual(result.returncode, 0, result.stderr)
        self.unchanged()

    def test_cli_plan_is_read_only(self):
        files = set(self.root.rglob("*"))
        result = self.cli("init-namespace", "--expected-legacy-repository", REPOSITORY,
                          "--expected-legacy-sha256", self.digest)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "planned")
        self.assertEqual(set(self.root.rglob("*")), files)
        self.assertEqual(co.storage_paths(self.root)[0], self.legacy)
        self.unchanged()

    def test_wrong_digest_or_repository_refuses_activation(self):
        for update in ({"expected_legacy_sha256": "f" * 64},
                       {"expected_legacy_repository": CURRENT},
                       {"expected_legacy_repository": "repository:github.com/unrelated/repo"}):
            with self.subTest(update=update), self.assertRaises(co.ContinuityError):
                self.initialize(**update)
            self.assertEqual(co.storage_paths(self.root)[0], self.legacy)
            self.unchanged()

    def test_incomplete_chain_is_not_a_new_namespace(self):
        self.legacy.write_bytes(self.before[0][:-1])
        with self.assertRaises(co.ContinuityError):
            self.initialize(expected_legacy_sha256=hashlib.sha256(self.legacy.read_bytes()).hexdigest())
        self.assertEqual(co.storage_paths(self.root)[0], self.legacy)
        self.assertEqual(self.index.read_bytes(), self.before[1])

    def test_exact_initialization_replay_is_idempotent_after_use(self):
        self.initialize()
        paths = co.storage_paths(self.root)
        event = fixture_event("ticket-003", "current-writer")
        cp = event["checkpoint"]
        cp["repositoryRef"] = cp["remoteObservation"]["repositoryRef"] = CURRENT
        cp["checkpointRef"] = "receipt:continuity.ticket-003.1." + co.canonical_digest(
            {k: v for k, v in cp.items() if k != "checkpointRef"})
        event["eventRef"] = "receipt:continuity-event.current-writer.1." + co.canonical_digest(
            {k: v for k, v in event.items() if k != "eventRef"})
        self.assertEqual(co.commit_event(self.root, event)["status"], "recorded")
        self.assertEqual(co.commit_event(self.root, event)["status"], "already-recorded")
        self.assertEqual(self.initialize()["status"], "already-enabled")
        self.assertEqual(len(list(co.iter_events(paths[0]))), 1)
        with self.assertRaises(co.ContinuityError):
            co.commit_event(self.root, fixture_event())
        self.unchanged()

    def test_existing_namespace_data_is_preserved_and_refused(self):
        plan = self.initialize(apply=False)
        occupied = self.root / plan["eventStreamPath"]
        occupied.parent.mkdir(parents=True)
        occupied.write_text("unique unrelated data\n")
        with self.assertRaises(co.ContinuityError):
            self.initialize()
        self.assertEqual(occupied.read_text(), "unique unrelated data\n")
        self.assertEqual(co.storage_paths(self.root)[0], self.legacy)
        self.unchanged()

    def test_publication_failure_leaves_legacy_selected(self):
        with patch("os.link", side_effect=OSError("fixture failure")):
            with self.assertRaises(OSError):
                self.initialize()
        self.assertEqual(co.storage_paths(self.root)[0], self.legacy)
        self.unchanged()
        self.assertEqual(self.initialize()["status"], "enabled")

    @unittest.skipUnless(hasattr(os, "symlink"), "symlink support")
    def test_symlinked_selector_parent_is_refused(self):
        outside = self.root.parent / "outside"
        outside.mkdir()
        parent = self.root / ".subactor/recovery/continuity-namespaces"
        parent.symlink_to(outside, target_is_directory=True)
        with self.assertRaises(co.ContinuityError):
            self.initialize()
        self.assertEqual(list(outside.iterdir()), [])
        self.unchanged()

    def test_malformed_selector_is_not_ignored(self):
        plan = self.initialize(apply=False)
        marker = self.root / plan["selectorPath"]
        marker.parent.mkdir(parents=True)
        marker.write_text('{"schema":"unrelated"}')
        with self.assertRaises(co.ContinuityError):
            co.storage_paths(self.root)
        self.unchanged()

    def test_selector_cannot_rebind_repository_or_redirect_paths(self):
        result = self.initialize()
        marker = self.root / result["selectorPath"]
        original = json.loads(marker.read_text())
        for update in ({"repositoryRef": REPOSITORY}, {"legacyRepositoryRef": CURRENT},
                       {"legacyEventCount": True}, {"eventStreamPath": "../outside"}):
            with self.subTest(update=update):
                marker.write_text(json.dumps({**original, **update}))
                with self.assertRaises(co.ContinuityError):
                    co.storage_paths(self.root)
        self.unchanged()

    def test_concurrent_selector_file_is_never_replaced(self):
        plan = self.initialize(apply=False)
        marker = self.root / plan["selectorPath"]
        original_link = os.link
        def raced_link(*args, **kwargs):
            marker.write_bytes(b"unique concurrent file\n")
            return original_link(*args, **kwargs)
        with patch("os.link", side_effect=raced_link):
            with self.assertRaises(FileExistsError):
                self.initialize()
        self.assertEqual(marker.read_bytes(), b"unique concurrent file\n")
        self.unchanged()

    def test_contending_processes_initialize_once(self):
        def run():
            return self.cli("init-namespace", "--expected-legacy-repository", REPOSITORY,
                            "--expected-legacy-sha256", self.digest, "--apply")
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda _: run(), range(2)))
        self.assertEqual([x.returncode for x in results], [0, 0], [x.stderr for x in results])
        self.assertCountEqual([json.loads(x.stdout)["status"] for x in results],
                              ["enabled", "already-enabled"])
        self.unchanged()


if __name__ == "__main__":
    unittest.main()
