import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class AdoptionHarmonizationTest(unittest.TestCase):
    def test_default_manifest_workstreams_are_orthogonal(self):
        manifest_path = ROOT / "governance" / "manifest.default.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        coordination = manifest["coordination"]
        workstreams = coordination["workstreams"]

        gov_owned = set(workstreams["governance"]["ownedPaths"])
        integration_owned = set(workstreams["integration"]["ownedPaths"])
        integration_required = set(coordination["integration"]["requiredForPaths"])

        # 1. Integration requiredForPaths must not claim governance-owned standard files
        for forbidden in (".governance/**", "AGENTS.md", ".subactor/manifest.json", ".governance/manifest.json"):
            self.assertNotIn(
                forbidden,
                integration_required,
                f"{forbidden} should not be in integration.requiredForPaths",
            )
            self.assertNotIn(
                forbidden,
                integration_owned,
                f"{forbidden} should not be in integration.ownedPaths",
            )

        # 2. Governance workstream must own standard files
        for required_gov in (
            ".aider.conf.yml",
            ".cursor/rules/**",
            ".githooks/**",
            ".github/copilot-instructions.md",
            ".github/workflows/new-project-governance.yml",
            ".gitignore",
            ".governance/**",
            ".subactor/**",
            "AGENTS.md",
            "CLAUDE.md",
            "GEMINI.md",
            "wellmanifest_governance.py",
            "worktree-guard.yaml",
        ):
            self.assertIn(
                required_gov,
                gov_owned,
                f"{required_gov} must be declared in governance.ownedPaths",
            )

        # 3. Governance and integration must not have exact duplicate path entries
        overlap = gov_owned.intersection(integration_owned)
        self.assertEqual(overlap, set(), f"governance and integration ownedPaths overlap on {overlap}")


if __name__ == "__main__":
    unittest.main()
