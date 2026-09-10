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

    def implicit_base(self, supplied=None, count=1, head="HEAD", targets=None):
        records = [SimpleNamespace(intent={"delivery": {
            "acceptedBaseSha": self.accepted, "targetBranch": target,
            "standardAdoption": {},
        }}) for target in (targets if targets is not None else ["main"] * count)]
        with patch.object(governance, "active_ticket_records", return_value=records):
            return governance.resolve_validation_base(supplied, self.root, [], {}, head)

    def publish_after_historical_adoption(self):
        preceding = self.commit("src/intervening.py", "already delivered\n")
        self.commit("src/latest.py", "latest delivery\n")
        self.publish()
        return preceding

    def test_implicit_base_limits_clean_published_scope_to_latest_delivery(self):
        preceding = self.publish_after_historical_adoption()
        self.assertEqual(preceding, self.implicit_base())
        self.assertEqual(["src/latest.py"], governance.changed_paths(
            self.root, self.implicit_base(), "HEAD", [],
        ))

    def test_implicit_base_on_detached_published_checkout(self):
        preceding = self.publish_after_historical_adoption()
        self.git("checkout", "--detach", "-q", "HEAD")
        self.assertEqual(preceding, self.implicit_base())

    def test_implicit_base_of_published_merge_is_first_parent(self):
        preceding = self.merge_feature("docs/target.md")
        self.assertEqual(preceding, self.implicit_base())

    def test_explicit_base_is_never_replaced(self):
        self.publish_after_historical_adoption()
        self.assertEqual(self.accepted, self.implicit_base(self.accepted))
        self.assertEqual("missing-explicit-base", self.implicit_base("missing-explicit-base"))

    def test_implicit_base_does_not_narrow_a_different_or_unreadable_head(self):
        preceding = self.publish_after_historical_adoption()
        for head in (preceding, "missing-head"):
            with self.subTest(head=head):
                self.assertEqual(self.accepted, self.implicit_base(head=head))

    def test_implicit_base_retains_dirty_and_staged_adoption_scope(self):
        self.publish_after_historical_adoption()
        (self.root / "src/latest.py").write_text("pending\n")
        self.assertEqual(self.accepted, self.implicit_base())
        self.git("add", "src/latest.py")
        self.assertEqual(self.accepted, self.implicit_base())

    def test_implicit_base_retains_untracked_adoption_scope(self):
        self.publish_after_historical_adoption()
        (self.root / "src/untracked.py").write_text("pending\n")
        self.assertEqual(self.accepted, self.implicit_base())

    def test_implicit_base_retains_unpublished_adoption_scope(self):
        self.publish_after_historical_adoption()
        self.git("checkout", "-qb", "ticket-002")
        self.commit("src/pending.py", "pending\n")
        self.assertEqual(self.accepted, self.implicit_base())

    def test_implicit_base_requires_remote_target_not_local_branch(self):
        self.publish_after_historical_adoption()
        self.git("update-ref", "-d", "refs/remotes/origin/main")
        self.assertEqual(self.accepted, self.implicit_base())

    def test_implicit_base_does_not_select_absent_adoptions(self):
        self.publish_after_historical_adoption()
        self.assertIsNone(self.implicit_base(count=0))

    def test_repeated_published_adoptions_select_the_latest_integration(self):
        preceding = self.publish_after_historical_adoption()
        for count in (2, 3, 20):
            with self.subTest(count=count):
                self.assertEqual(preceding, self.implicit_base(count=count))
                self.assertEqual(["src/latest.py"], governance.changed_paths(
                    self.root, self.implicit_base(count=count), "HEAD", [],
                ))

    def test_repeated_published_adoptions_on_detached_head(self):
        preceding = self.publish_after_historical_adoption()
        self.git("checkout", "--detach", "-q", "HEAD")
        self.assertEqual(preceding, self.implicit_base(count=3))

    def test_repeated_adoptions_preserve_explicit_base(self):
        self.publish_after_historical_adoption()
        self.assertEqual(self.accepted, self.implicit_base(self.accepted, count=3))

    def test_repeated_adoptions_cannot_hide_dirty_or_untracked_work(self):
        self.publish_after_historical_adoption()
        (self.root / "src/latest.py").write_text("pending\n")
        self.assertIsNone(self.implicit_base(count=3))
        self.git("add", "src/latest.py")
        self.assertIsNone(self.implicit_base(count=3))
        self.git("commit", "-qm", "pending")
        self.publish()
        (self.root / "src/untracked.py").write_text("pending\n")
        self.assertIsNone(self.implicit_base(count=3))

    def test_repeated_adoptions_require_the_exact_published_head(self):
        self.publish_after_historical_adoption()
        self.assertIsNone(self.implicit_base(count=3, head=self.accepted))
        self.git("checkout", "-qb", "ticket-002")
        self.commit("src/pending.py", "pending\n")
        self.assertIsNone(self.implicit_base(count=3))

    def test_repeated_adoptions_require_an_unambiguous_target(self):
        self.publish_after_historical_adoption()
        self.git("update-ref", "refs/remotes/origin/release", "HEAD")
        self.assertIsNone(self.implicit_base(targets=["main", "release"]))

    def test_repeated_adoptions_require_remote_and_readable_observations(self):
        self.publish_after_historical_adoption()
        original = governance.git_output

        def observe(root, arguments):
            if arguments[0] == "status":
                raise subprocess.CalledProcessError(128, ["git", *arguments])
            return original(root, arguments)

        with patch.object(governance, "git_output", side_effect=observe):
            self.assertIsNone(self.implicit_base(count=3))
        self.git("update-ref", "-d", "refs/remotes/origin/main")
        self.assertIsNone(self.implicit_base(count=3))

    def test_implicit_base_requires_readable_first_parent(self):
        self.assertEqual(self.accepted, self.implicit_base())

    def test_implicit_base_requires_readable_clean_status(self):
        self.publish_after_historical_adoption()
        original = governance.git_output

        def observe(root, arguments):
            if arguments[0] == "status":
                raise subprocess.CalledProcessError(128, ["git", *arguments])
            return original(root, arguments)

        with patch.object(governance, "git_output", side_effect=observe):
            self.assertEqual(self.accepted, self.implicit_base())


if __name__ == "__main__":
    unittest.main()
