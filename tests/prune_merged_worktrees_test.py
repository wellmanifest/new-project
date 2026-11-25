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
    monkeypatch.setattr(
        module, "_delete_exact_branch",
        lambda *args: subprocess.CompletedProcess(args, 1, "", "synthetic deletion refusal"),
    )
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
    assert _git(repo, "symbolic-ref", "refs/heads/" + branch) == unrelated


def test_dirty_other_checkout_retains_shared_branch(tmp_path):
    repo, wt, branch, _, head = _merged_fixture(tmp_path)
    other = tmp_path / "other"
    _git(repo, "worktree", "add", "--force", str(other), branch)
    sentinel = other / "private-work.txt"
    sentinel.write_text("retained caller data\n")
    prune_merged_worktrees(repo)
    assert not wt.exists()
    assert sentinel.read_text() == "retained caller data\n"
    assert _git(repo, "rev-parse", "refs/heads/" + branch) == head
    assert _git(other, "rev-parse", "HEAD") == head


def _canonical_merged_fixture(tmp_path, *, ticket="ticket-010", slug="runtime-caches", phase="released"):
    import json
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
    (repo / ".gitignore").write_text(
        "/.worktrees/\n"
        ".venv/\n"
        ".pytest_cache/\n"
        ".mypy_cache/\n"
        ".ruff_cache/\n"
        ".tox/\n"
        ".planfile/\n"
        "__pycache__/\n"
        "*.pyc\n"
        "*.egg-info/\n"
        ".env\n"
    )
    subactor = repo / ".subactor"
    subactor.mkdir()
    (subactor / ".gitignore").write_text("leases/\nsessions/\nrecovery/\nreceipts/\ncache/\nsnapshots/\n")
    (subactor / "manifest.json").write_text('{"schema":"subactor/v1"}\n')
    _git(repo, "add", ".gitignore", ".subactor/.gitignore", ".subactor/manifest.json")
    _git(repo, "commit", "-qm", "base")

    num = ticket.removeprefix("ticket-")
    branch = f"ticket/{num}-{slug}"
    stem = f"{ticket}--{slug}"
    wt = repo / ".worktrees" / stem
    wt.parent.mkdir(parents=True, exist_ok=True)
    _git(repo, "worktree", "add", "-b", branch, str(wt))
    pkg = wt / "pkg"
    pkg.mkdir()
    (pkg / "mod.py").write_text("VALUE = 1\n")
    _git(wt, "add", "pkg/mod.py")
    _git(wt, "commit", "-qm", "feature")
    _git(repo, "merge", "--no-ff", "-qm", "merge feature", branch)
    head = _git(wt, "rev-parse", "HEAD")

    leases = repo / ".subactor" / "leases"
    leases.mkdir(parents=True, exist_ok=True)
    lease_path = leases / f"{stem}.json"
    if phase is not None:
        lease_path.write_text(json.dumps({
            "schema": "wellmanifest.change-lease/v1",
            "leaseId": f"allocation-{stem}",
            "ticketId": ticket,
            "worktreeId": stem,
            "branchRef": f"refs/heads/{branch}",
            "phase": phase,
            "publicationFrozen": phase in {"publication_frozen", "dispatching", "approved"},
            "headSha": head,
        }))
    return repo, wt, branch, head, lease_path


