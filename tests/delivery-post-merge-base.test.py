#!/usr/bin/env python3
"""Exercise published delivery bases and stale proposals using real Git history."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import governance_check as governance


class PublishedDeliveryBaseTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="delivery-base-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.name", "Delivery test")
        self.git("config", "user.email", "delivery@example.invalid")
        self.git("config", "commit.gpgsign", "false")
        self.accepted = self.commit("src/base.py", "base\n")
        self.git("update-ref", "refs/remotes/origin/main", self.accepted)

    def git(self, *arguments):
        return subprocess.check_output(
            ["git", "-C", str(self.root), *arguments], stderr=subprocess.PIPE,
        ).decode().strip()

    def commit(self, name, content):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        self.git("add", name)
        self.git("commit", "-qm", name)
        return self.git("rev-parse", "HEAD")

    def publish(self):
        self.git("update-ref", "refs/remotes/origin/main", "HEAD")

    def findings(self, base):
        report = governance.Report(self.root)
        governance.check_delivery_base(
            self.root, {"targetBranches": ["main"]},
            {"targetBranch": "main", "acceptedBaseSha": self.accepted,
             "architecture": {"components": [{"paths": ["src/**"]}]}},
            SimpleNamespace(directory=Path("project/ticket-001")),
            "project/ticket-001/intent.json", base, report,
        )
        return report.findings

    def assert_overlap(self, base):
        self.assertIn("GOV-BASE-002", [finding.code for finding in self.findings(base)])

    def test_clean_published_single_commit_uses_its_preceding_base(self):
        self.commit("src/feature.py", "feature\n")
        self.publish()
        self.assertEqual([], self.findings(self.accepted))

    def merge_feature(self, target_path):
        self.git("checkout", "-qb", "ticket-001")
        self.commit("src/feature.py", "feature\n")
        self.git("checkout", "-q", "main")
        before = self.commit(target_path, "target advance\n")
        self.git("merge", "--no-ff", "-qm", "integrate feature", "ticket-001")
        self.publish()
        return before

    def test_clean_published_merge_preserves_unrelated_target_advance(self):
        before = self.merge_feature("docs/target.md")
        self.assertEqual([], self.findings(before))

    def test_published_merge_still_rejects_intervening_target_overlap(self):
        before = self.merge_feature("src/target.py")
        findings = self.findings(before)
        self.assertEqual(["GOV-BASE-002"], [finding.code for finding in findings])
        self.assertEqual(["src/target.py"], findings[0].evidence["overlappingPaths"])

    def test_unpublished_feature_against_accepted_target_passes(self):
        self.git("checkout", "-qb", "ticket-001")
        self.commit("src/feature.py", "feature\n")
        self.assertEqual([], self.findings(self.accepted))

    def test_unpublished_feature_cannot_hide_target_drift_with_old_supplied_base(self):
        target = self.commit("src/target.py", "target advance\n")
        self.git("update-ref", "refs/remotes/origin/main", target)
        self.git("checkout", "-qb", "ticket-001", self.accepted)
        self.commit("src/feature.py", "feature\n")
        self.assert_overlap(self.accepted)

    def test_dirty_published_tree_stays_conservative(self):
        self.commit("src/feature.py", "feature\n")
        self.publish()
        (self.root / "src/feature.py").write_text("unpublished edits\n")
        self.assert_overlap(self.accepted)

    def test_untracked_source_stays_conservative(self):
        self.commit("src/feature.py", "feature\n")
        self.publish()
        (self.root / "src/untracked.py").write_text("unpublished source\n")
        self.assert_overlap(self.accepted)

    def test_missing_or_self_base_stays_conservative(self):
        self.commit("src/feature.py", "feature\n")
        self.publish()
        for base in (None, "HEAD"):
            with self.subTest(base=base):
                self.assert_overlap(base)

    def test_older_supplied_base_cannot_hide_a_first_parent_advance(self):
        self.commit("src/target.py", "target advance\n")
        self.commit("src/feature.py", "feature\n")
        self.publish()
        self.assert_overlap(self.accepted)

    def test_unreadable_worktree_observation_stays_conservative(self):
        self.commit("src/feature.py", "feature\n")
        self.publish()
        original = governance.git_output

        def observe(root, arguments):
            if arguments[0] == "status":
                raise subprocess.CalledProcessError(128, ["git", *arguments])
            return original(root, arguments)

        with patch.object(governance, "git_output", side_effect=observe):
            self.assert_overlap(self.accepted)


if __name__ == "__main__":
    unittest.main()
