"""The managed pre-push hook refuses direct pushes to the declared target branch (GOV-PUSH-001)."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "template/files/pre-push.template.sh"


def git(cwd: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.test",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.test"}
    return subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True, check=check, env=env)


class PrePushHookTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="pre-push-"))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.remote = self.tmp / "remote.git"
        git(self.tmp, "init", "-q", "--bare", "-b", "main", str(self.remote))
        self.repo = self.tmp / "repo"
        git(self.tmp, "init", "-q", "-b", "main", str(self.repo))
        hooks = self.repo / ".githooks"
        hooks.mkdir()
        shutil.copy2(HOOK, hooks / "pre-push")
        (hooks / "pre-push").chmod(0o755)
        git(self.repo, "config", "core.hooksPath", ".githooks")
        git(self.repo, "remote", "add", "origin", str(self.remote))
        (self.repo / "README.md").write_text("x\n")
        git(self.repo, "add", "README.md")
        git(self.repo, "commit", "-q", "-m", "init")

    def manifest(self, branches: list[str]) -> None:
        (self.repo / ".governance").mkdir(exist_ok=True)
        (self.repo / ".governance/manifest.json").write_text(
            json.dumps({"schema": "new-project.governance/v2", "delivery": {"targetBranches": branches}}))

    def profile(self, name: str) -> None:
        (self.repo / ".governance").mkdir(exist_ok=True)
        (self.repo / ".governance/repository_policy.py").write_text(
            "import sys\nif '--profile' in sys.argv:\n    print(%r)\n" % name)

    def test_direct_push_to_main_is_refused(self) -> None:
        result = git(self.repo, "push", "origin", "main", check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("GOV-PUSH-001", result.stderr)
        self.assertEqual(git(self.remote, "branch", "--list", "main").stdout.strip(), "")

    def test_ticket_branch_push_is_allowed(self) -> None:
        git(self.repo, "switch", "-q", "-c", "ticket/001-example")
        result = git(self.repo, "push", "origin", "ticket/001-example", check=False)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_refspec_onto_main_from_another_branch_is_refused(self) -> None:
        git(self.repo, "switch", "-q", "-c", "ticket/002-example")
        result = git(self.repo, "push", "origin", "HEAD:main", check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("GOV-PUSH-001", result.stderr)

    def test_declared_target_branch_is_used(self) -> None:
        self.manifest(["master"])
        git(self.repo, "add", ".governance")
        git(self.repo, "commit", "-q", "-m", "manifest")
        self.assertEqual(git(self.repo, "push", "origin", "main", check=False).returncode, 0)
        result = git(self.repo, "push", "origin", "main:master", check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("'master'", result.stderr)

    def test_main_only_profiles_push_to_main_by_design(self) -> None:
        for name in ("main-only-planfile", "main-only-files", "local-audit"):
            with self.subTest(profile=name):
                self.profile(name)
                result = git(self.repo, "push", "--force", "origin", "main", check=False)
                self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
