"""The managed pre-push hook refuses direct pushes to the declared target branch (GOV-PUSH-001)."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from change_lease_safety_test import lease

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "template/files/pre-push.template.sh"


def git(cwd: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    env = {**{k: v for k, v in os.environ.items() if not k.startswith("GIT_")}, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.test",
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

    def install_writer(self, branch="ticket/001-example"):
        self.primary = self.repo
        self.writer_env = patch.dict(os.environ, {
            "NEW_PROJECT_WRITER_ACTOR": "agent:fixture",
            "NEW_PROJECT_WRITER_SESSION": "session-fixture",
            "NEW_PROJECT_LEASE_REVISION": "1", "NEW_PROJECT_FENCING_TOKEN": "1"})
        self.writer_env.start()
        self.addCleanup(self.writer_env.stop)
        self.repo = self.primary / ".worktrees/ticket-001--example"
        git(self.primary, "worktree", "add", "-q", "-b", branch, str(self.repo))
        for base in (self.primary, self.repo):
            managed = base / ".governance"
            managed.mkdir(exist_ok=True)
            shutil.copy2(ROOT / "scripts/change_lease_check.py", managed / "change_lease_check.py")
            shutil.copy2(ROOT / "subprojects/change-lease/change-lease.schema.json", managed / "change-lease.schema.json")
        (self.repo / ".githooks").mkdir(exist_ok=True)
        shutil.copy2(HOOK, self.repo / ".githooks/pre-push")
        (self.repo / ".githooks/pre-push").chmod(0o755)
        self.lease_path = self.primary / ".subactor/leases/ticket-001--example.json"
        self.lease_path.parent.mkdir(parents=True)
        self.writer_lease = lease()
        self.writer_lease.update(branchRef="refs/heads/" + branch, worktreeId="ticket-001--example",
            repositoryRef="local/" + hashlib.sha256(str(self.primary.resolve()).encode()).hexdigest())
        self.save_lease()

    def save_lease(self):
        self.lease_path.write_text(json.dumps(self.writer_lease))

    def test_other_session_push_and_force_push_leave_remote_unchanged(self):
        self.install_writer()
        for source in (HOOK, ROOT / ".githooks/pre-push"):
            for base in (self.repo, self.primary):
                shutil.copy2(source, base / ".githooks/pre-push")
                (base / ".githooks/pre-push").chmod(0o755)
            git(self.repo, "push", "origin", "ticket/001-example")
            before = git(self.remote, "rev-parse", "refs/heads/ticket/001-example").stdout
            (self.repo / "README.md").write_text(before)
            git(self.repo, "add", "README.md")
            git(self.repo, "commit", "--allow-empty", "-m", "another change")
            with patch.dict(os.environ, {"NEW_PROJECT_WRITER_SESSION": "second-session"}):
                for base in (self.repo, self.primary):
                    for force in ([], ["--force"]):
                        result = git(base, "push", *force, "origin", "ticket/001-example", check=False)
                        self.assertNotEqual(result.returncode, 0)
                        self.assertIn("GOV-CHANGE-LEASE-002", result.stdout + result.stderr)
                        self.assertEqual(git(self.remote, "rev-parse", "refs/heads/ticket/001-example").stdout, before)
            git(self.primary, "push", "--force", "origin", "ticket/001-example")

    def test_forced_rewrite_and_delete_require_the_writer(self):
        self.install_writer()
        git(self.repo, "push", "origin", "ticket/001-example")
        before = git(self.remote, "rev-parse", "refs/heads/ticket/001-example").stdout
        (self.repo / "README.md").write_text("rewritten history")
        git(self.repo, "add", "README.md")
        git(self.repo, "commit", "--amend", "-m", "rewritten seed")
        for source in (HOOK, ROOT / ".githooks/pre-push"):
            shutil.copy2(source, self.repo / ".githooks/pre-push")
            with patch.dict(os.environ, {"NEW_PROJECT_WRITER_SESSION": "second-session"}):
                for args in (("--force", "origin", "ticket/001-example"),
                             ("origin", ":ticket/001-example")):
                    result = git(self.repo, "push", *args, check=False)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("GOV-CHANGE-LEASE-002", result.stdout + result.stderr)
                    self.assertEqual(git(self.remote, "rev-parse", "refs/heads/ticket/001-example").stdout, before)
        git(self.repo, "push", "--force", "origin", "ticket/001-example")
        self.assertEqual(git(self.remote, "rev-parse", "refs/heads/ticket/001-example").stdout,
                         git(self.repo, "rev-parse", "HEAD").stdout)

    def test_all_refs_and_profile_exceptions_are_fenced(self):
        self.install_writer()
        for name in ("local-audit", "main-only-files", "main-only-planfile"):
            self.profile(name)
            with patch.dict(os.environ, {"NEW_PROJECT_WRITER_SESSION": "another-session"}):
                result = git(self.repo, "push", "origin", "main", "ticket/001-example", check=False)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("GOV-CHANGE-LEASE-002", result.stdout + result.stderr)
                self.assertEqual(git(self.remote, "show-ref", check=False).stdout, "")
        result = git(self.primary, "push", "origin", "main:ticket/002-unowned", check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("GOV-CHANGE-LEASE-001", result.stdout + result.stderr)

    def test_both_commit_hooks_fence_amends(self):
        self.install_writer()
        ticket = self.repo / "project/ticket-001"
        ticket.mkdir(parents=True)
        (ticket / "README.md").write_text("- **Status**: IN_PROGRESS\n")
        (self.repo / ".governance/worktree_guard.py").write_text("raise SystemExit(0)\n")
        for source in (ROOT / ".githooks/pre-commit", ROOT / "template/files/pre-commit.template.sh"):
            shutil.copy2(source, self.repo / ".githooks/pre-commit")
            (self.repo / ".githooks/pre-commit").chmod(0o755)
            (self.repo / "README.md").write_text(str(source))
            git(self.repo, "add", "README.md", "project/ticket-001/README.md")
            git(self.repo, "commit", "-m", "ticket-001 owner")
            (self.repo / "README.md").write_text(str(source) + " amend")
            git(self.repo, "add", "README.md")
            before = git(self.repo, "rev-parse", "HEAD").stdout
            with patch.dict(os.environ, {"NEW_PROJECT_WRITER_SESSION": "other-session"}):
                for args in (("commit", "-m", "ticket-001 other"), ("commit", "--amend", "--no-edit")):
                    result = git(self.repo, *args, check=False)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("GOV-CHANGE-LEASE-002", result.stdout + result.stderr)
                    self.assertEqual(git(self.repo, "rev-parse", "HEAD").stdout, before)
            git(self.repo, "commit", "--amend", "--no-edit")

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
        self.install_writer()

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
