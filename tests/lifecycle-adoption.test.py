#!/usr/bin/env python3

from __future__ import annotations

import hashlib
import json
import pathlib
import subprocess
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
GIT_LOCK_PATH = ROOT / "governance" / "git-lifecycle.lock.json"
TICKET_LOCK_PATH = ROOT / "governance" / "ticket-lifecycle.lock.json"
SSOT_PATH = ROOT / "governance" / "lifecycle-vendored-copy.ssot.json"

GIT_SOURCE_REVISION = "24cfe7cbbbc0d95f6b66f89124b471bee7287d0d"
TICKET_SOURCE_REVISION = "ad363efa7705919ff613305172bf8115ccf50b15"


def sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class LifecycleAdoptionTest(unittest.TestCase):
    def test_git_lifecycle_lock_binds_published_artifacts(self):
        self.assertTrue(GIT_LOCK_PATH.is_file(), f"missing {GIT_LOCK_PATH}")
        lock = json.loads(GIT_LOCK_PATH.read_text(encoding="utf-8"))
        self.assertEqual(lock["schema"], "new-project.git-lifecycle-lock/v1")
        self.assertEqual(lock["dependency"]["id"], "wellmanifest/git-lifecycle")
        self.assertEqual(lock["dependency"]["version"], "0.2.0-dev")
        self.assertEqual(lock["dependency"]["sourceRevision"], GIT_SOURCE_REVISION)

        for artifact in lock["artifacts"]:
            path = ROOT / artifact["packageSourcePath"]
            self.assertTrue(path.is_file(), f"missing artifact: {path}")
            expected = artifact["sourceSha256"]
            self.assertEqual(
                sha256(path),
                expected,
                f"digest mismatch for {artifact['packageSourcePath']}",
            )

    def test_ticket_lifecycle_lock_binds_published_artifacts(self):
        self.assertTrue(TICKET_LOCK_PATH.is_file(), f"missing {TICKET_LOCK_PATH}")
        lock = json.loads(TICKET_LOCK_PATH.read_text(encoding="utf-8"))
        self.assertEqual(lock["schema"], "new-project.ticket-lifecycle-lock/v1")
        self.assertEqual(lock["dependency"]["id"], "wellmanifest/ticket-lifecycle")
        self.assertEqual(lock["dependency"]["version"], "0.2.0-dev")
        self.assertEqual(lock["dependency"]["sourceRevision"], TICKET_SOURCE_REVISION)

        for artifact in lock["artifacts"]:
            path = ROOT / artifact["packageSourcePath"]
            self.assertTrue(path.is_file(), f"missing artifact: {path}")
            expected = artifact["sourceSha256"]
            self.assertEqual(
                sha256(path),
                expected,
                f"digest mismatch for {artifact['packageSourcePath']}",
            )

    def test_git_lifecycle_dsl_validation_passes(self):
        lifecycle_validator = ROOT / "subprojects" / "git-lifecycle" / "lifecycle.py"
        lifecycle_spec = ROOT / "subprojects" / "git-lifecycle" / "git-lifecycle.lifecycle"
        self.assertTrue(lifecycle_validator.is_file())
        self.assertTrue(lifecycle_spec.is_file())
        result = subprocess.run(
            [sys.executable, str(lifecycle_validator), "validate", str(lifecycle_spec)],
            capture_output=True,
            text=True,
            cwd=str(lifecycle_validator.parent),
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("VALID git-repository", result.stdout)

    def test_ticket_lifecycle_dsl_validation_passes(self):
        lifecycle_validator = ROOT / "subprojects" / "ticket-lifecycle" / "lifecycle.py"
        lifecycle_spec = ROOT / "subprojects" / "ticket-lifecycle" / "ticket-lifecycle.lifecycle"
        self.assertTrue(lifecycle_validator.is_file())
        self.assertTrue(lifecycle_spec.is_file())
        result = subprocess.run(
            [sys.executable, str(lifecycle_validator), "validate", str(lifecycle_spec)],
            capture_output=True,
            text=True,
            cwd=str(lifecycle_validator.parent),
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("VALID governed-ticket", result.stdout)

    def test_checkpoint_action_projected_in_git_lifecycle_and_ticket_lifecycle(self):
        git_schema = json.loads(
            (ROOT / "subprojects" / "git-lifecycle" / "git-lifecycle.schema.json").read_text(encoding="utf-8")
        )
        actions = git_schema["$defs"]["action"]["enum"]
        self.assertIn("checkpoint", actions)

        git_readme = (ROOT / "subprojects" / "git-lifecycle" / "README.md").read_text(encoding="utf-8")
        self.assertIn("checkpoint", git_readme)
        self.assertIn("wellmanifest/git-lifecycle", git_readme)

        ticket_readme = (ROOT / "subprojects" / "ticket-lifecycle" / "README.md").read_text(encoding="utf-8")
        self.assertIn("checkpoint", ticket_readme)
        self.assertIn("wellmanifest/ticket-lifecycle", ticket_readme)

    def test_ssot_decision_record_is_valid(self):
        self.assertTrue(SSOT_PATH.is_file(), f"missing {SSOT_PATH}")
        data = json.loads(SSOT_PATH.read_text(encoding="utf-8"))
        self.assertEqual(data["schema"], "wellmanifest.ssot/decision/v1")
        self.assertEqual(data["id"], "lifecycle-vendored-copy")
        decision_ids = {d["id"] for d in data["decisions"]}
        self.assertIn("git-lifecycle-vendored-copy", decision_ids)
        self.assertIn("ticket-lifecycle-vendored-copy", decision_ids)
        for d in data["decisions"]:
            self.assertEqual(d["kind"], "vendored_copy")
            self.assertEqual(d["gate"]["kind"], "parity_test")


if __name__ == "__main__":
    unittest.main()