def _populate_ignored_runtime_caches(wt: Path) -> None:
    (wt / ".venv" / "bin").mkdir(parents=True)
    (wt / ".venv" / "pyvenv.cfg").write_text("home = /usr/bin\n")
    (wt / ".venv" / "bin" / "python").symlink_to(sys.executable)
    (wt / ".pytest_cache" / "v" / "cache").mkdir(parents=True)
    (wt / ".pytest_cache" / "v" / "cache" / "nodeids").write_text("[]\n")
    (wt / ".mypy_cache").mkdir()
    (wt / ".ruff_cache").mkdir()
    (wt / ".planfile").mkdir()
    (wt / ".planfile" / "state.json").write_text("{}\n")
    (wt / ".subactor" / "cache").mkdir(parents=True)
    (wt / ".subactor" / "cache" / "autonomy-board.md").write_text("# Board\n")
    (wt / ".subactor" / "sessions").mkdir(parents=True)
    (wt / "pkg" / "__pycache__").mkdir(parents=True)
    (wt / "pkg" / "__pycache__" / "mod.cpython-313.pyc").write_bytes(b"pyc")
    (wt / "demo.egg-info").mkdir()
    (wt / "demo.egg-info" / "PKG-INFO").write_text("Name: demo\n")
    ro = wt / ".tox" / "readonly"
    ro.mkdir(parents=True)
    (ro / "cached.txt").write_text("cached\n")
    ro.chmod(0o500)


def test_canonical_released_worktree_with_ignored_runtime_caches_prunes_without_force(tmp_path, monkeypatch):
    import json
    from scripts import prune_merged_worktrees as module
    repo, wt, branch, _, _ = _canonical_merged_fixture(tmp_path, phase="released")
    _populate_ignored_runtime_caches(wt)
    assert not is_worktree_clean(wt)

    calls = []
    original = module.git_cmd

    def spy(cwd, *args):
        calls.append(args)
        return original(cwd, *args)

    monkeypatch.setattr(module, "git_cmd", spy)

    # Opt-out preserves ignored runtime caches
    opt_out = module.prune_merged_worktrees(repo, include_ignored_runtime=False)
    assert not opt_out["pruned"]
    assert wt.is_dir()

    # Dry-run reports would_remove without mutating caches
    dry = module.prune_merged_worktrees(repo, dry_run=True)
    assert len(dry["pruned"]) == 1
    assert dry["pruned"][0]["action"] == "would_remove"
    assert dry["pruned"][0]["cleanedIgnoredRuntime"] is True
    assert (wt / ".venv" / "pyvenv.cfg").is_file()

    # CLI execution with --include-ignored-runtime removes caches and prunes without --force
    exit_code = module.main(["--repo", str(repo), "--include-ignored-runtime", "--json"])
    assert exit_code == 0
    assert not wt.exists()
    assert not any("--force" in args or "-f" in args for args in calls if args[:2] == ("worktree", "remove"))
    branch_check = subprocess.run(
        ["git", "-C", str(repo), "show-ref", "--verify", "--quiet", f"refs/heads/{branch}"],
        check=False,
    )
    assert branch_check.returncode != 0


def test_canonical_worktree_preserves_unknown_ignored_files_like_dotenv_and_snapshots(tmp_path):
    repo, wt, branch, head, _ = _canonical_merged_fixture(tmp_path, ticket="ticket-011", slug="dotenv", phase="released")
    _populate_ignored_runtime_caches(wt)
    dotenv = wt / ".env"
    dotenv.write_text("SECRET_TOKEN=keep-me\n")

    report = prune_merged_worktrees(repo)
    assert not report["pruned"]
    assert dotenv.read_text() == "SECRET_TOKEN=keep-me\n"
    assert _git(repo, "rev-parse", f"refs/heads/{branch}") == head

    dotenv.unlink()
    snap = wt / ".subactor" / "snapshots" / "recovery.json"
    snap.parent.mkdir(parents=True)
    snap.write_text('{"snapshot":true}\n')
    report2 = prune_merged_worktrees(repo)
    assert not report2["pruned"]
    assert snap.is_file()

    snap.unlink()
    snap.parent.rmdir()
    report3 = prune_merged_worktrees(repo)
    assert len(report3["pruned"]) == 1
    assert not wt.exists()


