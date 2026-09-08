#!/usr/bin/env python3
"""Run the managed hook with a real staged pin and a forbidden updater."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class LocalPinTest(unittest.TestCase):
    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.repo), *args], check=True,
                              text=True, capture_output=True)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        self.git("init", "-b", "ticket/001-test")
        for directory in (".governance", ".subactor", "project/ticket-001"):
            (self.repo / directory).mkdir(parents=True)
        managed = {}
        for name in (".subactor/manifest.json", ".subactor/.gitignore"):
            shutil.copyfile(ROOT / name, self.repo / name)
            managed[name] = hashlib.sha256((self.repo / name).read_bytes()).hexdigest()
        lock = {"standard": {"id": "wellmanifest/new-project",
                             "version": "0.20.11", "sourceRepository": "wellmanifest/new-project",
                             "sourceRevision": "a" * 40, "publicationStatus": "published"},
                "managedFiles": managed}
        # Use the declared identifier, not a second hardcoded policy identity.
        manifest = json.loads((self.repo / ".subactor/manifest.json").read_text())
        lock["standard"]["id"] = manifest["standardPin"]["requiredStandardId"]
        (self.repo / ".governance/manifest.lock.json").write_text(json.dumps(lock))
        shutil.copyfile(ROOT / "scripts/work_continuity.py", self.repo / ".governance/work_continuity.py")
        (self.repo / ".governance/precommit_standard_update.py").write_text(
            "from pathlib import Path\nPath('updater-called').touch()\nraise SystemExit(91)\n")
        (self.repo / ".governance/standard-adoption.json").write_text("{}")
        (self.repo / ".governance/worktree_guard.py").write_text(
            "from pathlib import Path\nPath('guard-called').touch()\n")
        (self.repo / "project/ticket-001/README.md").write_text("- **Status**: IN_PROGRESS\n")
        (self.repo / "app.py").write_text("print('material change')\n")
        self.git("add", "--force", ".")

    def hook(self):
        return subprocess.run(["bash", str(ROOT / "template/files/pre-commit.template.sh")],
                              cwd=self.repo, capture_output=True, text=True)

    def test_valid_staged_pin_does_not_run_updater(self):
        result = self.hook()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.repo / "updater-called").exists())
        self.assertTrue((self.repo / "guard-called").exists())

    def test_mutated_managed_pin_is_blocked(self):
        with (self.repo / ".subactor/manifest.json").open("a") as stream:
            stream.write("\n")
        self.git("add", ".subactor/manifest.json")
        result = self.hook()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("GOV-CONTINUITY-001", result.stderr)
        self.assertFalse((self.repo / "guard-called").exists())
        self.assertFalse((self.repo / "updater-called").exists())

    def test_missing_pin_pair_is_blocked(self):
        self.git("rm", "--cached", ".governance/manifest.lock.json")
        result = self.hook()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("GOV-CONTINUITY-001", result.stderr)


if __name__ == "__main__":
    unittest.main()
