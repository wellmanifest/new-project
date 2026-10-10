#!/usr/bin/env python3

from __future__ import annotations

import hashlib
import json
import pathlib
import subprocess
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
LOCK_PATH = ROOT / "governance" / "session-recovery.lock.json"
STANDARD_PACKS_PATH = ROOT / "governance" / "standard-packs.json"


def sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class SessionRecoveryAdoptionTest(unittest.TestCase):
    def test_session_recovery_lock_binds_published_artifacts(self):
        self.assertTrue(LOCK_PATH.is_file(), f"missing {LOCK_PATH}")
        lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
        self.assertEqual(lock["schema"], "new-project.session-recovery-lock/v1")
        self.assertEqual(lock["dependency"]["id"], "wellmanifest/session-recovery")
        self.assertEqual(lock["dependency"]["version"], "0.1.0")

        for artifact in lock["artifacts"]:
            path = ROOT / artifact["packageSourcePath"]
            self.assertTrue(path.is_file(), f"missing artifact: {path}")
            expected = artifact["sourceSha256"]
            self.assertEqual(
                sha256(path),
                expected,
                f"digest mismatch for {artifact['packageSourcePath']}",
            )

    def test_standard_packs_declares_session_recovery(self):
        self.assertTrue(STANDARD_PACKS_PATH.is_file(), f"missing {STANDARD_PACKS_PATH}")
        packs_data = json.loads(STANDARD_PACKS_PATH.read_text(encoding="utf-8"))
        pack_ids = {p["id"] for p in packs_data["packs"]}
        self.assertIn("wellmanifest/session-recovery", pack_ids)

        agent_reqs = {r["id"] for r in packs_data["profiles"]["agent-executor"]["requirements"]}
        self.assertIn("wellmanifest/session-recovery", agent_reqs)

    def test_conformance_script_runs(self):
        conformance_script = ROOT / "subprojects" / "session-recovery" / "conformance.py"
        self.assertTrue(conformance_script.is_file())
        result = subprocess.run(
            [sys.executable, str(conformance_script), "--help"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("LLM Session Recovery Conformance Utility", result.stdout)


if __name__ == "__main__":
    unittest.main()