def test_canonical_worktree_requires_terminal_unlocked_lease(tmp_path):
    import json
    repo, wt, _, _, lease_path = _canonical_merged_fixture(tmp_path, ticket="ticket-012", slug="lease-gate", phase="claimed")
    _populate_ignored_runtime_caches(wt)

    for non_terminal in ("claimed", "editing", "validating", "publication_frozen"):
        data = json.loads(lease_path.read_text())
        data["phase"] = non_terminal
        data["publicationFrozen"] = non_terminal == "publication_frozen"
        lease_path.write_text(json.dumps(data))
        report = prune_merged_worktrees(repo)
        assert not report["pruned"]
        assert wt.is_dir()

    # Missing lease also refuses ignored-runtime cleanup
    saved = lease_path.read_bytes()
    lease_path.unlink()
    assert not prune_merged_worktrees(repo)["pruned"]
    assert wt.is_dir()

    # Terminal 'merged' lease while unlocked succeeds
    data = json.loads(saved)
    data["phase"] = "merged"
    data["publicationFrozen"] = False
    lease_path.write_text(json.dumps(data))
    if sys.platform != "win32":
        import fcntl
        lock_file = lease_path.with_name(lease_path.name + ".lock")
        with lock_file.open("w") as held:
            fcntl.flock(held, fcntl.LOCK_EX | fcntl.LOCK_NB)
            locked_report = prune_merged_worktrees(repo)
            assert not locked_report["pruned"]
            assert wt.is_dir()

    final_report = prune_merged_worktrees(repo)
    assert len(final_report["pruned"]) == 1
    assert not wt.exists()


def test_canonical_worktree_with_active_process_cwd_or_git_lock_is_preserved(tmp_path):
    repo, wt, _, _, _ = _canonical_merged_fixture(tmp_path, ticket="ticket-013", slug="busy-proc", phase="released")
    _populate_ignored_runtime_caches(wt)

    if sys.platform.startswith("linux") and Path("/proc").is_dir():
        sleeper = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"], cwd=str(wt))
        try:
            busy_report = prune_merged_worktrees(repo)
            assert not busy_report["pruned"]
            assert any("active process" in item["reason"] for item in busy_report["skipped"])
            assert wt.is_dir()
        finally:
            sleeper.terminate()
            sleeper.wait(timeout=5)

    _git(repo, "worktree", "lock", str(wt))
    locked_report = prune_merged_worktrees(repo)
    assert not locked_report["pruned"]
    assert any("locked" in item["reason"] for item in locked_report["skipped"])
    assert wt.is_dir()

    _git(repo, "worktree", "unlock", str(wt))
    clean_report = prune_merged_worktrees(repo)
    assert len(clean_report["pruned"]) == 1
    assert not wt.exists()


