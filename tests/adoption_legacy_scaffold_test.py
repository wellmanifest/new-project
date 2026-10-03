"""Actual CLI regressions for explicit migration of minimal Wellman scaffolds."""
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/create_adoption_lock.py"
LEGACY = {
    "schema": "wellmanifest.manifest/v1",
    "standard": {"id": "profile:baseline", "version": "0.20.37"},
}


class LegacyScaffoldMigrationTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.target = self.root / "target"
        self.target.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=self.target, check=True)
        subprocess.run(["git", "remote", "add", "origin", "https://github.com/fixture/target.git"],
                       cwd=self.target, check=True)
        for name in ("README.md", "VERSION", "CHANGELOG.md", "TODO.md", "project/TICKETS.md"):
            path = self.target / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("target-owned prerequisite\n")
        self.manifest = self.target / ".governance/manifest.json"
        self.manifest.parent.mkdir()
        self.manifest.write_text(json.dumps(LEGACY, indent=4) + "\n")
        self.revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()

    def contents(self):
        return {str(p.relative_to(self.target)): p.read_bytes()
                for p in self.target.rglob("*") if p.is_file() and ".git" not in p.relative_to(self.target).parts}

    def run_adopter(self, *arguments):
        return subprocess.run([sys.executable, str(SCRIPT), "--target-root", str(self.target),
                               "--source-revision", self.revision, "--allow-unpublished-for-testing",
                               *arguments], capture_output=True, text=True, timeout=60)

    def test_default_upgrade_still_refuses_incomplete_manifest(self):
        before = self.contents()
        result = self.run_adopter("--upgrade")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("does not extend", result.stderr)
        self.assertEqual(self.contents(), before)

    def test_explicit_review_then_apply_installs_pinned_native_adoption(self):
        before = self.contents()
        review = self.run_adopter("--check", "--migrate-wellman-scaffold")
        self.assertEqual(review.returncode, 1, review.stderr)
        self.assertIn("UPDATE .governance/manifest.json", review.stdout)
        self.assertEqual(self.contents(), before)
        result = self.run_adopter("--upgrade", "--migrate-wellman-scaffold")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        manifest = json.loads(self.manifest.read_text())
        lock = json.loads((self.manifest.parent / "manifest.lock.json").read_text())
        self.assertEqual(manifest["schema"], "new-project.governance/v2")
        self.assertIn("approvalEvidence", manifest)
        self.assertEqual(lock["standard"]["sourceRevision"], self.revision)
        self.assertEqual(lock["standard"]["publicationStatus"], "unpublished-test")
        self.assertTrue((self.target / "project/new-ticket.sh").is_file())
        for name in ("README.md", "VERSION", "CHANGELOG.md", "TODO.md", "project/TICKETS.md"):
            self.assertEqual((self.target / name).read_bytes(), before[name])

    def test_custom_and_native_manifests_cannot_use_migration(self):
        cases = [[], {**LEGACY, "coordination": {"policy": "keep"}},
                 {**LEGACY, "schema": "new-project.governance/v2"},
                 {**LEGACY, "standard": {"id": "wellmanifest/new-project", "version": "0.20.80"}},
                 {**LEGACY, "standard": {**LEGACY["standard"], "sourceRevision": "a" * 40}},
                 {**LEGACY, "standard": {**LEGACY["standard"], "version": 37}},
                 {**LEGACY, "standard": {**LEGACY["standard"], "version": ""}}]
        for document in cases:
            with self.subTest(document=document):
                self.manifest.write_text(json.dumps(document) + "\n")
                before = self.contents()
                result = self.run_adopter("--upgrade", "--migrate-wellman-scaffold")
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("minimal Wellman baseline", result.stderr)
                self.assertEqual(self.contents(), before)

    def test_native_adoption_evidence_prevents_migration(self):
        for name in ("manifest.lock.json", "manifest.base.json", "package-manifest.json"):
            with self.subTest(name=name):
                path = self.manifest.parent / name
                path.write_text("{}\n")
                before = self.contents()
                result = self.run_adopter("--upgrade", "--migrate-wellman-scaffold")
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("native adoption evidence", result.stderr)
                self.assertEqual(self.contents(), before)
                path.unlink()

    def test_missing_prerequisite_preserves_all_files(self):
        (self.target / "README.md").unlink()
        before = self.contents()
        result = self.run_adopter("--upgrade", "--migrate-wellman-scaffold")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("MISSING target prerequisite README.md", result.stdout)
        self.assertEqual(self.contents(), before)

    def test_migration_needs_explicit_review_or_upgrade(self):
        before = self.contents()
        result = self.run_adopter("--migrate-wellman-scaffold")
        self.assertEqual(result.returncode, 2)
        self.assertIn("--check or --upgrade", result.stderr)
        self.assertEqual(self.contents(), before)

    def test_migration_keeps_publication_verification(self):
        spec = importlib.util.spec_from_file_location("legacy_adoption", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        before = self.contents()
        args = [str(SCRIPT), "--target-root", str(self.target), "--source-revision", self.revision,
                "--upgrade", "--migrate-wellman-scaffold"]
        with patch.object(sys, "argv", args), patch.object(
            module, "verify_publication_evidence", side_effect=SystemExit("publication-fixture-refusal")
        ) as verifier:
            with self.assertRaisesRegex(SystemExit, "publication-fixture-refusal"):
                module.main()
            verifier.assert_called_once()
        self.assertEqual(self.contents(), before)

    def test_duplicate_keys_cannot_hide_native_policy(self):
        self.manifest.write_text('{"schema":"new-project.governance/v2","schema":"wellmanifest.manifest/v1",'
                                 '"standard":{"id":"profile:baseline","version":"0.20.37"}}')
        before = self.contents()
        result = self.run_adopter("--upgrade", "--migrate-wellman-scaffold")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("minimal Wellman baseline", result.stderr)
        self.assertEqual(self.contents(), before)

    @unittest.skipIf(sys.platform == "win32", "symlink creation needs host privileges on Windows")
    def test_symlinked_targets_are_preserved(self):
        outside = self.root / "outside"
        outside.mkdir()
        sentinel = outside / "sentinel.txt"
        sentinel.write_text("outside target\n")
        (self.target / ".github").symlink_to(outside, target_is_directory=True)
        before = self.contents()
        result = self.run_adopter("--upgrade", "--migrate-wellman-scaffold")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("symlinked target", result.stderr)
        self.assertEqual(self.contents(), before)
        self.assertEqual(list(outside.iterdir()), [sentinel])


if __name__ == "__main__":
    unittest.main()
