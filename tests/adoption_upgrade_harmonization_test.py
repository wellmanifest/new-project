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


class AdoptionHarmonizationTest(unittest.TestCase):
    def test_default_manifest_workstreams_are_orthogonal(self):
        manifest_path = ROOT / "governance" / "manifest.default.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        coordination = manifest["coordination"]
        workstreams = coordination["workstreams"]

        gov_owned = set(workstreams["governance"]["ownedPaths"])
        integration_owned = set(workstreams["integration"]["ownedPaths"])
        integration_required = set(coordination["integration"]["requiredForPaths"])

        # 1. Integration requiredForPaths must not claim governance-owned standard files
        for forbidden in (".governance/**", "AGENTS.md", ".subactor/manifest.json", ".governance/manifest.json"):
            self.assertNotIn(
                forbidden,
                integration_required,
                f"{forbidden} should not be in integration.requiredForPaths",
            )
            self.assertNotIn(
                forbidden,
                integration_owned,
                f"{forbidden} should not be in integration.ownedPaths",
            )

        # 2. Governance workstream must own standard files
        for required_gov in (
            ".aider.conf.yml",
            ".cursor/rules/**",
            ".githooks/**",
            ".github/copilot-instructions.md",
            ".github/workflows/new-project-governance.yml",
            ".gitignore",
            ".governance/**",
            ".subactor/**",
            "AGENTS.md",
            "CLAUDE.md",
            "GEMINI.md",
            "wellmanifest_governance.py",
            "worktree-guard.yaml",
        ):
            self.assertIn(
                required_gov,
                gov_owned,
                f"{required_gov} must be declared in governance.ownedPaths",
            )

        # 3. Governance and integration must not have exact duplicate path entries
        overlap = gov_owned.intersection(integration_owned)
        self.assertEqual(overlap, set(), f"governance and integration ownedPaths overlap on {overlap}")


