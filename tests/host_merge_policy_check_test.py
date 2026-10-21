#!/usr/bin/env python3
"""The governance gate warns about the superseded autonomous-merge host block (issue #507)."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load(name: str, relative: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


sys.path.insert(0, str(ROOT / "scripts"))
CHECK = _load("host_merge_governance_check", "scripts/governance_check.py")
POLICY = _load("host_merge_publication_policy", "scripts/host_publication_policy.py")
STALE = ("# Agents\n<!-- wellmanifest:autonomous-merge:start -->\n## Prymat Zielonych Testów\n"
         "Merge on green under `wellmanifest/merge@ticket-008`; use gh pr merge --admin.\n"
         "<!-- wellmanifest:autonomous-merge:end -->\n")


class HostMergePolicyCheckTest(unittest.TestCase):
    def findings(self, files: dict[str, str]):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for name, text in files.items():
                (root / name).write_text(text, encoding="utf-8")
            report = CHECK.Report(root)
            CHECK.check_host_merge_policy(root, report)
            return [finding for finding in report.findings if finding.code == "GOV-HOST-MERGE-001"], report

    def test_stale_block_is_a_warning_naming_each_file(self):
        found, report = self.findings({"AGENTS.md": STALE, "CLAUDE.md": STALE, "README.md": STALE})
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0].severity, "warning")
        self.assertEqual(sorted(found[0].paths), ["AGENTS.md", "CLAUDE.md"])
        self.assertEqual(report.errors, 0)

    def test_reconciled_block_passes(self):
        found, _ = self.findings({"AGENTS.md": POLICY.render(STALE)})
        self.assertEqual(found, [])

    def test_files_without_the_block_or_with_the_text_elsewhere_pass(self):
        prose = "# Agents\nHistory: wellmanifest/merge@ticket-008 was superseded.\n"
        found, _ = self.findings({"AGENTS.md": prose, "GEMINI.md": "# Gemini\n"})
        self.assertEqual(found, [])

    def test_symlinked_host_file_is_not_followed(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            outside = root.parent / (root.name + "-outside.md")
            outside.write_text(STALE, encoding="utf-8")
            try:
                (root / "AGENTS.md").symlink_to(outside)
                report = CHECK.Report(root)
                CHECK.check_host_merge_policy(root, report)
                self.assertEqual([f for f in report.findings if f.code == "GOV-HOST-MERGE-001"], [])
            finally:
                outside.unlink()

    def test_code_is_registered_with_a_runbook(self):
        codes = json.loads((ROOT / "governance/diagnostics.json").read_text(encoding="utf-8"))["codes"]
        documentation = codes["GOV-HOST-MERGE-001"]["documentation"]
        runbook = (ROOT / documentation).read_text(encoding="utf-8")
        for section in ("## Situation", "## Meaning", "## Safe resolution", "## Verification",
                        "## Do not", "## Related rules"):
            self.assertIn(section, runbook)

    def test_bundled_checker_matches_the_script(self):
        bundled = ROOT / "packages/wellman/src/wellman/_bundled/governance_check.py"
        self.assertEqual(bundled.read_bytes(), (ROOT / "scripts/governance_check.py").read_bytes())


if __name__ == "__main__":
    unittest.main()
