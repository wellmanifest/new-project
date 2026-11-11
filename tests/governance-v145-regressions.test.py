"""Regressions for v0.20.145 governance hardening (ticket-426)."""
from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


def _load_module(name: str, relative: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class GovernanceV145RegressionsTest(unittest.TestCase):
    def test_resolved_checks_text_handles_quoted_uses_keys(self):
        ref = "wellmanifest/new-project/.github/workflows/reusable.yml@" + ("a" * 40)
        callee = (
            "name: Reusable\n"
            "on: workflow_call\n"
            "jobs:\n"
            "  verify:\n"
            "    name: enforce\n"
            "    runs-on: ubuntu-latest\n"
            "    steps:\n"
            "      - run: echo ok\n"
        )
        for index, relative in enumerate(
            (
                "scripts/generate_required_checks.py",
                "packages/wellman/src/wellman/_bundled/generate_required_checks.py",
            )
        ):
            module = _load_module(f"gen_checks_{index}", relative)
            for key_spelling in ("uses:", "'uses':", '"uses":'):
                caller = (
                    "name: Governance\n"
                    "on: pull_request\n"
                    "jobs:\n"
                    "  gate:\n"
                    "    name: governance\n"
                    f"    {key_spelling} {ref}\n"
                )
                callers: list[str] = []
                if key_spelling == "uses:":
                    resolved = module.resolved_checks_text(caller, {ref: callee}, callers)
                    self.assertEqual(resolved, ["governance / enforce"], (relative, key_spelling))
                    self.assertEqual(callers, [], (relative, key_spelling))
                else:
                    # End-to-end literal_jobs refuses quoted job keys with SystemExit,
                    # and REUSABLE_CALL capture extraction never raises IndexError even if literal_jobs yields body.
                    with self.assertRaises(SystemExit):
                        module.resolved_checks_text(caller, {ref: callee}, callers)
                    job_body = f"    name: governance\n    {key_spelling} {ref}"
                    original_literal_jobs = module.literal_jobs

                    def fake_literal_jobs(doc: str, _orig=original_literal_jobs, _body=job_body, _caller=caller):
                        if doc == _caller:
                            return [("gate", _body)]
                        return _orig(doc)

                    with patch.object(module, "literal_jobs", side_effect=fake_literal_jobs):
                        resolved = module.resolved_checks_text(caller, {ref: callee}, callers)
                    self.assertEqual(resolved, ["governance / enforce"], (relative, key_spelling))

    def test_scoped_paths_rejects_parent_traversal_and_noncanonical_components(self):
        import ticket_storage

        for bad_scope in (
            ["scripts/../outside.py"],
            ["../outside.py"],
            ["./scripts/work_start_check.py"],
            ["scripts//work_start_check.py"],
            ["/abs/path.py"],
        ):
            with self.subTest(bad_scope=bad_scope):
                with self.assertRaises(ValueError):
                    ticket_storage.scoped_paths(ROOT, "governance", bad_scope)

    def test_publication_observation_catches_subprocess_error_without_leaking(self):
        import work_start_check

        entries = [
            {
                "path": str(ROOT),
                "branch": "refs/heads/main",
                "headSha": "b" * 40,
                "allDirtyPaths": [],
            }
        ]
        secret_err = subprocess.CalledProcessError(
            128,
            ["git", "ls-remote"],
            stderr="https://user:super-secret-token@example.invalid/repo.git",
        )
        with tempfile.TemporaryDirectory() as td:
            with patch.object(work_start_check, "remote_heads", side_effect=secret_err):
                obs = work_start_check.publication_observation(Path(td), entries, "main")
        self.assertEqual(obs["status"], "unavailable")
        self.assertIsNone(obs["remoteRefsDigest"])
        self.assertNotIn("super-secret-token", str(obs))
        self.assertEqual(obs["worktrees"][0]["nextAction"], "observe-remote")


if __name__ == "__main__":
    unittest.main()