def test_prune_holds_exclusive_lease_lock_and_aborts_on_mid_flight_lease_mutation(tmp_path, monkeypatch):
    import json
    import scripts.prune_merged_worktrees as prune_mod

    repo, wt, _, _, lease_path = _canonical_merged_fixture(
        tmp_path, ticket="ticket-014", slug="fenced-prune", phase="released"
    )
    _populate_ignored_runtime_caches(wt)
    lock_file = lease_path.with_name(lease_path.name + ".lock")

    # Dry-run must remain strictly read-only and never create a .json.lock file.
    dry = prune_merged_worktrees(repo, dry_run=True)
    assert len(dry["pruned"]) == 1
    assert not lock_file.exists()

    # Simulate a mid-flight uncooperative lease reactivation during runtime cleanup;
    # exact-inode/content CAS revalidation must abort BEFORE git worktree remove runs.
    original_remove_entry = prune_mod._remove_anchored_runtime_entry
    remove_git_calls: list[tuple[str, ...]] = []
    original_git_cmd = prune_mod.git_cmd

    def tracking_git_cmd(cwd: Path, *args: str):
        if len(args) >= 2 and args[0] == "worktree" and args[1] == "remove":
            remove_git_calls.append(args)
        return original_git_cmd(cwd, *args)

    mutated_once = False

    def racing_remove_entry(worktree: Path, rel_entry: str) -> None:
        nonlocal mutated_once
        original_remove_entry(worktree, rel_entry)
        if not mutated_once:
            mutated_once = True
            reactivated = json.loads(lease_path.read_text(encoding="utf-8"))
            reactivated["phase"] = "claimed"
            lease_path.write_text(json.dumps(reactivated), encoding="utf-8")

    monkeypatch.setattr(prune_mod, "git_cmd", tracking_git_cmd)
    monkeypatch.setattr(prune_mod, "_remove_anchored_runtime_entry", racing_remove_entry)

    raced_report = prune_merged_worktrees(repo)
    assert not raced_report["pruned"]
    assert not remove_git_calls
    assert wt.is_dir()
    assert any("claimed" in item["reason"] or "changed" in item["reason"] for item in raced_report["skipped"])

    # Restore terminal lease and verify exclusive flock is held DURING git worktree remove.
    settled = json.loads(lease_path.read_text(encoding="utf-8"))
    settled["phase"] = "released"
    lease_path.write_text(json.dumps(settled), encoding="utf-8")
    _populate_ignored_runtime_caches(wt)
    monkeypatch.setattr(prune_mod, "_remove_anchored_runtime_entry", original_remove_entry)

    observed_exclusive_lock = False
    if sys.platform != "win32":
        import fcntl

        def asserting_git_cmd(cwd: Path, *args: str):
            nonlocal observed_exclusive_lock
            if len(args) >= 2 and args[0] == "worktree" and args[1] == "remove":
                with lock_file.open("r") as probe:
                    try:
                        fcntl.flock(probe, fcntl.LOCK_SH | fcntl.LOCK_NB)
                    except BlockingIOError:
                        observed_exclusive_lock = True
            return original_git_cmd(cwd, *args)

        monkeypatch.setattr(prune_mod, "git_cmd", asserting_git_cmd)

    ok_report = prune_merged_worktrees(repo)
    assert len(ok_report["pruned"]) == 1
    assert not wt.exists()
    if sys.platform != "win32":
        assert observed_exclusive_lock is True


def test_self_ignoring_runtime_cache_contents_are_disposable(tmp_path):
    """ruff-style caches carry their own ``*`` ignore file, so Git lists their contents.

    The listed entries sit below an allowlisted root and must not make the
    released, merged checkout look dirty forever.
    """
    repo, wt, branch, _, _ = _canonical_merged_fixture(tmp_path, ticket="ticket-012", slug="self-ignoring")
    cache = wt / ".hypothesis"
    (cache / "examples" / "ab").mkdir(parents=True)
    (cache / ".gitignore").write_text("# Automatically created by a cache tool.\n*\n")
    (cache / "CACHEDIR.TAG").write_text("Signature: 8a477f597d28d172789f06886806bc55\n")
    (cache / "examples" / "ab" / "entry").write_bytes(b"example")
    listed = _git(wt, "status", "--porcelain=v1", "--untracked-files=all", "--ignored=matching")
    assert "!! .hypothesis/.gitignore" in listed

    report = prune_merged_worktrees(repo)
    assert [entry["action"] for entry in report["pruned"]] == ["removed"]
    assert report["pruned"][0]["cleanedIgnoredRuntime"] is True
    assert not wt.exists()
    assert subprocess.run(["git", "-C", str(repo), "show-ref", "--verify", "--quiet", f"refs/heads/{branch}"],
                          check=False).returncode != 0


def test_nested_entries_follow_their_runtime_root(tmp_path):
    from scripts.prune_merged_worktrees import is_safe_ignored_runtime_path
    for rel in (".ruff_cache/.gitignore", ".ruff_cache/0.17.3/", ".planfile/sprints/",
                ".subactor/receipts/work-start/", ".subactor/cache/autonomy-board.md",
                ".pytest_cache/v/cache/nodeids"):
        assert is_safe_ignored_runtime_path(tmp_path, rel), rel
    for rel in (".subactor/snapshots/recovery.json", ".subactor/leases/ticket-1--x.json",
                ".subactor/manifest.json", ".env", "secrets/.ruff_cache/x", ".ruff_cache/../.env",
                "pkg/.planfile/state.json"):
        assert not is_safe_ignored_runtime_path(tmp_path, rel), rel
