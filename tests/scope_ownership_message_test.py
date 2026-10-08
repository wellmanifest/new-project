#!/usr/bin/env python3
"""GOV-WORK-START-001 scope rejections name unowned paths and their owners (ticket-324)."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
SOURCE = Path(__file__).resolve().parents[1]
STORAGE = SOURCE / "scripts" / "ticket_storage.py"


class ScopeOwnershipMessageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="scope-message-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        manifest = json.loads((SOURCE / "governance" / "manifest.default.json").read_text(encoding="utf-8"))
        manifest["coordination"]["workstreams"] = {
            "application": {"ownedPaths": ["src/**", "tests/**"]},
            "governance": {"ownedPaths": ["README.md", "project/**"]},
            "integration": {"ownedPaths": ["docs/**"]},
        }
        (self.root / ".governance").mkdir()
        (self.root / ".governance" / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    def scope(self, workstream, *paths):
        arguments = [sys.executable, str(STORAGE), "scope", "--root", str(self.root), "--workstream", workstream]
        for path in paths:
            arguments += ["--path", path]
        return subprocess.run(arguments, capture_output=True, text=True, check=False)

    def test_owned_scope_is_accepted(self):
        result = self.scope("application", "src/app.py")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), ["src/app.py"])

    def test_unowned_paths_name_their_owning_workstreams(self):
        result = self.scope("application", "src/app.py", "README.md", "docs/**")
        self.assertEqual(result.returncode, 3)
        self.assertIn("not owned by workstream 'application'", result.stderr)
        self.assertIn("README.md (owned by governance)", result.stderr)
        self.assertIn("docs/** (owned by integration)", result.stderr)

    def test_path_owned_by_nobody_is_named(self):
        result = self.scope("application", "infra/main.tf")
        self.assertEqual(result.returncode, 3)
        self.assertIn("infra/main.tf (owned by no workstream)", result.stderr)

    def test_unknown_workstream_lists_declared_ones(self):
        result = self.scope("frontend", "src/app.py")
        self.assertEqual(result.returncode, 3)
        self.assertIn("unknown workstream 'frontend'; declared: application, governance, integration", result.stderr)

    def test_unsafe_characters_are_redacted(self):
        result = self.scope("application", "docs/$(id)`x`")
        self.assertEqual(result.returncode, 3)
        self.assertIn("<redacted> (owned by integration)", result.stderr)
        self.assertNotIn("$(id)", result.stderr)


if __name__ == "__main__":
    unittest.main()
