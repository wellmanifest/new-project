#!/usr/bin/env python3
"""Prune clean integrated checkouts while preserving changed or declined refs.

The caller must separately verify ownership, released writers and cleanup
permission. Git removal releases only the exact checkout registration. Branch
cleanup verifies the integration target and expected branch tip atomically;
this helper never forces deletion or globally prunes other registrations.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import stat
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

CANONICAL_WORKTREE_RE = re.compile(r"^(ticket-([0-9]{3,}))--([a-z0-9]+(?:-[a-z0-9]+)*)$")
TERMINAL_LEASE_PHASES = frozenset({"released", "merged", "closed"})
SAFE_TOP_LEVEL_RUNTIME_NAMES = frozenset({
    ".venv",
    "venv",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".hypothesis",
    ".tox",
    ".nox",
    ".planfile",
    ".coverage",
    "htmlcov",
    "node_modules",
    "build",
    "dist",
})
SAFE_SUBACTOR_RUNTIME_DIRS = frozenset({"cache", "sessions", "recovery", "receipts"})


def git_cmd(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(cwd), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def get_worktrees(repo: Path) -> list[dict[str, str]]:
    res = git_cmd(repo, "worktree", "list", "--porcelain")
    if res.returncode != 0:
        raise RuntimeError(f"git worktree list failed: {res.stderr}")

    worktrees: list[dict[str, str]] = []
    current: dict[str, str] = {}
    for line in res.stdout.splitlines():
        line = line.strip()
        if not line:
            if current:
                worktrees.append(current)
                current = {}
            continue
        parts = line.split(" ", 1)
        key = parts[0]
        val = parts[1] if len(parts) > 1 else ""
        current[key] = val
    if current:
        worktrees.append(current)
    return worktrees


def is_worktree_clean(path: Path) -> bool:
    # Ignored files may contain unique data, so retain their checkout unless
    # separately proven disposable under a terminal canonical lease.
    res = git_cmd(path, "status", "--porcelain", "--untracked-files=all", "--ignored=matching")
    return res.returncode == 0 and not res.stdout.strip()


def is_ancestor(repo: Path, commit: str, target: str) -> bool:
    res = git_cmd(repo, "merge-base", "--is-ancestor", commit, target)
    return res.returncode == 0


def _commit(repo: Path, ref: str) -> str | None:
    result = git_cmd(repo, "rev-parse", "--verify", ref + "^{commit}")
    value = result.stdout.strip()
    if result.returncode == 0 and re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", value):
        return value
    return None


def _target(repo: Path, name: str) -> tuple[str, str, str]:
    if name.startswith(("refs/heads/", "refs/remotes/")):
        candidates = [(name, name)]
    elif name.startswith("origin/"):
        candidates = [(name, "refs/remotes/" + name)]
    else:
        candidates = [("origin/" + name, "refs/remotes/origin/" + name),
                      (name, "refs/heads/" + name)]
    for display, full in candidates:
        if full.startswith("refs/remotes/") and "/" not in full.removeprefix("refs/remotes/"):
            continue
        if git_cmd(repo, "check-ref-format", full).returncode != 0:
            continue
        if git_cmd(repo, "symbolic-ref", "--quiet", full).returncode == 0:
            raise ValueError("Target must identify a direct branch reference, not a symbolic alias")
        sha = _commit(repo, full)
        if sha is not None:
            return display, full, sha
    raise ValueError(f"Target branch '{name}' not found in {repo}")


def _checkout_matches(path: Path, head: str, branch: str) -> bool:
    if _commit(path, "HEAD") != head:
        return False
    symbolic = git_cmd(path, "symbolic-ref", "--quiet", "HEAD")
    if symbolic.returncode not in (0, 1):
        return False
    return (symbolic.stdout.strip() if symbolic.returncode == 0 else "") == branch


def _no_symlink_components(path: Path) -> bool:
    absolute = Path(os.path.abspath(path))
    if not absolute.is_absolute():
        return False
    current = Path(absolute.anchor)
    try:
        for part in absolute.parts[1:]:
            current = current / part
            st = current.lstat()
            if stat.S_ISLNK(st.st_mode):
                return False
    except OSError:
        return False
    return True


def _is_canonical_worktree(primary: Path, path: Path) -> tuple[bool, str | None]:
    abs_primary = Path(os.path.abspath(primary))
    abs_path = Path(os.path.abspath(path))
    if abs_path.parent != abs_primary / ".worktrees":
        return False, None
    match = CANONICAL_WORKTREE_RE.fullmatch(abs_path.name)
    if match is None:
        return False, None
    if not _no_symlink_components(abs_primary) or not _no_symlink_components(abs_path):
        return False, None
    return True, match.group(1)


def _check_terminal_lease(primary: Path, worktree_id: str, ticket_id: str) -> tuple[bool, str]:
    lease_dir = Path(os.path.abspath(primary)) / ".subactor" / "leases"
    lease_path = lease_dir / f"{worktree_id}.json"
    if not os.path.lexists(lease_path):
        return False, "terminal lease required"
    if not _no_symlink_components(lease_dir):
        return False, "unsafe lease directory"
    try:
        st = lease_path.lstat()
        if not stat.S_ISREG(st.st_mode):
            return False, "lease must be a regular file"
        if os.name == "posix" and hasattr(os, "O_NOFOLLOW"):
            lock_path = lease_dir / f"{worktree_id}.json.lock"
            if os.path.lexists(lock_path):
                import fcntl
                lock_st = lock_path.lstat()
                if not stat.S_ISREG(lock_st.st_mode):
                    return False, "unsafe lease lock"
                lock_fd = os.open(str(lock_path), os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
                try:
                    try:
                        fcntl.flock(lock_fd, fcntl.LOCK_SH | fcntl.LOCK_NB)
                    except BlockingIOError:
                        return False, "lease lock active"
                    fcntl.flock(lock_fd, fcntl.LOCK_UN)
                finally:
                    os.close(lock_fd)
            fd = os.open(str(lease_path), os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
            with os.fdopen(fd, "rb") as stream:
                raw = stream.read(65537)
        else:
            raw = lease_path.read_bytes()
        if len(raw) > 65536:
            return False, "lease exceeds bounded size"
        lease = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return False, "lease unreadable"
    if not isinstance(lease, dict):
        return False, "lease invalid"
    if lease.get("worktreeId") != worktree_id or lease.get("ticketId") != ticket_id:
        return False, "lease binding mismatch"
    phase = lease.get("phase")
    if lease.get("publicationFrozen") is not False or phase not in TERMINAL_LEASE_PHASES:
        return False, f"lease phase is {phase!r}"
    return True, "ok"


def _link_inside(raw: str, target: Path, prefix: str) -> bool:
    value = raw.removesuffix(" (deleted)")
    if value == prefix or (value.startswith(prefix) and value[len(prefix)] == "/"):
        return True
    if value.startswith("/") and ("//" in value or "/./" in value or value.endswith("/.")):
        try:
            Path(value).relative_to(target)
            return True
        except ValueError:
            return False
    return False


def _worktree_in_use(path: Path, *, proc_root: Path = Path("/proc")) -> str | None:
    git_dir_res = git_cmd(path, "rev-parse", "--path-format=absolute", "--git-dir")
    if git_dir_res.returncode != 0 or not git_dir_res.stdout.strip():
        return "worktree git metadata unavailable"
    git_dir = Path(git_dir_res.stdout.strip())
    for lock_name in ("locked", "index.lock", "HEAD.lock"):
        if os.path.lexists(git_dir / lock_name):
            return f"worktree {lock_name} present"
    if os.name != "posix" or not proc_root.is_dir():
        return None
    target = Path(os.path.abspath(path))
    prefix = str(target)
    self_pid = os.getpid()
    try:
        proc_entries = list(proc_root.iterdir())
    except OSError:
        return None
    for entry in proc_entries:
        if not entry.name.isdigit():
            continue
        pid = int(entry.name)
        if pid == self_pid:
            continue
        candidates = [entry / "cwd", entry / "exe"]
        try:
            candidates.extend((entry / "fd").iterdir())
        except OSError:
            pass
        for link in candidates:
            try:
                dest = os.readlink(link)
            except OSError:
                continue
            if _link_inside(dest, target, prefix):
                return f"worktree in use by active process (pid {pid})"
    return None


def is_safe_ignored_runtime_path(worktree: Path, relpath: str) -> bool:
    if (
        not relpath
        or relpath.startswith("/")
        or "\\" in relpath
        or "\0" in relpath
    ):
        return False
    clean = relpath.rstrip("/")
    if not clean:
        return False
    parts = clean.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        return False
    top = parts[0]
    leaf = parts[-1]
    if len(parts) == 1 and (
        top in SAFE_TOP_LEVEL_RUNTIME_NAMES
        or top.startswith(".coverage.")
        or top.endswith(".egg-info")
    ):
        return True
    if leaf == "__pycache__" or leaf.endswith((".pyc", ".pyo")):
        return True
    if leaf.endswith(".egg-info") and len(parts) <= 3:
        return True
    if len(parts) == 2 and top == ".subactor" and leaf in SAFE_SUBACTOR_RUNTIME_DIRS:
        return True
    if clean == ".subactor":
        subactor_dir = worktree / ".subactor"
        try:
            st = subactor_dir.lstat()
            if not stat.S_ISDIR(st.st_mode):
                return False
            children = [item.name for item in subactor_dir.iterdir()]
        except OSError:
            return False
        return bool(children) and set(children) <= SAFE_SUBACTOR_RUNTIME_DIRS
    return False


def _inspect_ignored_runtime_only(path: Path) -> tuple[bool, list[str]]:
    res = git_cmd(path, "status", "--porcelain=v1", "-z", "--untracked-files=all", "--ignored=matching")
    if res.returncode != 0:
        return False, []
    tokens = [tok for tok in res.stdout.split("\0") if tok]
    if not tokens:
        return True, []
    entries: list[str] = []
    for tok in tokens:
        if not tok.startswith("!! "):
            return False, []
        rel = tok[3:]
        if not is_safe_ignored_runtime_path(path, rel):
            return False, []
        entries.append(rel.rstrip("/"))
    return True, entries


def _rmtree_at(parent_fd: int, name: str) -> None:
    flags = os.O_RDONLY | os.O_DIRECTORY | getattr(os, "O_NOFOLLOW", 0)
    dir_fd = os.open(name, flags, dir_fd=parent_fd)
    try:
        try:
            os.fchmod(dir_fd, 0o700)
        except OSError:
            pass
        for child in os.listdir(dir_fd):
            child_st = os.stat(child, dir_fd=dir_fd, follow_symlinks=False)
            if stat.S_ISDIR(child_st.st_mode):
                _rmtree_at(dir_fd, child)
            else:
                os.unlink(child, dir_fd=dir_fd)
    finally:
        os.close(dir_fd)
    os.rmdir(name, dir_fd=parent_fd)


def _remove_anchored_runtime_entry(worktree: Path, rel_entry: str) -> None:
    if os.name != "posix" or not hasattr(os, "O_NOFOLLOW"):
        import shutil
        target = worktree / rel_entry
        if not os.path.lexists(target):
            return
        st = target.lstat()
        if stat.S_ISDIR(st.st_mode):
            shutil.rmtree(target)
        else:
            target.unlink()
        return
    parts = [part for part in rel_entry.split("/") if part]
    if not parts or any(part in {".", ".."} for part in parts):
        raise ValueError(f"Unsafe runtime path: {rel_entry}")
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    fds = [os.open(str(Path(os.path.abspath(worktree))), flags)]
    try:
        for part in parts[:-1]:
            fds.append(os.open(part, flags, dir_fd=fds[-1]))
        parent_fd = fds[-1]
        leaf = parts[-1]
        try:
            st = os.stat(leaf, dir_fd=parent_fd, follow_symlinks=False)
        except FileNotFoundError:
            return
        if stat.S_ISDIR(st.st_mode):
            _rmtree_at(parent_fd, leaf)
        else:
            os.unlink(leaf, dir_fd=parent_fd)
    finally:
        for fd in reversed(fds):
            os.close(fd)


def _delete_exact_branch(
    repo: Path, branch: str, head: str, target: str, target_sha: str,
) -> subprocess.CompletedProcess[str]:
    # Prepare locks both exact names and verifies their expected OIDs. Inspect
    # their direct/symbolic type while those locks are held, before committing.
    command = ["git", "-C", str(repo), "update-ref", "--no-deref", "--stdin"]
    transaction = (f"start\nverify {target} {target_sha}\n"
                   f"delete {branch} {head}\nprepare\n")
    with tempfile.TemporaryFile(mode="w+t", encoding="utf-8", errors="replace") as errors:
        try:
            process = subprocess.Popen(
                command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                stderr=errors, text=True, encoding="utf-8", errors="replace",
            )
        except OSError as error:
            return subprocess.CompletedProcess(command, 1, "", str(error))
        prefix = ""
        output = ""
        declined = None
        try:
            process.stdin.write(transaction)
            process.stdin.flush()
            prefix = process.stdout.readline() + process.stdout.readline()
            if prefix != "start: ok\nprepare: ok\n":
                declined = "reference transaction preparation failed"
            else:
                for ref in (target, branch):
                    if git_cmd(repo, "symbolic-ref", "--quiet", ref).returncode != 1:
                        declined = "reference became symbolic or could not be verified under lock"
                        break
            if not declined:
                try:
                    if any(item.get("branch") == branch for item in get_worktrees(repo)):
                        declined = "branch remains checked out elsewhere"
                except RuntimeError as error:
                    declined = f"could not verify other checkout registrations: {error}"
            if process.poll() is None:
                process.stdin.write("abort\n" if declined else "commit\n")
                process.stdin.flush()
            output, _ = process.communicate()
        except (OSError, ValueError) as error:
            declined = f"reference transaction outcome unconfirmed: {error}"
        finally:
            if process.poll() is None or (process.stdout and not process.stdout.closed):
                if process.poll() is None:
                    try:
                        process.stdin.write("abort\n")
                        process.stdin.flush()
                    except (OSError, ValueError):
                        pass
                try:
                    remaining, _ = process.communicate(timeout=5)
                    output += remaining or ""
                except subprocess.TimeoutExpired:
                    if process.poll() is None:
                        process.kill()
                        process.wait(timeout=5)
                    for stream in (process.stdin, process.stdout):
                        if stream and not stream.closed:
                            stream.close()
                    declined = "reference transaction interrupted; reconcile refs before retry"
        errors.seek(0)
        detail = errors.read()
        if declined:
            return subprocess.CompletedProcess(command, 1, prefix + output, declined + ": " + detail)
        if process.returncode == 0 and "commit: ok\n" not in output:
            return subprocess.CompletedProcess(command, 1, prefix + output, "commit outcome unconfirmed: " + detail)
        return subprocess.CompletedProcess(command, process.returncode, prefix + output, detail)


def prune_merged_worktrees(
    repo: Path,
    target_branch: str = "main",
    dry_run: bool = False,
    include_ignored_runtime: bool = True,
) -> dict[str, Any]:
    target_ref, target_full, target_sha = _target(repo, target_branch)
    wts = get_worktrees(repo)
    if not wts:
        return {"pruned": [], "skipped": []}
    primary = Path(wts[0].get("worktree", str(repo)))
    target_name = (target_full.removeprefix("refs/heads/")
                   if target_full.startswith("refs/heads/")
                   else target_full.removeprefix("refs/remotes/").split("/", 1)[1])
    pruned: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    for wt in wts[1:]:
        path = Path(wt.get("worktree", ""))
        head = wt.get("HEAD", "")
        branch = wt.get("branch", "")
        name = branch.removeprefix("refs/heads/") if branch else None

        def skip(reason: str, **extra: Any) -> None:
            skipped.append({"path": str(path), "branch": name, "reason": reason, **extra})

        if not path.exists():
            skip("directory missing")
            continue
        if "locked" in wt:
            skip("worktree locked")
            continue
        if branch and (not branch.startswith("refs/heads/")
                       or git_cmd(repo, "check-ref-format", branch).returncode != 0):
            skip("invalid branch reference")
            continue
        if name == target_name or branch == target_full:
            skip("target branch checkout")
            continue

        clean = is_worktree_clean(path)
        runtime_entries: list[str] = []
        is_canonical, ticket_id = _is_canonical_worktree(primary, path)

        if not clean:
            if not include_ignored_runtime or not is_canonical or ticket_id is None:
                skip("dirty (uncommitted, untracked or ignored data)")
                continue
            only_safe_runtime, runtime_entries = _inspect_ignored_runtime_only(path)
            if not only_safe_runtime or not runtime_entries:
                skip("dirty (uncommitted, untracked or ignored data)")
                continue

        if not is_ancestor(repo, head, target_sha):
            skip(f"not merged into {target_ref}", head=head)
            continue

        if is_canonical and ticket_id is not None:
            lease_file = primary / ".subactor" / "leases" / f"{path.name}.json"
            if runtime_entries or os.path.lexists(lease_file):
                lease_ok, lease_detail = _check_terminal_lease(primary, path.name, ticket_id)
                if not lease_ok:
                    skip(f"ignored runtime data retained ({lease_detail})" if runtime_entries
                         else f"lease not terminal ({lease_detail})")
                    continue
            in_use_reason = _worktree_in_use(path)
            if in_use_reason is not None:
                skip(in_use_reason)
                continue

        if (_commit(repo, target_full) != target_sha
                or not _checkout_matches(path, head, branch)
                or (branch and _commit(repo, branch) != head)):
            skip("checkout, branch or target changed since observation")
            continue
        if dry_run:
            entry: dict[str, Any] = {"path": str(path), "branch": name, "action": "would_remove"}
            if runtime_entries:
                entry["cleanedIgnoredRuntime"] = True
            pruned.append(entry)
            continue

        if runtime_entries:
            try:
                for rel_entry in runtime_entries:
                    _remove_anchored_runtime_entry(path, rel_entry)
            except (OSError, ValueError) as exc:
                skip(f"ignored runtime cleanup failed: {exc}")
                continue
            if (_commit(repo, target_full) != target_sha
                    or not _checkout_matches(path, head, branch)
                    or (branch and _commit(repo, branch) != head)):
                skip("checkout, branch or target changed since observation")
                continue

        # Git also refuses removal if tracked/untracked/non-runtime ignored data
        # appeared after inspection; never turn its refusal into a force removal.
        removed = git_cmd(repo, "worktree", "remove", str(path))
        if removed.returncode != 0:
            skip(f"remove failed: {removed.stderr.strip()}")
            continue
        if branch:
            deleted = _delete_exact_branch(repo, branch, head, target_full, target_sha)
            if deleted.returncode != 0:
                skip(f"branch cleanup declined or unconfirmed: {deleted.stderr.strip()}")
        result_entry: dict[str, Any] = {"path": str(path), "branch": name, "action": "removed"}
        if runtime_entries:
            result_entry["cleanedIgnoredRuntime"] = True
        pruned.append(result_entry)
    return {"target": target_ref, "pruned": pruned, "skipped": skipped}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Prune linked worktrees that are clean and already merged."
    )
    parser.add_argument(
        "--repo",
        type=Path,
        default=Path.cwd(),
        help="Path to repository (default: current directory)",
    )
    parser.add_argument(
        "--target-branch", default="main", help="Target branch to check ancestry against (default: main)"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Report what would be pruned without changing anything"
    )
    parser.add_argument(
        "--include-ignored-runtime",
        "--include-ignored-caches",
        dest="include_ignored_runtime",
        action="store_true",
        default=True,
        help="Allow pruning terminal-leased canonical worktrees containing only allowlisted ignored runtime caches (default)",
    )
    parser.add_argument(
        "--no-include-ignored-runtime",
        dest="include_ignored_runtime",
        action="store_false",
        help="Retain canonical worktrees even when only allowlisted ignored runtime caches remain",
    )
    parser.add_argument("--json", action="store_true", help="Output JSON format")
    args = parser.parse_args(argv)

    try:
        report = prune_merged_worktrees(
            args.repo.resolve(),
            target_branch=args.target_branch,
            dry_run=args.dry_run,
            include_ignored_runtime=args.include_ignored_runtime,
        )
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"Target branch: {report['target']}")
        print(f"Pruned ({len(report['pruned'])}):")
        for item in report["pruned"]:
            print(f"  - {item['path']} ({item.get('branch', 'detached')}) -> {item['action']}")
        print(f"Skipped ({len(report['skipped'])}):")
        for item in report["skipped"]:
            print(f"  - {item['path']} ({item.get('branch', 'detached')}): {item['reason']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