class AdoptionPlanFixture:
    """Real Git/package fixtures; only external publication IO is mocked."""

    @classmethod
    def command(cls, root, *args, check=True, env=None):
        environment = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        result = subprocess.run(args, cwd=root, text=True, capture_output=True, check=False,
                                env=env or environment)
        if check and result.returncode:
            raise AssertionError(result.stdout + result.stderr)
        return result

    @staticmethod
    def load_adopter(source):
        spec = importlib.util.spec_from_file_location("plan_fixture_adopter", source / "scripts/create_adoption_lock.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    @classmethod
    def setUpClass(cls):
        cache = ROOT / ".subactor/cache/adoption-allocation-tests"
        cache.mkdir(parents=True, exist_ok=True)
        cls.temporary = tempfile.TemporaryDirectory(prefix="case-", dir=cache)
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.base = Path(cls.temporary.name)
        cls.version = (ROOT / "VERSION").read_text().strip()
        cls.source = cls.base / "standard"
        cls.command(cls.base, "git", "clone", "--quiet", "--no-hardlinks", str(ROOT), str(cls.source))
        for key, value in (("user.name", "Fixture"), ("user.email", "fixture@example.invalid"),
                           ("core.hooksPath", os.devnull), ("core.excludesFile", os.devnull)):
            cls.command(cls.source, "git", "config", key, value)
        # A genuine older package lacks incoming ownership and two targets.
        p = cls.source / "governance/package-manifest.json"
        package = json.loads(p.read_text())
        missing = {".gitattributes", ".github/workflows/new-project-branch-hygiene.yml"}
        package["files"] = [item for item in package["files"] if item["target"] not in missing]
        p.write_text(json.dumps(package, indent=2) + "\n")
        p = cls.source / "governance/manifest.default.json"
        manifest = json.loads(p.read_text())
        manifest["coordination"]["workstreams"]["governance"]["ownedPaths"] = [
            name for name in manifest["coordination"]["workstreams"]["governance"]["ownedPaths"]
            if name not in missing]
        p.write_text(json.dumps(manifest, indent=2) + "\n")
        cls.command(cls.source, "git", "add", ".")
        cls.command(cls.source, "git", "commit", "--quiet", "-m", "Fixture old package")
        cls.old_revision = cls.command(cls.source, "git", "rev-parse", "HEAD").stdout.strip()
        old_adopter = cls.load_adopter(cls.source)
        cls.template = cls.base / "template"
        cls.command(cls.base, "git", "init", "--quiet", "-b", "main", str(cls.template))
        for key, value in (("user.name", "Fixture"), ("user.email", "fixture@example.invalid"),
                           ("core.hooksPath", os.devnull), ("core.excludesFile", os.devnull)):
            cls.command(cls.template, "git", "config", key, value)
        for name in ("README.md", "VERSION", "CHANGELOG.md", "TODO.md", "project/TICKETS.md"):
            p = cls.template / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("0.1.0\n" if name == "VERSION" else "# Fixture\n")
        with patch.object(sys, "argv", ["adopter", "--target-root", str(cls.template),
                "--source-revision", cls.old_revision, "--upgrade"]), \
                patch.object(old_adopter, "verify_publication_evidence"), contextlib.redirect_stdout(io.StringIO()):
            assert old_adopter.main() == 0
        cls.command(cls.template, "git", "config", "core.hooksPath", os.devnull)
        cls.command(cls.template, "git", "add", ".")
        cls.command(cls.template, "git", "commit", "--quiet", "-m", "Fixture installed native base")
        incoming_package = json.loads((ROOT / "governance/package-manifest.json").read_text())
        incoming_sources = {item["source"] for item in incoming_package["files"]}
        incoming_sources.update(("project/new-ticket.sh", "scripts/create_adoption_lock.py",
                     "governance/package-manifest.json", "governance/standard-adoption-plan.schema.json",
                     "governance/manifest.default.json", "governance/manifest.hub.json",
                     "packages/wellman/pyproject.toml", "VERSION"))
        for name in sorted(incoming_sources):
            (cls.source / name).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / name, cls.source / name)
        cls.command(cls.source, "git", "add", ".")
        cls.command(cls.source, "git", "commit", "--quiet", "-m", "Fixture incoming immutable package")
        cls.revision = cls.command(cls.source, "git", "rev-parse", "HEAD").stdout.strip()
        cls.adopter = cls.load_adopter(cls.source)

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="case-", dir=self.base)
        self.addCleanup(temporary.cleanup)
        self.case = Path(temporary.name)
        self.target = self.case / "product"
        self.command(self.case, "git", "clone", "--quiet", "--no-hardlinks", str(self.template), str(self.target))
        for key, value in (("user.name", "Fixture"), ("user.email", "fixture@example.invalid"),
                           ("core.hooksPath", os.devnull), ("core.excludesFile", os.devnull)):
            self.command(self.target, "git", "config", key, value)
        self.plan_path = self.target / ".subactor/receipts/allocation-plan.json"
        self.plan_path.parent.mkdir(parents=True)

    def export(self):
        output = io.StringIO()
        with patch.object(self.adopter, "verify_publication_evidence"), contextlib.redirect_stdout(output):
            result = self.adopter.main(["--target-root", str(self.target),
                "--source-revision", self.revision, "--check", "--allocation-plan"])
        self.assertEqual(result, 0)
        plan = json.loads(output.getvalue())
        self.plan_path.write_text(json.dumps(plan))
        return plan

    def verify(self, **kwargs):
        with patch.object(self.adopter, "verify_publication_evidence"):
            return self.adopter.verify_allocation_plan(self.plan_path, self.target, "governance", **kwargs)

    def publication_environment(self):
        """CLI fixture replaces only canonical tag/release transport responses."""
        support = self.case / "publication-io"
        support.mkdir()
        real_git = shutil.which("git")
        (support / "git").write_text(
            "#!/bin/sh\nif [ \"$1\" = ls-remote ]; then\n"
            f"printf '%s\\n' '{'a' * 40} refs/tags/v{self.version}' '{self.revision} refs/tags/v{self.version}^{{}}'\n"
            f"else exec '{real_git}' \"$@\"; fi\n")
        (support / "git").chmod(0o755)
        (support / "gh").write_text("#!/bin/sh\nprintf '%s\\n' fixture-publication-token\n")
        (support / "gh").chmod(0o755)
        (support / "sitecustomize.py").write_text(
            "import io,json,urllib.request\n"
            "def fixture_release(request, **kwargs):\n"
            f"    assert request.full_url == 'https://api.github.com/repos/wellmanifest/new-project/releases/tags/v{self.version}'\n"
            f"    return io.BytesIO(json.dumps({{'tag_name':'v{self.version}','draft':False,'prerelease':False,'published_at':'2026-01-01T00:00:00Z'}}).encode())\n"
            "urllib.request.urlopen = fixture_release\n")
        environment = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
        environment.update(PATH=str(support) + os.pathsep + environment["PATH"],
                           PYTHONPATH=str(support), PYTHONDONTWRITEBYTECODE="1", GH_TOKEN="fixture")
        environment.pop("GITHUB_TOKEN", None)
        return environment


