#!/usr/bin/env python3
"""Adopt an immutable new-project governance revision into a target repository."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile


MANAGED_SOURCES = {
    "template/files/AGENTS.template.md": "AGENTS.md",
    "project.sh": "project.sh",
    "project.bat": "project.bat",
    "governance/approval-evidence.schema.json": ".governance/approval-evidence.schema.json",
    "governance/diagnostics.json": ".governance/diagnostics.json",
    "scripts/governance_check.py": ".governance/governance_check.py",
    "governance/intent.schema.json": ".governance/intent.schema.json",
    "governance/lock.schema.json": ".governance/lock.schema.json",
    "governance/manifest.schema.json": ".governance/manifest.schema.json",
    "governance/stack-profiles.json": ".governance/stack-profiles.json",
    "project/governance-check.sh": "project/governance-check.sh",
    "project/governance-check.bat": "project/governance-check.bat",
    "project/new-ticket.sh": "project/new-ticket.sh",
    "project/readme.sh": "project/readme.sh",
}
EXECUTABLE_TARGETS = {
    "project.sh",
    "project/governance-check.sh",
    "project/new-ticket.sh",
    "project/readme.sh",
}


def git_bytes(root: Path, revision: str, source: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{revision}:{source}"], cwd=root)


def atomic_write(path: Path, content: bytes, mode: int | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        if mode is not None:
            os.chmod(temporary, mode)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def lock_content(
    target_root: Path,
    revision: str,
    version: str,
    payloads: dict[str, bytes],
) -> bytes:
    """Build the lock from expected payloads without requiring prior writes."""
    managed_targets = sorted({*MANAGED_SOURCES.values(), ".governance/manifest.json"})
    managed_hashes: dict[str, str] = {}
    for target in managed_targets:
        content = payloads.get(target)
        if content is None:
            content = (target_root / target).read_bytes()
        managed_hashes[target] = hashlib.sha256(content).hexdigest()

    lock = {
        "schema": "new-project.lock/v1",
        "standard": {
            "id": "wellmanifest/new-project",
            "version": version,
            "sourceRepository": "wellmanifest/new-project",
            "sourceRevision": revision,
            "publicationStatus": "published",
        },
        "managedFiles": managed_hashes,
    }
    return (json.dumps(lock, indent=2, sort_keys=True) + "\n").encode()


def planned_changes(
    target_root: Path,
    payloads: dict[str, bytes],
    expected_lock: bytes,
) -> list[tuple[str, str]]:
    """Return deterministic (action, path) entries for adoption drift."""
    changes: list[tuple[str, str]] = []
    for target, content in sorted(payloads.items()):
        path = target_root / target
        if not path.exists():
            changes.append(("CREATE", target))
        elif path.read_bytes() != content:
            changes.append(("UPDATE", target))
        elif target in EXECUTABLE_TARGETS and not os.access(path, os.X_OK):
            changes.append(("CHMOD", target))

    lock_target = ".governance/manifest.lock.json"
    lock_path = target_root / lock_target
    if not lock_path.exists():
        changes.append(("CREATE", lock_target))
    elif lock_path.read_bytes() != expected_lock:
        changes.append(("UPDATE", lock_target))
    return changes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target-root", required=True)
    parser.add_argument("--source-revision", required=True)
    parser.add_argument("--upgrade", action="store_true", help="Replace differing standard-managed files")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Report adoption drift and planned changes without writing files",
    )
    args = parser.parse_args()

    if args.check and args.upgrade:
        parser.error("--check and --upgrade are mutually exclusive")

    if re.fullmatch(r"[0-9a-f]{40}", args.source_revision) is None:
        parser.error("--source-revision must be a full lowercase 40-character commit SHA")
    standard_root = Path(__file__).resolve().parent.parent
    target_root = Path(args.target_root).resolve()
    subprocess.run(
        ["git", "cat-file", "-e", f"{args.source_revision}^{{commit}}"],
        cwd=standard_root,
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    payloads = {
        target: git_bytes(standard_root, args.source_revision, source)
        for source, target in MANAGED_SOURCES.items()
    }
    manifest_path = target_root / ".governance/manifest.json"
    if not manifest_path.exists():
        payloads[".governance/manifest.json"] = git_bytes(
            standard_root, args.source_revision, "governance/manifest.default.json"
        )

    manifest_content = (
        manifest_path.read_bytes()
        if manifest_path.exists()
        else payloads[".governance/manifest.json"]
    )
    try:
        manifest = json.loads(manifest_content)
    except json.JSONDecodeError as error:
        raise SystemExit(f"target manifest is not valid JSON: {error}") from error
    version = git_bytes(standard_root, args.source_revision, "VERSION").decode().strip()
    if manifest.get("standard", {}).get("version") != version:
        raise SystemExit(f"target manifest version must equal adopted standard version {version}")

    expected_lock = lock_content(
        target_root,
        args.source_revision,
        version,
        payloads,
    )
    changes = planned_changes(target_root, payloads, expected_lock)

    if args.check:
        if not changes:
            print(f"up-to-date wellmanifest/new-project {version} at {args.source_revision}")
            return 0
        for action, target in changes:
            print(f"{action} {target}")
        print(f"drift detected: {len(changes)} change(s) required")
        return 1

    conflicts = [
        target for target, content in payloads.items()
        if (target_root / target).exists() and (target_root / target).read_bytes() != content
    ]
    if conflicts and not args.upgrade:
        raise SystemExit(f"managed files differ; rerun with --upgrade after review: {', '.join(sorted(conflicts))}")

    for target, content in sorted(payloads.items()):
        path = target_root / target
        if not path.exists() or path.read_bytes() != content:
            atomic_write(path, content, 0o755 if target in EXECUTABLE_TARGETS else None)
        elif target in EXECUTABLE_TARGETS and not os.access(path, os.X_OK):
            os.chmod(path, 0o755)
    atomic_write(
        target_root / ".governance/manifest.lock.json",
        expected_lock,
    )
    print(f"adopted wellmanifest/new-project {version} at {args.source_revision}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
