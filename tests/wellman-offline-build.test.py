#!/usr/bin/env python3
"""Actual missing-build-tools refusal in a clean offline Python environment."""

import os
from pathlib import Path
import subprocess
import tempfile
import unittest
import venv


ROOT = Path(__file__).resolve().parents[1]


class OfflineBuildPrerequisitesTests(unittest.TestCase):
    def test_clean_venv_fails_before_wheel_build_or_index_lookup(self):
        with tempfile.TemporaryDirectory(prefix="wellman-missing-build-tools-") as directory:
            root = Path(directory)
            runtime = root / "venv"
            # No pip or build tools: this is a real environment, not a mocked
            # installer that merely reports the command we expected to run.
            venv.EnvBuilder(with_pip=False).create(runtime)
            environment = os.environ.copy()
            environment.update(
                PATH=str(runtime / "bin") + os.pathsep + os.environ.get("PATH", ""),
                PIP_NO_INDEX="1",
                PIP_DISABLE_PIP_VERSION_CHECK="1",
                PYTHONPATH="",
            )
            result = subprocess.run(
                ["bash", str(ROOT / "tests/wellman-package.test.sh")],
                cwd=ROOT, env=environment, text=True, capture_output=True, timeout=15,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("WELLMAN-BUILD-TOOLS-MISSING", result.stderr)
            self.assertNotIn("build and install the wheel", result.stdout)
            self.assertNotIn("Retrying", result.stderr)
            self.assertFalse(list(root.rglob("*.whl")))


if __name__ == "__main__":
    unittest.main()