class AdoptionAllocationPlanTest(AdoptionPlanFixture, unittest.TestCase):
    def test_export_is_read_only_and_independently_recomputed(self):
        before = self.command(self.target, "git", "status", "--porcelain").stdout
        plan = self.export()
        self.assertEqual(self.command(self.target, "git", "status", "--porcelain").stdout, before)
        self.assertFalse(plan["grantsAuthority"])
        self.assertTrue(plan["readOnly"])
        self.assertEqual(self.verify(), plan)
        self.assertIn(".gitattributes", plan["ownershipAdditions"])
        self.assertIn(".github/workflows/new-project-branch-hygiene.yml", plan["allowedPaths"])
        from jsonschema import Draft202012Validator
        Draft202012Validator(json.loads((ROOT / "governance/standard-adoption-plan.schema.json").read_text())).validate(plan)

    def test_caller_scope_distinguishes_absent_empty_and_exact(self):
        plan = self.export()
        self.assertEqual(self.verify(requested_paths=None), plan)
        self.assertEqual(self.verify(requested_paths=plan["allowedPaths"]), plan)
        for requested in ([], ["src/foreign.py"]):
            with self.subTest(requested=requested):
                with self.assertRaisesRegex(SystemExit, "caller scope differs"):
                    self.verify(requested_paths=requested)

    def test_modified_plan_fields_and_numeric_boolean_are_rejected(self):
        original = self.export()
        for name, value in (("grantsAuthority", True), ("readOnly", 1), ("unknown", False),
                            ("allowedPaths", ["src/foreign.py"]), ("digest", "0" * 64)):
            with self.subTest(field=name):
                modified = copy.deepcopy(original)
                modified[name] = value
                self.plan_path.write_text(json.dumps(modified))
                with self.assertRaises(SystemExit):
                    self.verify()

    def test_head_advance_refuses_stale_plan(self):
        self.export()
        self.command(self.target, "git", "commit", "--quiet", "--allow-empty", "-m", "Moved base")
        with self.assertRaises(SystemExit):
            self.verify()

    def test_dirty_content_changes_refuse_even_with_same_status_letters(self):
        path = self.target / "foreign.txt"
        path.write_text("first\n")
        self.export()
        path.write_text("second\n")
        with self.assertRaises(SystemExit):
            self.verify()

    def test_mode_change_refuses_stale_plan(self):
        self.export()
        path = self.target / "README.md"
        path.chmod(path.stat().st_mode ^ 0o100)
        with self.assertRaises(SystemExit):
            self.verify()

    def test_index_change_is_bound_even_without_worktree_status_change(self):
        self.export()
        before = self.command(self.target, "git", "status", "--porcelain").stdout
        self.command(self.target, "git", "update-index", "--assume-unchanged", "README.md")
        self.assertEqual(self.command(self.target, "git", "status", "--porcelain").stdout, before)
        with self.assertRaises(SystemExit):
            self.verify()

    def test_broken_managed_hash_closure_is_rejected(self):
        path = self.target / ".governance/diagnostics.json"
        path.write_bytes(path.read_bytes() + b"\n")
        with self.assertRaises(SystemExit):
            self.export()

    def test_publication_failure_and_root_traversal_are_rejected(self):
        arguments = ["--target-root", str(self.target), "--source-revision", self.revision,
                     "--check", "--allocation-plan"]
        with (patch.object(self.adopter, "verify_publication_evidence", side_effect=SystemExit("unpublished")),
              self.assertRaises(SystemExit)):
            self.adopter.main(arguments)
        arguments[1] = str(self.target / ".." / self.target.name)
        with self.assertRaises(SystemExit):
            self.adopter.main(arguments)

    def test_unborn_scaffold_does_not_borrow_ancestor_git_identity(self):
        scaffold = self.case / "unborn-scaffold"
        scaffold.mkdir()
        self.assertEqual(self.adopter.ignored_payload_targets(scaffold, {"README.md"}), [])
        with self.assertRaises((SystemExit, subprocess.CalledProcessError)):
            self.adopter.allocation_target_state(scaffold, {"README.md"})

    def test_symlinked_target_and_plan_are_rejected(self):
        self.export()
        path = self.target / ".governance/standard-adoption-plan.schema.json"
        path.unlink(missing_ok=True)
        path.symlink_to(self.target / "README.md")
        with self.assertRaisesRegex(SystemExit, "symlink"):
            self.verify()
        path.unlink()
        link = self.case / "plan-link.json"
        link.symlink_to(self.plan_path)
        with self.assertRaises(SystemExit):
            self.adopter.verify_allocation_plan(link, self.target, "governance")

    def test_duplicate_fields_oversized_and_unpublished_mode_refuse(self):
        self.plan_path.write_text('{"source":{},"source":{}}')
        with self.assertRaises(SystemExit):
            self.verify()
        self.plan_path.write_text(" " * (self.adopter.MAX_RELEASE_METADATA_BYTES + 1))
        with self.assertRaises(SystemExit):
            self.verify()
        with self.assertRaises(SystemExit):
            self.adopter.main(["--target-root", str(self.target), "--source-revision", self.revision,
                               "--check", "--allocation-plan", "--allow-unpublished-for-testing"])

    def test_changed_adoption_pin_is_rejected(self):
        self.export()
        path = self.target / ".governance/manifest.lock.json"
        lock = json.loads(path.read_text())
        lock["standard"]["sourceRevision"] = "f" * 40
        path.write_text(json.dumps(lock))
        with self.assertRaises(SystemExit):
            self.verify()

    def test_changed_source_exporter_and_allocator_refuse(self):
        self.export()
        for name in ("scripts/create_adoption_lock.py", "project/new-ticket.sh"):
            path = self.source / name
            raw = path.read_bytes()
            try:
                path.write_bytes(raw + b"\n# changed fixture bytes\n")
                with self.assertRaises(SystemExit):
                    self.verify()
            finally:
                path.write_bytes(raw)

    def test_existing_foreign_managed_target_requires_explicit_takeover(self):
        path = self.target / ".github/workflows/new-project-branch-hygiene.yml"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("name: Foreign owner\n")
        self.command(self.target, "git", "add", ".")
        self.command(self.target, "git", "commit", "--quiet", "-m", "Foreign workflow")
        with self.assertRaises(SystemExit):
            self.export()

    def test_seed_owner_is_not_transferred(self):
        path = self.target / ".governance/manifest.json"
        manifest = json.loads(path.read_text())
        manifest["coordination"]["workstreams"]["infrastructure"]["ownedPaths"].append(".gitattributes")
        path.write_text(json.dumps(manifest))
        self.command(self.target, "git", "add", ".")
        self.command(self.target, "git", "commit", "--quiet", "-m", "Local seed owner")
        with self.assertRaises(SystemExit):
            self.export()

    def test_installer_matches_exported_projection_preserving_local_owners(self):
        plan = self.export()
        before = json.loads((self.target / ".governance/manifest.json").read_text())
        with patch.object(self.adopter, "verify_publication_evidence"), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(self.adopter.main(["--target-root", str(self.target),
                "--source-revision", self.revision, "--upgrade"]), 0)
        for item in plan["files"]:
            self.assertEqual(hashlib.sha256((self.target / item["path"]).read_bytes()).hexdigest(), item["sha256"], item["path"])
        after = json.loads((self.target / ".governance/manifest.json").read_text())
        self.assertEqual(after, plan["prospectiveManifest"])
        self.assertEqual(before["coordination"]["workstreams"]["infrastructure"],
                         after["coordination"]["workstreams"]["infrastructure"])


if __name__ == "__main__":
    unittest.main()
