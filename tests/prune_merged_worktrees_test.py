#!/usr/bin/env python3
"""Tests for the prune_merged_worktrees tool."""

import subprocess
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.prune_merged_worktrees import prune_merged_worktrees, is_worktree_clean, is_ancestor


def test_prune_merged_worktrees_lifecycle(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()

    subprocess.run(["git", "-C", str(repo), "init", "-b", "main"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.name", "Test User"], check=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.email", "test@example.com"], check=True)

    f1 = repo / "file.txt"
    f1.write_text("initial")
    subprocess.run(["git", "-C", str(repo), "add", "file.txt"], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-m", "initial"], check=True)

    # Add worktree 1: merged
    wt1 = tmp_path / "wt1"
    subprocess.run(["git", "-C", str(repo), "worktree", "add", "-b", "branch1", str(wt1)], check=True, capture_output=True)
    (wt1 / "branch1.txt").write_text("branch1")
    subprocess.run(["git", "-C", str(wt1), "add", "branch1.txt"], check=True)
    subprocess.run(["git", "-C", str(wt1), "commit", "-m", "branch1"], check=True)

    # Merge branch1 into main
    subprocess.run(["git", "-C", str(repo), "merge", "branch1", "-m", "merge branch1"], check=True, capture_output=True)

    # Add worktree 2: unmerged
    wt2 = tmp_path / "wt2"
    subprocess.run(["git", "-C", str(repo), "worktree", "add", "-b", "branch2", str(wt2)], check=True, capture_output=True)
    (wt2 / "branch2.txt").write_text("branch2")
    subprocess.run(["git", "-C", str(wt2), "add", "branch2.txt"], check=True)
    subprocess.run(["git", "-C", str(wt2), "commit", "-m", "branch2"], check=True)

    # Add worktree 3: merged but dirty
    wt3 = tmp_path / "wt3"
    subprocess.run(["git", "-C", str(repo), "worktree", "add", "-b", "branch3", str(wt3)], check=True, capture_output=True)
    # Merge branch3 into main
    subprocess.run(["git", "-C", str(repo), "merge", "branch3", "-m", "merge branch3"], check=True, capture_output=True)
    # make dirty
    (wt3 / "dirty.txt").write_text("dirty")

    # Run dry-run
    res_dry = prune_merged_worktrees(repo, target_branch="main", dry_run=True)
    pruned_paths_dry = [item["path"] for item in res_dry["pruned"]]
    assert str(wt1) in pruned_paths_dry
    assert str(wt2) not in pruned_paths_dry
    assert str(wt3) not in pruned_paths_dry

    # Run actual prune
    res_actual = prune_merged_worktrees(repo, target_branch="main", dry_run=False)
    pruned_paths = [item["path"] for item in res_actual["pruned"]]
    assert str(wt1) in pruned_paths
    assert not wt1.exists()

    # wt2 and wt3 must remain
    assert wt2.exists()
    assert wt3.exists()
