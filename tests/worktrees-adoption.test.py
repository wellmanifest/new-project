#!/usr/bin/env python3

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
LOCK_PATH = ROOT / "governance" / "worktrees.lock.json"
SOURCE_REVISION = "73f9b99227bfbad6ce02834324d053279fb48611"


def sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_checker():
    path = ROOT / "subprojects" / "worktrees" / "conformance.py"
    spec = importlib.util.spec_from_file_location("worktrees_conformance", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
    finally:
        sys.modules.pop(spec.name, None)
    return module


def run(*args: str, cwd: pathlib.Path | None = None) -> str:
    result = subprocess.run(
        args,
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


class WorktreesAdoptionTest(unittest.TestCase):
    def test_lock_binds_published_artifacts(self):
        lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
        self.assertEqual(lock["schema"], "new-project.worktrees-lock/v1")
        self.assertEqual(lock["dependency"]["id"], "wellmanifest/worktrees")
        self.assertEqual(lock["dependency"]["version"], "0.4.0")
        self.assertEqual(lock["dependency"]["sourceRevision"], SOURCE_REVISION)
        expected = {
            "subprojects/worktrees/worktrees.schema.json":
                "da485b122b749374146d86a74cfa2dc678c091556883cdca48e3caf0d06d8199",
            "subprojects/worktrees/conformance.py":
                "dd1ac79d9265c6f00cab2b62c2348c1a45b63c0aba6a3c180dab9672a7984c02",
        }
        self.assertEqual(
            {artifact["packageSourcePath"] for artifact in lock["artifacts"]},
            set(expected),
        )
        for artifact in lock["artifacts"]:
            path = artifact["packageSourcePath"]
            self.assertEqual(artifact["sourceSha256"], expected[path])
            self.assertEqual(sha256(ROOT / path), expected[path])

    def test_package_distributes_managed_contract(self):
        package = json.loads(
            (ROOT / "governance" / "package-manifest.json").read_text(encoding="utf-8")
        )
        entries = {item["target"]: item for item in package["files"]}
        expected = {
            ".governance/worktrees.schema.json": False,
            ".governance/worktree_path_check.py": True,
            ".governance/worktrees.lock.json": False,
            ".governance/workspace_lifecycle_check.py": True,
            ".governance/worktree_overlap_check.py": True,
            "worktree-guard.yaml": False,
        }
        for target, executable in expected.items():
            self.assertEqual(entries[target]["strategy"], "managed")
            self.assertEqual(entries[target]["executable"], executable)

    def test_planner_enforces_repository_local_relative_layout_on_both_platforms(self):
        checker = load_checker()
        record = checker.plan(
            repository="wellmanifest/new-project",
            repository_name="new-project",
            ticket="ticket-178",
            slug="adopt-worktrees-v4",
            primary_checkout="/workspace/new-project",
        )
        self.assertEqual(record["schema"], "wellmanifest.worktrees/v4")
        self.assertEqual(record["kind"], "layout-record")
        self.assertEqual(
            record["worktreePath"],
            "/workspace/new-project/worktrees/ticket-178--adopt-worktrees-v4",
        )
        self.assertEqual(
            record["leasePath"],
            "/workspace/new-project/.subactor/leases/"
            "ticket-178--adopt-worktrees-v4.json",
        )
        self.assertEqual(record["linkMode"], "relative")
        self.assertEqual(record["minimumGitVersion"], "2.51.0")
        self.assertEqual(checker.validate(record), [])
        record["worktreePath"] = (
            "/workspace/.worktrees/.branches/new-project/"
            "ticket-178--adopt-worktrees-v4"
        )
        self.assertIn("noncanonical:worktreePath", checker.validate(record))

        windows = checker.plan(
            repository="wellmanifest/new-project",
            repository_name="new-project",
            ticket="ticket-178",
            slug="adopt-worktrees-v4",
            primary_checkout=r"C:\workspace\new-project",
            path_style="windows",
        )
        self.assertEqual(
            windows["worktreePath"],
            r"C:\workspace\new-project\worktrees\ticket-178--adopt-worktrees-v4",
        )
        self.assertEqual(
            windows["leasePath"],
            r"C:\workspace\new-project\.subactor\leases\ticket-178--adopt-worktrees-v4.json",
        )

    def test_inventory_classifies_every_recovery_layout_without_effects(self):
        checker = load_checker()
        primary = "/workspace/new-project"
        registered = [
            {"path": primary, "head": "a" * 40, "branch": "refs/heads/main"},
            {
                "path": f"{primary}/worktrees/ticket-178--adopt-worktrees-v4",
                "head": "b" * 40,
                "branch": "refs/heads/ticket/178-adopt-worktrees-v4",
            },
            {
                "path": (
                    "/workspace/.worktrees/.branches/new-project/"
                    "ticket-179--legacy-v3"
                ),
                "head": "c" * 40,
                "branch": "refs/heads/ticket/179-legacy-v3",
            },
            {
                "path": "/workspace/.worktrees/new-project/ticket-180--legacy-v2",
                "head": "d" * 40,
                "branch": "refs/heads/ticket/180-legacy-v2",
            },
            {
                "path": "/workspace/.worktrees/new-project--ticket-181--legacy-v1",
                "head": "e" * 40,
                "branch": "refs/heads/ticket/181-legacy-v1",
            },
            {
                "path": "/tmp/new-project-ticket-182",
                "head": "f" * 40,
                "branch": "refs/heads/ticket/182-system-temp",
            },
            {
                "path": "/workspace/elsewhere/new-project-ticket-183",
                "head": "1" * 40,
                "branch": "refs/heads/ticket/183-unknown",
            },
            {
                "path": "/workspace/duplicate-ticket-178",
                "head": "2" * 40,
                "branch": "refs/heads/ticket/178-adopt-worktrees-v4",
            },
        ]
        before = json.dumps(registered, sort_keys=True)
        inventory = checker.inventory(
            repository="wellmanifest/new-project",
            repository_name="new-project",
            primary_checkout=primary,
            registered=registered,
        )
        self.assertTrue(inventory["readOnly"])
        self.assertEqual(checker.validate(inventory), [])
        self.assertEqual(json.dumps(registered, sort_keys=True), before)
        classifications = {
            entry["path"]: entry["classification"] for entry in inventory["entries"]
        }
        self.assertEqual(classifications[primary], "primary")
        self.assertEqual(
            classifications[f"{primary}/worktrees/ticket-178--adopt-worktrees-v4"],
            "canonical-v4",
        )
        self.assertIn("legacy-v3", classifications.values())
        self.assertIn("legacy-v2", classifications.values())
        self.assertIn("legacy-v1", classifications.values())
        self.assertIn("system-temp", classifications.values())
        self.assertIn("unknown", classifications.values())
        duplicates = [
            entry
            for entry in inventory["entries"]
            if "duplicate-delivery" in entry["anomalies"]
        ]
        self.assertEqual(len(duplicates), 2)

    def test_agent_templates_and_ignores_declare_v4_boundary(self):
        agents_path = ROOT / "template" / "files" / "AGENTS.template.md"
        agents = agents_path.read_text(encoding="utf-8")
        self.assertIn(
            "<primaryCheckout>/worktrees/<ticket-NNN>--<slug>", agents
        )
        self.assertIn(".subactor/leases/<ticket-NNN>--<slug>.json", agents)
        self.assertIn("linkMode=relative", agents)
        self.assertIn("minimum Git 2.51.0", agents)
        self.assertIn("Never automatically move, repair,", agents)
        for pointer in (
            "CLAUDE.template.md", "GEMINI.template.md", "cursor-rule.template.mdc"
        ):
            text = (ROOT / "template" / "files" / pointer).read_text(encoding="utf-8")
            self.assertIn("AGENTS.md", text, pointer)
        ignores = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
        self.assertIn("/worktrees/", ignores)
        for directory in (
            "leases", "sessions", "recovery", "receipts", "cache", "snapshots"
        ):
            self.assertIn(f"/.subactor/{directory}/", ignores)
        self.assertNotIn("/.subactor/", ignores)
        manifest = ROOT / ".subactor" / "manifest.json"
        self.assertTrue(manifest.is_file())
        self.assertFalse(
            subprocess.run(
                ["git", "-C", str(ROOT), "check-ignore", "--quiet", str(manifest)],
                check=False,
            ).returncode == 0
        )

    def test_feature_probe_requires_version_and_both_options(self):
        checker = load_checker()

        def runner(arguments, **_kwargs):
            if arguments == ["git", "--version"]:
                output = b"git version 2.51.0\n"
            elif arguments[-2:] == ["add", "-h"]:
                output = b"usage: git worktree add --relative-paths\n"
            elif arguments[-2:] == ["repair", "-h"]:
                output = b"usage: git worktree repair --relative-paths\n"
            else:
                raise AssertionError(arguments)
            return subprocess.CompletedProcess(arguments, 0, output, b"")

        self.assertTrue(checker.feature_probe(runner=runner)["supported"])

        def missing_repair(arguments, **kwargs):
            result = runner(arguments, **kwargs)
            if arguments[-2:] == ["repair", "-h"]:
                return subprocess.CompletedProcess(arguments, 0, b"usage: repair\n", b"")
            return result

        self.assertFalse(checker.feature_probe(runner=missing_repair)["supported"])

    def test_relative_scratch_worktree_survives_primary_rename_and_exact_repair(self):
        checker = load_checker()
        probe = checker.feature_probe()
        if not probe["supported"]:
            self.skipTest(f"Git lacks Worktrees v4 relative feature: {probe}")

        with tempfile.TemporaryDirectory(prefix="new-project-v4-") as temporary:
            root = pathlib.Path(temporary)
            primary = root / "sample"
            renamed = root / "renamed-sample"
            run("git", "init", "--quiet", "--initial-branch=main", str(primary))
            run("git", "-C", str(primary), "config", "user.email", "v4@example.invalid")
            run("git", "-C", str(primary), "config", "user.name", "v4-test")
            (primary / ".gitignore").write_text("/worktrees/\n/.subactor/\n", encoding="utf-8")
            (primary / "README.md").write_text("sample\n", encoding="utf-8")
            run("git", "-C", str(primary), "add", ".gitignore", "README.md")
            run("git", "-C", str(primary), "commit", "--quiet", "-m", "initial")
            linked = primary / "worktrees" / "ticket-201--rename-safe"
            run(
                "git", "-C", str(primary), "worktree", "add", "--relative-paths",
                "--quiet", "-b", "ticket/201-rename-safe", str(linked),
            )
            pointer = (linked / ".git").read_text(encoding="utf-8").strip()
            self.assertFalse(os.path.isabs(pointer.removeprefix("gitdir: ")), pointer)
            primary.rename(renamed)
            moved_linked = renamed / "worktrees" / "ticket-201--rename-safe"
            self.assertEqual(run("git", "-C", str(moved_linked), "rev-parse", "HEAD"),
                             run("git", "-C", str(renamed), "rev-parse", "HEAD"))
            run(
                "git", "-C", str(renamed), "worktree", "repair", "--relative-paths",
                str(moved_linked),
            )
            self.assertEqual(
                pathlib.Path(checker.resolve_primary_checkout(str(moved_linked))),
                renamed,
            )
            record = checker.plan(
                repository="example/sample",
                repository_name="sample",
                ticket="ticket-201",
                slug="rename-safe",
                primary_checkout=str(renamed),
                path_style="windows" if os.name == "nt" else "posix",
            )
            self.assertEqual(pathlib.Path(record["worktreePath"]), moved_linked)
            self.assertEqual(checker.validate_filesystem(record), [])


if __name__ == "__main__":
    unittest.main()
