#!/usr/bin/env python3
"""Exercise the actual Git message boundary and managed hook installation."""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class CommitMessageHookTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name) / "repo"
        self.repo.mkdir()
        self.git("init", "-q", "-b", "ticket/123-repair")
        self.git("config", "user.name", "Hook Test")
        self.git("config", "user.email", "hook-test@example.invalid")
        hooks = self.repo / ".githooks"
        hooks.mkdir()
        shutil.copy2(ROOT / "template/files/commit-msg.template.sh", hooks / "commit-msg")
        self.git("config", "core.hooksPath", ".githooks")
        (self.repo / "material.txt").write_text("material\n")
        self.git("add", "material.txt")

    def git(self, *args, check=True):
        return subprocess.run(["git", *args], cwd=self.repo, capture_output=True,
                              text=True, check=check)

    def test_rejected_subjects_never_create_a_commit(self):
        for message in ("fix: repair", "fix: ticket-124", "fix: ticket-1234",
                        "fix: xticket-123", "fix: ticket-123-extra",
                        "fix: repair\n\nticket-123"):
            with self.subTest(message=message):
                result = self.git("commit", "-m", message, check=False)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("GOV-AGENT-HOST-001", result.stderr)
                self.assertNotEqual(self.git("rev-parse", "--verify", "HEAD",
                                             check=False).returncode, 0)

    def test_matching_subject_creates_commit(self):
        self.git("commit", "-qm", "fix(component,ticket-123): repair")
        self.assertEqual(self.git("rev-list", "--count", "HEAD").stdout.strip(), "1")

    def test_detached_head_is_rejected(self):
        self.git("commit", "-qm", "fix: repair (ticket-123)")
        self.git("checkout", "--detach", "-q")
        before = self.git("rev-parse", "HEAD").stdout
        result = self.git("commit", "--allow-empty", "-m", "fix: ticket-123", check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(before, self.git("rev-parse", "HEAD").stdout)

    def test_repository_profiles_preserve_existing_policy(self):
        policy = self.repo / ".governance/repository_policy.py"
        policy.parent.mkdir()
        self.git("checkout", "-qb", "main")
        for profile in ("local-audit", "main-only-planfile", "main-only-files"):
            with self.subTest(profile=profile):
                policy.write_text(f"print({profile!r})\n")
                self.git("commit", "--allow-empty", "-qm", "existing policy message")

    def test_installer_and_checker_require_executable_message_hook(self):
        installer = ["bash", str(ROOT / "scripts/install-agent-hosts.sh"),
                     "--source", str(ROOT), "--target", str(self.repo)]
        subprocess.run(installer, check=True, capture_output=True)
        hook = self.repo / ".githooks/commit-msg"
        self.assertTrue(hook.stat().st_mode & 0o111)
        subprocess.run(installer + ["--check"], check=True, capture_output=True)
        spec = importlib.util.spec_from_file_location("host_check", ROOT / "scripts/agent_host_check.py")
        module = importlib.util.module_from_spec(spec)
        import sys
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        contract = json.loads((self.repo / ".governance/agent-hosts.json").read_text())
        self.assertFalse(module.check_hook(self.repo, contract, "agent"))
        hook.chmod(0o644)
        failed = subprocess.run(installer + ["--check"], capture_output=True, text=True)
        self.assertNotEqual(failed.returncode, 0)
        self.assertIn("GOV-AGENT-HOST-005", failed.stderr)
        self.assertTrue(module.check_hook(self.repo, contract, "ci"))
        hook.unlink()
        self.assertTrue(module.check_hook(self.repo, contract, "ci"))

    def test_invalid_additional_hook_refused_without_effect(self):
        installer = ["bash", str(ROOT / "scripts/install-agent-hosts.sh"),
                     "--source", str(ROOT), "--target", str(self.repo)]
        subprocess.run(installer, check=True, capture_output=True)
        path = self.repo / ".governance/agent-hosts.json"
        contract = json.loads(path.read_text())
        for invalid in (["../outside"], ".githooks/commit-msg", [None],
                        [".githooks/commit-msg", ".githooks/commit-msg"]):
            with self.subTest(invalid=invalid):
                contract["hook"]["additionalHooks"] = invalid
                path.write_text(json.dumps(contract))
                hook = self.repo / ".githooks/commit-msg"
                hook.chmod(0o644)
                result = subprocess.run(["bash", str(ROOT / "scripts/install-agent-hosts.sh"),
                                         "--source", str(self.repo)],
                                        cwd=self.repo, capture_output=True, text=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(hook.stat().st_mode & 0o111)


if __name__ == "__main__":
    unittest.main()
