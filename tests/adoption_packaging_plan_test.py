#!/usr/bin/env python3
"""Regression tests for native adoption packaging declaration planning (#548)."""

from __future__ import annotations

import contextlib
import copy
import hashlib
import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]

RICH_PYPROJECT_TEMPLATE = """# Historical adopter packaging metadata (modeled on subactor/autonom)
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "autonom-fixture"
version = "0.1.0"
description = '''
Multiline literal description containing fake headers:
[tool.wellmanifest]
standard = "0.0.0"
revision = "0000000000000000000000000000000000000000"
'''
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    "pydantic>=2.7",  # keep trailing comment intact
    "httpx>=0.27",
]

[tool.wellmanifest]
# Pinned standard metadata verified by agent_host_check.py
standard = "{standard}"  # version comment preserved
revision = '{revision}'
gate = "project/governance-check.sh"

[tool.pytest.ini_options]
addopts = "-q -p wellmanifest_governance"
testpaths = ["tests"]
"""

RICH_PACKAGE_JSON_TEMPLATE = """{{
  "name": "@fixture/autonom-web",
  "version": "0.1.0",
  "private": true,
  "scripts": {{
    "prepare": "bash ./scripts/install-agent-hosts.sh",
    "test": "node --test"
  }},
  "wellmanifest": {{
    "gate": "project/governance-check.sh",
    "revision": "{revision}",
    "standard": "{standard}"
  }},
  "dependencies": {{
    "zod": "^3.23.8"
  }}
}}
"""


