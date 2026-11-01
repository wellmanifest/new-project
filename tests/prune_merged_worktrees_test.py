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


# Every mutation below is confined to a new disposable repository. In
# particular, races update synthetic refs rather than any host checkout.
def _git(repo, *args):
    return subprocess.run(
        ["git", "-C", str(repo), *args], check=True,
        capture_output=True, text=True,
    ).stdout.strip()


def _merged_fixture(tmp_path, *, remote_target=False):
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    for key, value in {
        "user.name": "Disposable Fixture",
        "user.email": "fixture@example.invalid",
        "commit.gpgsign": "false",
        "core.hooksPath": str(repo / ".no-hooks"),
    }.items():
        _git(repo, "config", key, value)
    (repo / "README").write_text("initial\n")
    _git(repo, "add", "README")
    _git(repo, "commit", "-qm", "initial fixture")
    initial = _git(repo, "rev-parse", "HEAD")
    branch = "ticket/001-disposable"
    wt = tmp_path / "linked"
    _git(repo, "worktree", "add", "-b", branch, str(wt))
    (wt / "delivered.txt").write_text("integrated fixture\n")
    _git(wt, "add", "delivered.txt")
    _git(wt, "commit", "-qm", "integrated fixture")
    _git(repo, "merge", "--ff-only", branch)
    head = _git(repo, "rev-parse", "HEAD")
    if remote_target:
        _git(repo, "update-ref", "refs/remotes/origin/main", head)
    return repo, wt, branch, initial, head


def test_declined_branch_delete_never_forces_or_globally_prunes(tmp_path, monkeypatch):
    from scripts import prune_merged_worktrees as module
    repo, wt, branch, _, head = _merged_fixture(tmp_path)
    original = module.git_cmd
    calls = []

    def decline(cwd, *args, **kwargs):
        calls.append(args)
        if args[:2] == ("branch", "-d") or (args[:1] == ("update-ref",) and "--stdin" in args):
            return subprocess.CompletedProcess(args, 1, "", "synthetic deletion refusal")
        return original(cwd, *args, **kwargs)

    monkeypatch.setattr(module, "git_cmd", decline)
    report = module.prune_merged_worktrees(repo)
    assert not wt.exists()
    assert _git(repo, "rev-parse", "refs/heads/" + branch) == head
    assert not any(args[:2] == ("branch", "-D") for args in calls)
    assert ("worktree", "prune") not in calls
    assert any(item.get("branch") == branch for item in report["skipped"])


def test_branch_advanced_after_removal_is_retained(tmp_path, monkeypatch):
    from scripts import prune_merged_worktrees as module
    repo, wt, branch, _, head = _merged_fixture(tmp_path)
    tree = _git(repo, "rev-parse", head + "^{tree}")
    advanced = _git(repo, "commit-tree", tree, "-p", head, "-m", "unique unmerged fixture")
    original = module.git_cmd

    def advance(cwd, *args, **kwargs):
        result = original(cwd, *args, **kwargs)
        if args[:2] == ("worktree", "remove") and result.returncode == 0:
            _git(repo, "update-ref", "refs/heads/" + branch, advanced, head)
        return result

    monkeypatch.setattr(module, "git_cmd", advance)
    module.prune_merged_worktrees(repo)
    assert not wt.exists()
    assert _git(repo, "rev-parse", "refs/heads/" + branch) == advanced
    assert _git(repo, "rev-parse", "main") == head


def test_target_changed_after_removal_retains_branch(tmp_path, monkeypatch):
    from scripts import prune_merged_worktrees as module
    repo, wt, branch, initial, head = _merged_fixture(tmp_path, remote_target=True)
    original = module.git_cmd

    def change_target(cwd, *args, **kwargs):
        result = original(cwd, *args, **kwargs)
        if args[:2] == ("worktree", "remove") and result.returncode == 0:
            _git(repo, "update-ref", "refs/remotes/origin/main", initial, head)
        return result

    monkeypatch.setattr(module, "git_cmd", change_target)
    module.prune_merged_worktrees(repo)
    assert not wt.exists()
    assert _git(repo, "rev-parse", "refs/heads/" + branch) == head
    assert _git(repo, "rev-parse", "refs/remotes/origin/main") == initial


def test_target_checkout_is_preserved(tmp_path):
    repo, _, _, _, head = _merged_fixture(tmp_path)
    _git(repo, "switch", "-c", "workspace-dev")
    target = tmp_path / "target-main"
    _git(repo, "worktree", "add", str(target), "main")
    prune_merged_worktrees(repo)
    assert target.is_dir()
    assert _git(repo, "rev-parse", "refs/heads/main") == head
    assert _git(target, "branch", "--show-current") == "main"


def test_ignored_data_and_unrelated_missing_registration_are_preserved(tmp_path, monkeypatch):
    from scripts import prune_merged_worktrees as module
    import shutil
    repo, wt, _, _, _ = _merged_fixture(tmp_path)
    _git(repo, "config", "core.excludesFile", str(repo / ".git/info/exclude"))
    (repo / ".git/info/exclude").write_text("ignored-data.txt\n")
    sentinel = wt / "ignored-data.txt"
    sentinel.write_text("unique ignored fixture data\n")
    module.prune_merged_worktrees(repo)
    assert sentinel.read_text() == "unique ignored fixture data\n"
    sentinel.unlink()
    missing = tmp_path / "missing"
    _git(repo, "worktree", "add", "-b", "ticket/002-missing", str(missing))
    shutil.rmtree(missing)
    original = module.git_cmd
    calls = []

    def observe(cwd, *args, **kwargs):
        calls.append(args)
        return original(cwd, *args, **kwargs)

    monkeypatch.setattr(module, "git_cmd", observe)
    module.prune_merged_worktrees(repo)
    assert not wt.exists()
    assert ("worktree", "prune") not in calls
    assert str(missing) in _git(repo, "worktree", "list", "--porcelain")


def test_branch_changed_before_removal_preserves_checkout(tmp_path, monkeypatch):
    from scripts import prune_merged_worktrees as module
    repo, wt, branch, _, head = _merged_fixture(tmp_path)
    tree = _git(repo, "rev-parse", head + "^{tree}")
    advanced = _git(repo, "commit-tree", tree, "-p", head, "-m", "unique before-removal fixture")
    original = module.get_worktrees

    def change_after_inventory(path):
        snapshot = original(path)
        _git(repo, "update-ref", "refs/heads/" + branch, advanced, head)
        return snapshot

    monkeypatch.setattr(module, "get_worktrees", change_after_inventory)
    report = module.prune_merged_worktrees(repo)
    assert wt.is_dir()
    assert _git(repo, "rev-parse", "refs/heads/" + branch) == advanced
    assert not report["pruned"]
    assert any("changed since observation" in item["reason"] for item in report["skipped"])


def test_symbolic_branch_race_never_deletes_another_ref(tmp_path, monkeypatch):
    from scripts import prune_merged_worktrees as module
    repo, wt, branch, _, head = _merged_fixture(tmp_path)
    unrelated = "refs/heads/unrelated"
    _git(repo, "update-ref", unrelated, head)
    original = module.git_cmd

    def replace_with_alias(cwd, *args, **kwargs):
        result = original(cwd, *args, **kwargs)
        if args[:2] == ("worktree", "remove") and result.returncode == 0:
            _git(repo, "symbolic-ref", "refs/heads/" + branch, unrelated)
        return result

    monkeypatch.setattr(module, "git_cmd", replace_with_alias)
    module.prune_merged_worktrees(repo)
    assert _git(repo, "rev-parse", unrelated) == head
    assert _git(repo, "rev-parse", "main") == head
