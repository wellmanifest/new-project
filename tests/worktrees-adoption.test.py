#!/usr/bin/env python3

from __future__ import annotations

import hashlib
import importlib.util
import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
LOCK_PATH = ROOT / "governance" / "worktrees.lock.json"


def sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_checker():
    path = ROOT / "subprojects" / "worktrees" / "conformance.py"
    spec = importlib.util.spec_from_file_location("worktrees_conformance", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class WorktreesAdoptionTest(unittest.TestCase):
    def test_lock_binds_published_artifacts(self):
        lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
        self.assertEqual(lock["schema"], "new-project.worktrees-lock/v1")
        self.assertEqual(lock["dependency"]["id"], "wellmanifest/worktrees")
        self.assertEqual(lock["dependency"]["version"], "0.3.0")
        self.assertEqual(
            lock["dependency"]["sourceRevision"],
            "49ab80b6a4a165add0b5e087f10b0ecb754f1514",
        )
        for artifact in lock["artifacts"]:
            self.assertEqual(
                sha256(ROOT / artifact["packageSourcePath"]),
                artifact["sourceSha256"],
            )

    def test_package_distributes_managed_contract(self):
        package = json.loads(
            (ROOT / "governance" / "package-manifest.json").read_text(encoding="utf-8")
        )
        entries = {item["target"]: item for item in package["files"]}
        expected = {
            ".governance/worktrees.schema.json": False,
            ".governance/worktree_path_check.py": True,
            ".governance/worktrees.lock.json": False,
        }
        for target, executable in expected.items():
            self.assertEqual(entries[target]["strategy"], "managed")
            self.assertEqual(entries[target]["executable"], executable)

    def test_planner_and_validator_enforce_workspace_root(self):
        checker = load_checker()
        record = checker.plan(
            repository="wellmanifest/new-project",
            repository_name="new-project",
            ticket="ticket-127",
            slug="worktrees-standard",
            workspace_root="/workspace/wellmanifest",
        )
        self.assertEqual(
            record["worktreePath"],
            "/workspace/wellmanifest/.worktrees/.branches/new-project/ticket-127--worktrees-standard",
        )
        self.assertEqual(
            record["branchWorktreesRoot"],
            "/workspace/wellmanifest/.worktrees/.branches",
        )
        self.assertEqual(
            record["repositoryWorktreesRoot"],
            "/workspace/wellmanifest/.worktrees/.branches/new-project",
        )
        self.assertEqual(
            record["leasePath"],
            "/workspace/wellmanifest/.worktrees/.leases/new-project/ticket-127--worktrees-standard.json",
        )
        self.assertEqual(checker.validate(record), [])
        record["worktreePath"] = "/workspace/wellmanifest/.worktrees/new-project--ticket-127--worktrees-standard"
        self.assertIn("noncanonical:worktreePath", checker.validate(record))

    def test_agent_template_declares_canonical_layout(self):
        template = (ROOT / "template" / "files" / "AGENTS.template.md").read_text(
            encoding="utf-8"
        )
        self.assertIn(
            "<workspace>/.worktrees/.branches/<repo>/<ticket-NNN>--<slug>",
            template,
        )
        self.assertIn("Reject a symlink", template)
        self.assertIn("parallel `<organization>-worktrees`", template)
        self.assertIn("never move an existing worktree automatically", template)


if __name__ == "__main__":
    unittest.main()
