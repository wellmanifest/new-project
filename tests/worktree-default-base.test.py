#!/usr/bin/env python3
"""A new writer must not own main's changes relative to an older branch."""
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("default_base_overlap", ROOT / "scripts/worktree_overlap_check.py")
overlap = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = overlap
spec.loader.exec_module(overlap)


class DefaultBaseTest(unittest.TestCase):
    def git(self, path, *args, check=True):
        return subprocess.run(["git", "-C", str(path), *args], check=check,
                              capture_output=True, text=True)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.main, self.old, self.new = (self.root / name for name in ("main", "old", "new"))
        self.git(self.root, "init", "-b", "main", str(self.main))
        self.git(self.main, "config", "user.name", "Fixture")
        self.git(self.main, "config", "user.email", "fixture@example.invalid")
        (self.main / "shared.txt").write_text("base\n")
        self.git(self.main, "add", ".")
        self.git(self.main, "commit", "-m", "base")
        self.base = self.git(self.main, "rev-parse", "HEAD").stdout.strip()
        self.git(self.main, "worktree", "add", "-b", "ticket/001-old", str(self.old))
        (self.old / "shared.txt").write_text("old branch\n")
        self.git(self.old, "commit", "-am", "old contribution")
        (self.main / "shared.txt").write_text("published main\n")
        self.git(self.main, "commit", "-am", "published contribution")
        self.main_sha = self.git(self.main, "rev-parse", "HEAD").stdout.strip()
        self.git(self.main, "update-ref", "refs/remotes/origin/main", self.main_sha)
        self.git(self.main, "symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/main")
        self.git(self.main, "worktree", "add", "-b", "ticket/002-new", str(self.new))
        (self.new / "independent.txt").write_text("new writer's own change\n")

    def checkout(self, path):
        dirty = overlap.dirty_paths(path, ())
        return overlap.Checkout(path, path / ".git", "fixture",
                                self.git(path, "rev-parse", "HEAD").stdout.strip(),
                                None, bool(dirty), True, dirty,
                                overlap.changed_paths(path, ()), (), ())

    def contested(self):
        first, second = self.checkout(self.old), self.checkout(self.new)
        answer = overlap.contested_paths(first, second, ())
        self.assertEqual(answer, overlap.contested_paths(second, first, ()))
        return answer

    def test_committed_main_conflict_does_not_belong_to_new_writer(self):
        self.assertEqual(self.contested(), ())

    def test_pending_conflict_is_reported_but_not_attributed_to_new_writer(self):
        self.assertEqual(self.git(self.old, "merge", "--no-commit", "origin/main", check=False).returncode, 1)
        self.assertIn("shared.txt", overlap.dirty_paths(self.old, ()))
        self.assertEqual(self.contested(), ())

    def test_staged_resolution_does_not_implicate_independent_writer(self):
        self.git(self.old, "merge", "--no-commit", "origin/main", check=False)
        (self.old / "shared.txt").write_text("old writer's resolution\n")
        self.git(self.old, "add", "shared.txt")
        self.assertEqual(self.contested(), ())

    def test_new_committed_disjoint_change_does_not_own_main_history(self):
        self.git(self.new, "add", ".")
        self.git(self.new, "commit", "-m", "new independent change")
        self.assertEqual(self.contested(), ())

    def test_actual_dirty_peer_edit_conflicts_with_old_commit(self):
        (self.new / "shared.txt").write_text("new writer edits the same file\n")
        self.assertEqual(self.contested(), ("shared.txt",))

    def test_actual_committed_peer_edit_remains_conflicted(self):
        (self.new / "shared.txt").write_text("new writer commit\n")
        self.git(self.new, "commit", "-am", "new competing contribution")
        self.assertEqual(self.contested(), ("shared.txt",))

    def test_missing_remote_observation_is_conservative(self):
        self.git(self.main, "update-ref", "-d", "refs/remotes/origin/main")
        self.assertEqual(self.contested(), ("shared.txt",))

    def test_missing_merge_tree_uses_actual_contributions(self):
        with patch.object(overlap, "merge_tree_conflicts", return_value=None):
            self.assertEqual(self.contested(), ())
            (self.new / "shared.txt").write_text("new competing edit\n")
            self.assertEqual(self.contested(), ("shared.txt",))

    def test_two_dirty_writers_on_main_still_conflict(self):
        self.git(self.old, "reset", "--hard", self.main_sha)
        (self.old / "shared.txt").write_text("first edit\n")
        (self.new / "shared.txt").write_text("second edit\n")
        self.assertEqual(self.contested(), ("shared.txt",))

    def test_divergent_clone_observation_is_conservative(self):
        clone = self.root / "clone"
        self.git(self.root, "clone", "--no-hardlinks", str(self.main), str(clone))
        self.new = clone
        self.git(clone, "update-ref", "refs/remotes/origin/main", self.base)
        (clone / "independent.txt").write_text("clone's independent edit\n")
        self.assertEqual(self.contested(), ("shared.txt",))

    def test_partial_contribution_read_failure_is_conservative(self):
        original = overlap.run_git

        def fail_second_read(path, *args):
            if path == self.new and args == ("diff", "--name-only", "--no-renames", self.main_sha, self.main_sha):
                raise overlap.AuditError("fixture unreadable object")
            return original(path, *args)

        with patch.object(overlap, "run_git", side_effect=fail_second_read):
            self.assertEqual(self.contested(), ("shared.txt",))

    def share_feature_head(self):
        # Both fixtures inherit the same unpublished feature contribution.
        # Only disposable fixture checkouts are reset, never the source repo.
        shared = self.git(self.old, "rev-parse", "HEAD").stdout.strip()
        self.git(self.new, "reset", "--hard", shared)
        return shared

    def test_shared_feature_head_with_one_dirty_writer_is_not_contested(self):
        self.share_feature_head()
        (self.new / "shared.txt").write_text("one actual writer\n")
        self.assertEqual(self.contested(), ())

    def test_shared_feature_with_descendant_disjoint_commit_is_not_contested(self):
        self.share_feature_head()
        self.git(self.new, "add", "independent.txt")
        self.git(self.new, "commit", "-m", "descendant independent contribution")
        (self.old / "shared.txt").write_text("ancestor checkout edits inherited file\n")
        self.assertEqual(self.contested(), ())

    def test_shared_feature_with_two_dirty_writers_remains_contested(self):
        self.share_feature_head()
        (self.old / "shared.txt").write_text("first actual writer\n")
        (self.new / "shared.txt").write_text("second actual writer\n")
        self.assertEqual(self.contested(), ("shared.txt",))

    def test_shared_feature_with_unique_peer_commit_remains_contested(self):
        self.share_feature_head()
        (self.new / "shared.txt").write_text("unique peer contribution\n")
        self.git(self.new, "commit", "-am", "unique peer contribution")
        (self.old / "shared.txt").write_text("competing dirty change\n")
        self.assertEqual(self.contested(), ("shared.txt",))

    def test_shared_feature_with_divergent_disjoint_commits_is_not_contested(self):
        self.share_feature_head()
        (self.old / "old-only.txt").write_text("old-only\n")
        self.git(self.old, "add", "old-only.txt")
        self.git(self.old, "commit", "-m", "old independent contribution")
        self.git(self.new, "add", "independent.txt")
        self.git(self.new, "commit", "-m", "new independent contribution")
        (self.old / "shared.txt").write_text("one dirty inherited path\n")
        self.assertEqual(self.contested(), ())

    def test_shared_feature_with_unreadable_pair_retains_conservative_fallback(self):
        shared = self.share_feature_head()
        (self.new / "shared.txt").write_text("one actual writer\n")
        original = overlap.run_git

        def fail_pair_read(path, *args):
            if args == ("diff", "--name-only", shared, shared):
                raise overlap.AuditError("fixture unreadable pair contribution")
            return original(path, *args)

        with patch.object(overlap, "run_git", side_effect=fail_pair_read):
            self.assertEqual(self.contested(), ("shared.txt",))

    def test_rename_modify_conflict_preserves_renamed_path(self):
        content = "".join(f"line {number}\n" for number in range(20))
        (self.main / "shared.txt").write_text(content + "base\n")
        self.git(self.main, "commit", "-am", "rename fixture base")
        baseline = self.git(self.main, "rev-parse", "HEAD").stdout.strip()
        self.git(self.main, "update-ref", "refs/remotes/origin/main", baseline)
        for checkout in (self.old, self.new):
            self.git(checkout, "reset", "--hard", baseline)
        (self.old / "shared.txt").write_text(content + "old edit\n")
        self.git(self.old, "commit", "-am", "old edit")
        self.git(self.new, "mv", "shared.txt", "renamed.txt")
        (self.new / "renamed.txt").write_text(content + "new edit\n")
        self.git(self.new, "add", "renamed.txt")
        self.git(self.new, "commit", "-m", "rename contribution")
        self.assertIn("renamed.txt", self.contested())


if __name__ == "__main__":
    unittest.main()