class HistoricalPythonAdopterTest(unittest.TestCase):
    """Real Git/package fixture reproducing #548 end-to-end."""

    @classmethod
    def command(cls, root: Path, *args: str, check: bool = True, env: dict[str, str] | None = None):
        environment = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        if env is not None:
            environment.update(env)
        result = subprocess.run(
            args, cwd=root, text=True, capture_output=True, check=False, env=environment,
        )
        if check and result.returncode:
            raise AssertionError(f"Command {args} failed ({result.returncode}):\n{result.stdout}\n{result.stderr}")
        return result

    @staticmethod
    def load_adopter(source: Path):
        spec = importlib.util.spec_from_file_location(
            "packaging_plan_fixture_adopter", source / "scripts/create_adoption_lock.py",
        )
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    @classmethod
    def setUpClass(cls):
        cache = ROOT / ".subactor/cache/adoption-packaging-tests"
        cache.mkdir(parents=True, exist_ok=True)
        cls.temporary = tempfile.TemporaryDirectory(prefix="pkg548-", dir=cache)
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.base = Path(cls.temporary.name)
        cls.version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        cls.old_version = "0.20.35"

        cls.source = cls.base / "standard"
        cls.command(cls.base, "git", "clone", "--quiet", "--no-hardlinks", str(ROOT), str(cls.source))
        for key, value in (
            ("user.name", "Fixture"),
            ("user.email", "fixture@example.invalid"),
            ("core.hooksPath", os.devnull),
            ("core.excludesFile", os.devnull),
        ):
            cls.command(cls.source, "git", "config", key, value)

        # Simulate historical 0.20.35 source revision prior to incoming upgrade.
        (cls.source / "VERSION").write_text(cls.old_version + "\n", encoding="utf-8")
        for manifest_rel in ("governance/manifest.default.json", "governance/manifest.hub.json"):
            mpath = cls.source / manifest_rel
            mdoc = json.loads(mpath.read_text(encoding="utf-8"))
            mdoc["standard"]["version"] = cls.old_version
            mpath.write_text(json.dumps(mdoc, indent=2) + "\n", encoding="utf-8")
        cls.command(cls.source, "git", "add", ".")
        cls.command(cls.source, "git", "commit", "--quiet", "-m", "Fixture historical 0.20.35 standard")
        cls.old_revision = cls.command(cls.source, "git", "rev-parse", "HEAD").stdout.strip()
        old_adopter = cls.load_adopter(cls.source)

        # Build historical adopter template repository with installed 0.20.35 + pyproject.toml.
        cls.template = cls.base / "template"
        cls.command(cls.base, "git", "init", "--quiet", "-b", "main", str(cls.template))
        for key, value in (
            ("user.name", "Fixture"),
            ("user.email", "fixture@example.invalid"),
            ("core.hooksPath", os.devnull),
            ("core.excludesFile", os.devnull),
        ):
            cls.command(cls.template, "git", "config", key, value)
        cls.command(
            cls.template, "git", "remote", "add", "origin", "https://github.com/subactor/autonom-fixture.git",
        )
        for name in ("README.md", "VERSION", "CHANGELOG.md", "TODO.md", "project/TICKETS.md"):
            target_file = cls.template / name
            target_file.parent.mkdir(parents=True, exist_ok=True)
            target_file.write_text("0.1.0\n" if name == "VERSION" else "# Fixture\n", encoding="utf-8")
        with (
            patch.object(
                sys, "argv",
                ["adopter", "--target-root", str(cls.template), "--source-revision", cls.old_revision, "--upgrade"],
            ),
            patch.object(old_adopter, "verify_publication_evidence"),
            contextlib.redirect_stdout(io.StringIO()),
        ):
            assert old_adopter.main() == 0
        (cls.template / "pyproject.toml").write_text(
            RICH_PYPROJECT_TEMPLATE.format(standard=cls.old_version, revision=cls.old_revision),
            encoding="utf-8",
        )
        cls.command(cls.template, "git", "config", "core.hooksPath", os.devnull)
        cls.command(cls.template, "git", "add", ".")
        cls.command(cls.template, "git", "commit", "--quiet", "-m", "Installed 0.20.35 with pyproject.toml")

        # Advance standard source to current incoming package with updated create_adoption_lock.py.
        incoming_package = json.loads((ROOT / "governance/package-manifest.json").read_text(encoding="utf-8"))
        incoming_sources = {item["source"] for item in incoming_package["files"]}
        incoming_sources.update((
            "project/new-ticket.sh",
            "scripts/create_adoption_lock.py",
            "governance/package-manifest.json",
            "governance/standard-adoption-plan.schema.json",
            "governance/manifest.default.json",
            "governance/manifest.hub.json",
            "packages/wellman/pyproject.toml",
            "VERSION",
        ))
        for name in sorted(incoming_sources):
            dest = cls.source / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / name, dest)
        cls.command(cls.source, "git", "add", ".")
        cls.command(cls.source, "git", "commit", "--quiet", "-m", "Incoming standard package")
        cls.revision = cls.command(cls.source, "git", "rev-parse", "HEAD").stdout.strip()
        cls.adopter = cls.load_adopter(cls.source)

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="case-", dir=self.base)
        self.addCleanup(temporary.cleanup)
        self.case = Path(temporary.name)
        self.target = self.case / "autonom"
        self.command(self.case, "git", "clone", "--quiet", "--no-hardlinks", str(self.template), str(self.target))
        for key, value in (
            ("user.name", "Fixture"),
            ("user.email", "fixture@example.invalid"),
            ("core.hooksPath", os.devnull),
            ("core.excludesFile", os.devnull),
        ):
            self.command(self.target, "git", "config", key, value)
        self.plan_path = self.case / "allocation-plan.json"

    def export_plan(self, *extra_args: str) -> dict:
        out = io.StringIO()
        with patch.object(self.adopter, "verify_publication_evidence"), contextlib.redirect_stdout(out):
            rc = self.adopter.main([
                "--target-root", str(self.target),
                "--source-revision", self.revision,
                "--check", "--allocation-plan",
                *extra_args,
            ])
        self.assertEqual(rc, 0)
        plan = json.loads(out.getvalue())
        self.plan_path.write_text(json.dumps(plan), encoding="utf-8")
        return plan

    def run_check(self, root: Path | None = None) -> tuple[int, str]:
        out = io.StringIO()
        with patch.object(self.adopter, "verify_publication_evidence"), contextlib.redirect_stdout(out):
            rc = self.adopter.main([
                "--target-root", str(root or self.target),
                "--source-revision", self.revision,
                "--check",
            ])
        return rc, out.getvalue()

    def run_upgrade(self, root: Path | None = None) -> tuple[int, str]:
        out = io.StringIO()
        with patch.object(self.adopter, "verify_publication_evidence"), contextlib.redirect_stdout(out):
            rc = self.adopter.main([
                "--target-root", str(root or self.target),
                "--source-revision", self.revision,
                "--upgrade",
            ])
        return rc, out.getvalue()

    def publication_environment(self) -> dict[str, str]:
        support = self.case / "publication-io"
        support.mkdir(exist_ok=True)
        real_git = shutil.which("git")
        assert real_git is not None
        (support / "git").write_text(
            "#!/bin/sh\nif [ \"$1\" = ls-remote ]; then\n"
            f"printf '%s\\n' '{'a' * 40} refs/tags/v{self.version}' '{self.revision} refs/tags/v{self.version}^{{}}'\n"
            f"else exec '{real_git}' \"$@\"; fi\n",
            encoding="utf-8",
        )
        (support / "git").chmod(0o755)
        (support / "gh").write_text("#!/bin/sh\nprintf '%s\\n' fixture-publication-token\n", encoding="utf-8")
        (support / "gh").chmod(0o755)
        (support / "sitecustomize.py").write_text(
            "import io, json, urllib.request\n"
            "def fixture_release(request, **kwargs):\n"
            f"    assert request.full_url == 'https://api.github.com/repos/wellmanifest/new-project/releases/tags/v{self.version}'\n"
            f"    return io.BytesIO(json.dumps({{'tag_name': 'v{self.version}', 'draft': False, 'prerelease': False, 'published_at': '2026-01-01T00:00:00Z'}}).encode())\n"
            "urllib.request.urlopen = fixture_release\n",
            encoding="utf-8",
        )
        environment = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
        environment.update(
            PATH=str(support) + os.pathsep + environment["PATH"],
            PYTHONPATH=str(support),
            PYTHONDONTWRITEBYTECODE="1",
            GH_TOKEN="fixture",
        )
        environment.pop("GITHUB_TOKEN", None)
        return environment

    def test_allocation_plan_includes_pyproject_allocates_ticket_and_passes_upgraded_gate(self):
        plan = self.export_plan()
        self.assertIn("pyproject.toml", plan["allowedPaths"])
        self.assertIn("pyproject.toml", plan["target"]["files"])
        self.assertIsNotNone(plan["target"]["files"]["pyproject.toml"])

        file_entries = {item["path"]: item for item in plan["files"]}
        self.assertIn("pyproject.toml", file_entries)
        self.assertEqual(file_entries["pyproject.toml"]["strategy"], "generated")
        self.assertEqual(file_entries["pyproject.toml"]["gitMode"], "100644")

        from jsonschema import Draft202012Validator
        schema = json.loads((ROOT / "governance/standard-adoption-plan.schema.json").read_text(encoding="utf-8"))
        Draft202012Validator(schema).validate(plan)

        # Allocate native governance ticket using the new standard's new-ticket.sh & plan.
        pub_env = self.publication_environment()
        alloc = self.command(
            self.target,
            "bash", str(self.source / "project/new-ticket.sh"),
            "--title", "Upgrade standard package (#548)",
            "--agent", "fixture",
            "--writer-actor", "agent:fixture",
            "--writer-session", "fixture-upgrade-548",
            "--workstream", "governance",
            "--worktree-slug", "upgrade-548",
            "--standard-adoption-plan", str(self.plan_path),
            env=pub_env,
        )
        self.assertIn("Successfully allocated ticket-001", alloc.stdout)
        wt = self.target / ".worktrees/ticket-001--upgrade-548"
        intent = json.loads((wt / "project/ticket-001/intent.json").read_text(encoding="utf-8"))
        self.assertIn("pyproject.toml", intent["allowedPaths"])

        # Apply upgrade inside the allocated worktree.
        rc, _ = self.run_upgrade(wt)
        self.assertEqual(rc, 0)

        # Unrelated metadata, comments, quote styles, and multiline strings must match byte-for-byte.
        expected_pyproject = RICH_PYPROJECT_TEMPLATE.format(
            standard=self.version, revision=self.revision,
        ).encode("utf-8")
        self.assertEqual((wt / "pyproject.toml").read_bytes(), expected_pyproject)
        self.assertEqual(
            hashlib.sha256(expected_pyproject).hexdigest(),
            file_entries["pyproject.toml"]["sha256"],
        )

        # Managed hash closure must NEVER include target-owned pyproject.toml.
        upgraded_lock = json.loads((wt / ".governance/manifest.lock.json").read_text(encoding="utf-8"))
        self.assertNotIn("pyproject.toml", upgraded_lock["managedFiles"])

        # Post-upgrade --check must pass cleanly.
        check_rc, check_out = self.run_check(wt)
        self.assertEqual(check_rc, 0, check_out)
        self.assertIn("up-to-date", check_out)

        # Complete ticket README metadata and commit inside worktree with valid lease fencing,
        # then verify both agent_host_check.py and full governance-check.sh pass!
        readme_path = wt / "project/ticket-001/README.md"
        readme_text = readme_path.read_text(encoding="utf-8").replace(
            "- **Owner**: unresolved:human", "- **Owner**: agent:fixture",
        )
        readme_path.write_text(readme_text, encoding="utf-8")
        lease = json.loads(
            (self.target / ".subactor/leases/ticket-001--upgrade-548.json").read_text(encoding="utf-8")
        )
        commit_env = {
            "NEW_PROJECT_WRITER_ACTOR": lease["ownerActor"],
            "NEW_PROJECT_WRITER_SESSION": lease["ownerSession"],
            "NEW_PROJECT_LEASE_REVISION": str(lease["leaseRevision"]),
            "NEW_PROJECT_FENCING_TOKEN": str(lease["fencingToken"]),
        }
        self.command(wt, "bash", "./scripts/install-agent-hosts.sh", "--target", str(wt))
        self.command(wt, "git", "add", "-A")
        self.command(
            wt, "git", "commit", "--quiet",
            "-m", "chore(governance): adopt standard upgrade [ticket-001]",
            env=commit_env,
        )

        host_res = self.command(
            wt, sys.executable, str(wt / ".governance/agent_host_check.py"),
            "--root", str(wt), "--format", "json",
        )
        host_report = json.loads(host_res.stdout)
        packaging_findings = [
            f for f in host_report["findings"] if f["code"].startswith("GOV-PACKAGING-")
        ]
        self.assertEqual(packaging_findings, [], host_report)

        gov_res = self.command(wt, "bash", "./project/governance-check.sh", env=commit_env)
        self.assertIn("GOV-PASS", gov_res.stdout)

    def test_check_distinguishes_inconsistent_upgrade_from_up_to_date(self):
        stale_bytes = (self.target / "pyproject.toml").read_bytes()
        rc, _ = self.run_upgrade(self.target)
        self.assertEqual(rc, 0)
        self.assertEqual(self.run_check(self.target)[0], 0)

        # Simulate an internally inconsistent upgrade where lock/managed files updated
        # but pyproject.toml kept the old standard/revision.
        (self.target / "pyproject.toml").write_bytes(stale_bytes)
        rc, output = self.run_check(self.target)
        self.assertEqual(rc, 1, output)
        self.assertNotIn("up-to-date", output)
        self.assertIn("UPDATE pyproject.toml", output)

    def test_node_package_json_plan_and_byte_preserving_upgrade(self):
        pkg_path = self.target / "package.json"
        pkg_path.write_text(
            RICH_PACKAGE_JSON_TEMPLATE.format(standard=self.old_version, revision=self.old_revision),
            encoding="utf-8",
        )
        self.command(self.target, "git", "add", "package.json")
        self.command(self.target, "git", "commit", "--quiet", "-m", "Add package.json declaration")
        self.command(self.target, "git", "update-ref", "refs/remotes/origin/main", "HEAD")

        plan = self.export_plan()
        self.assertIn("package.json", plan["allowedPaths"])
        self.assertIn("pyproject.toml", plan["allowedPaths"])

        rc, _ = self.run_upgrade(self.target)
        self.assertEqual(rc, 0)

        expected_pkg = RICH_PACKAGE_JSON_TEMPLATE.format(
            standard=self.version, revision=self.revision,
        ).encode("utf-8")
        self.assertEqual(pkg_path.read_bytes(), expected_pkg)
        upgraded_lock = json.loads((self.target / ".governance/manifest.lock.json").read_text(encoding="utf-8"))
        self.assertNotIn("package.json", upgraded_lock["managedFiles"])
        self.assertEqual(self.run_check(self.target)[0], 0)

    def test_missing_authority_refuses_plan_and_allocation(self):
        with (
            patch.object(self.adopter, "verify_publication_evidence", side_effect=SystemExit("unpublished")),
            self.assertRaisesRegex(SystemExit, "unpublished"),
        ):
            self.adopter.main([
                "--target-root", str(self.target),
                "--source-revision", self.revision,
                "--check", "--allocation-plan",
            ])
        with self.assertRaises(SystemExit):
            self.adopter.main([
                "--target-root", str(self.target),
                "--source-revision", self.revision,
                "--check", "--allocation-plan", "--allow-unpublished-for-testing",
            ])

        self.export_plan()
        with patch.object(self.adopter, "verify_publication_evidence"):
            with self.assertRaisesRegex(SystemExit, "workstream"):
                self.adopter.verify_allocation_plan(self.plan_path, self.target, "integration")

        # Missing explicit writer session paired with writer actor must refuse native allocation.
        pub_env = self.publication_environment()
        denied = self.command(
            self.target,
            "bash", str(self.source / "project/new-ticket.sh"),
            "--title", "Unauthorized upgrade",
            "--writer-actor", "agent:fixture",
            "--workstream", "governance",
            "--worktree-slug", "denied-upgrade",
            "--standard-adoption-plan", str(self.plan_path),
            check=False,
            env=pub_env,
        )
        self.assertNotEqual(denied.returncode, 0)
        self.assertFalse((self.target / ".worktrees/ticket-001--denied-upgrade").exists())

    def test_stale_target_refuses_recomputation(self):
        self.export_plan()
        pyproject = self.target / "pyproject.toml"
        original = pyproject.read_bytes()

        # 1. Post-export modification to pyproject.toml invalidates plan.
        pyproject.write_bytes(original + b"# concurrent edit\n")
        with patch.object(self.adopter, "verify_publication_evidence"):
            with self.assertRaisesRegex(SystemExit, "stale|unmanaged"):
                self.adopter.verify_allocation_plan(self.plan_path, self.target, "governance")
        pyproject.write_bytes(original)

        # 2. Index mutation without worktree status change invalidates plan.
        self.command(self.target, "git", "update-index", "--assume-unchanged", "README.md")
        with patch.object(self.adopter, "verify_publication_evidence"):
            with self.assertRaisesRegex(SystemExit, "stale"):
                self.adopter.verify_allocation_plan(self.plan_path, self.target, "governance")
        self.command(self.target, "git", "update-index", "--no-assume-unchanged", "README.md")

        # 3. HEAD advance invalidates plan.
        self.command(self.target, "git", "commit", "--quiet", "--allow-empty", "-m", "Concurrent HEAD")
        with patch.object(self.adopter, "verify_publication_evidence"):
            with self.assertRaisesRegex(SystemExit, "stale|alias"):
                self.adopter.verify_allocation_plan(self.plan_path, self.target, "governance")

    def test_conflicting_or_missing_ownership_refuses_with_actionable_diagnostics(self):
        manifest_path = self.target / ".governance/manifest.json"
        original_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

        # Case 1: Claimed exclusively by application workstream.
        app_owned = copy.deepcopy(original_manifest)
        app_owned["coordination"]["workstreams"]["integration"]["ownedPaths"] = [
            p for p in app_owned["coordination"]["workstreams"]["integration"]["ownedPaths"]
            if p != "pyproject.toml"
        ]
        app_owned["coordination"]["workstreams"]["application"]["ownedPaths"].append("pyproject.toml")
        manifest_path.write_text(json.dumps(app_owned, indent=2) + "\n", encoding="utf-8")
        self.command(self.target, "git", "add", ".governance/manifest.json")
        self.command(self.target, "git", "commit", "--quiet", "-m", "Application claims pyproject.toml")
        self.command(self.target, "git", "update-ref", "refs/remotes/origin/main", "HEAD")
        with self.assertRaisesRegex(SystemExit, r"pyproject\.toml.*conflicting workstream ownership.*application"):
            self.export_plan()

        # Case 2: Overlapping ownership across integration and infrastructure.
        overlapping = copy.deepcopy(original_manifest)
        overlapping["coordination"]["workstreams"]["infrastructure"]["ownedPaths"].append("pyproject.toml")
        manifest_path.write_text(json.dumps(overlapping, indent=2) + "\n", encoding="utf-8")
        self.command(self.target, "git", "add", ".governance/manifest.json")
        self.command(self.target, "git", "commit", "--quiet", "-m", "Overlapping pyproject.toml owners")
        self.command(self.target, "git", "update-ref", "refs/remotes/origin/main", "HEAD")
        with self.assertRaisesRegex(
            SystemExit, r"pyproject\.toml.*conflicting workstream ownership.*infrastructure, integration"
        ):
            self.export_plan()

        # Case 3: Unowned by any workstream.
        unowned = copy.deepcopy(original_manifest)
        unowned["coordination"]["workstreams"]["integration"]["ownedPaths"] = [
            p for p in unowned["coordination"]["workstreams"]["integration"]["ownedPaths"]
            if p != "pyproject.toml"
        ]
        manifest_path.write_text(json.dumps(unowned, indent=2) + "\n", encoding="utf-8")
        self.command(self.target, "git", "add", ".governance/manifest.json")
        self.command(self.target, "git", "commit", "--quiet", "-m", "Unowned pyproject.toml")
        self.command(self.target, "git", "update-ref", "refs/remotes/origin/main", "HEAD")
        with self.assertRaisesRegex(SystemExit, r"pyproject\.toml.*no owning workstream"):
            self.export_plan()

    def test_unmanaged_edits_to_pyproject_refuse_allocation_plan(self):
        pyproject = self.target / "pyproject.toml"
        committed = pyproject.read_bytes()

        # Working-tree dirty edit.
        pyproject.write_bytes(committed + b"\n# local unmanaged edit\n")
        with self.assertRaisesRegex(SystemExit, r"pyproject\.toml has unmanaged local edits"):
            self.export_plan()

        # Staged index edit.
        self.command(self.target, "git", "add", "pyproject.toml")
        with self.assertRaisesRegex(SystemExit, r"pyproject\.toml has unmanaged local edits"):
            self.export_plan()

        self.command(self.target, "git", "reset", "--hard", "--quiet", "HEAD")
        self.assertEqual(pyproject.read_bytes(), committed)

    def test_missing_or_malformed_declarations_fail_closed_across_modes(self):
        pyproject = self.target / "pyproject.toml"
        lock_before = (self.target / ".governance/manifest.lock.json").read_bytes()

        bad_cases = [
            ("malformed_toml", "[project\nname = 'broken'\n"),
            ("missing_block", '[project]\nname = "x"\n[tool.pytest.ini_options]\naddopts = "-p wellmanifest_governance"\n'),
            ("missing_revision", '[tool.wellmanifest]\nstandard = "0.20.35"\ngate = "project/governance-check.sh"\n[tool.pytest.ini_options]\naddopts = "-p wellmanifest_governance"\n'),
            ("unsafe_gate", f'[tool.wellmanifest]\nstandard = "0.20.35"\nrevision = "{self.old_revision}"\ngate = "../escape.sh"\n[tool.pytest.ini_options]\naddopts = "-p wellmanifest_governance"\n'),
            ("missing_lifecycle", f'[tool.wellmanifest]\nstandard = "0.20.35"\nrevision = "{self.old_revision}"\ngate = "project/governance-check.sh"\n'),
        ]
        for label, content in bad_cases:
            with self.subTest(case=label):
                pyproject.write_text(content, encoding="utf-8")
                with self.assertRaisesRegex(SystemExit, "invalid target packaging declaration"):
                    self.export_plan()
                with self.assertRaisesRegex(SystemExit, "invalid target packaging declaration"):
                    self.run_upgrade()
                self.assertEqual((self.target / ".governance/manifest.lock.json").read_bytes(), lock_before)
                rc, check_out = self.run_check()
                self.assertEqual(rc, 1, check_out)
                self.assertNotIn("up-to-date", check_out)
                self.assertIn("INVALID packaging declaration", check_out)

        # Symlinked packaging marker must fail closed immediately.
        pyproject.unlink()
        pyproject.symlink_to(self.target / "README.md")
        with self.assertRaisesRegex(SystemExit, "symlink"):
            self.export_plan()
        with self.assertRaisesRegex(SystemExit, "symlink"):
            self.run_check()


if __name__ == "__main__":
    unittest.main()
