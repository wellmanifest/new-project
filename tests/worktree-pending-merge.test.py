#!/usr/bin/env python3
"""Exercise pending merges with real indexes, conflicts and remote refs."""
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("overlap", ROOT / "scripts/worktree_overlap_check.py")
overlap = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = overlap
spec.loader.exec_module(overlap)


class PendingMergeTest(unittest.TestCase):
    def git(self, path, *args, check=True):
        return subprocess.run(["git", "-C", str(path), *args], check=check,
                              text=True, capture_output=True)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.main = Path(self.temp.name) / "main"
        self.peer = Path(self.temp.name) / "peer"
        self.feature = Path(self.temp.name) / "feature"
        self.git(Path(self.temp.name), "init", "-b", "main", str(self.main))
        self.git(self.main, "config", "user.email", "test@example.invalid")
        self.git(self.main, "config", "user.name", "test")
        for name in ("imported.txt", "conflict.txt", "deleted.txt"):
            (self.main / name).write_text("base\n")
        self.git(self.main, "add", ".")
        self.git(self.main, "commit", "-m", "base")
        self.git(self.main, "worktree", "add", "-b", "ticket/001-feature", str(self.feature))
        (self.feature / "conflict.txt").write_text("feature\n")
        self.git(self.feature, "commit", "-am", "feature")
        (self.main / "imported.txt").write_text("approved main\n")
        (self.main / "conflict.txt").write_text("main\n")
        (self.main / "deleted.txt").unlink()
        self.git(self.main, "commit", "-am", "approved changes")
        self.main_sha = self.git(self.main, "rev-parse", "HEAD").stdout.strip()
        self.git(self.main, "update-ref", "refs/remotes/origin/main", self.main_sha)
        self.git(self.main, "symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/main")
        self.git(self.main, "worktree", "add", "-b", "ticket/002-peer", str(self.peer))
        (self.peer / "peer.txt").write_text("independent\n")
        self.git(self.peer, "add", ".")
        self.git(self.peer, "commit", "-m", "peer")
        result = self.git(self.feature, "merge", "--no-commit", "origin/main", check=False)
        self.assertEqual(result.returncode, 1, result.stderr)

    def checkout(self, path):
        dirty = overlap.dirty_paths(path, ())
        return overlap.Checkout(path, self.main / ".git", "fixture",
                                self.git(path, "rev-parse", "HEAD").stdout.strip(),
                                None, bool(dirty), True, dirty,
                                overlap.changed_paths(path, ()), (), ())

    def contested(self):
        first, second = self.checkout(self.feature), self.checkout(self.peer)
        result = overlap.contested_paths(first, second, ())
        self.assertEqual(result, overlap.contested_paths(second, first, ()))
        return result

    def test_clean_main_imports_are_not_competing_edits(self):
        self.assertEqual(self.contested(), ("conflict.txt",))
        # Reporting must still expose all dirty paths, including imports.
        self.assertIn("imported.txt", overlap.dirty_paths(self.feature, ()))

    def test_staged_local_edit_remains_contested(self):
        (self.feature / "imported.txt").write_text("local staged\n")
        self.git(self.feature, "add", "imported.txt")
        self.assertIn("imported.txt", self.contested())

    def test_unstaged_local_edit_remains_contested(self):
        (self.feature / "imported.txt").write_text("local unstaged\n")
        self.assertIn("imported.txt", self.contested())

    def test_recreated_deleted_file_remains_contested(self):
        (self.feature / "deleted.txt").write_text("untracked replacement\n")
        self.assertIn("deleted.txt", self.contested())

    def test_local_mode_change_remains_contested(self):
        self.git(self.feature, "update-index", "--chmod=+x", "imported.txt")
        self.assertIn("imported.txt", self.contested())

    def test_unresolved_index_remains_contested(self):
        self.assertIn("conflict.txt", self.contested())

    def test_missing_remote_ref_is_conservative(self):
        self.git(self.main, "update-ref", "-d", "refs/remotes/origin/main")
        self.assertIn("imported.txt", self.contested())

    def test_different_merge_head_is_conservative(self):
        self.git(self.feature, "merge", "--abort")
        self.git(self.main, "switch", "-c", "unreviewed")
        (self.main / "unreviewed.txt").write_text("unreviewed\n")
        self.git(self.main, "add", ".")
        self.git(self.main, "commit", "-m", "unreviewed")
        self.assertEqual(self.git(self.feature, "merge", "--no-commit", "unreviewed",
                                  check=False).returncode, 1)
        self.assertIn("imported.txt", self.contested())

    def test_no_pending_merge_is_conservative(self):
        self.git(self.feature, "merge", "--abort")
        (self.feature / "imported.txt").write_text("approved main\n")
        self.git(self.feature, "add", "imported.txt")
        self.assertIn("imported.txt", self.contested())

    def test_multiple_merge_heads_are_conservative(self):
        merge_file = Path(self.git(self.feature, "rev-parse", "--path-format=absolute",
                                   "--git-path", "MERGE_HEAD").stdout.strip())
        peer_sha = self.git(self.peer, "rev-parse", "HEAD").stdout.strip()
        merge_file.write_text(self.main_sha + "\n" + peer_sha + "\n")
        self.assertIn("imported.txt", self.contested())

    def test_clean_import_does_not_claim_peers_unstaged_edit(self):
        (self.peer / "imported.txt").write_text("peer's own edit\n")
        self.assertEqual(self.contested(), ("conflict.txt",))


if __name__ == "__main__":
    unittest.main()
