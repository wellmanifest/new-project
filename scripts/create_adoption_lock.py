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


PACKAGE_MANIFEST = "governance/package-manifest.json"
MANIFEST_SOURCE = "governance/manifest.default.json"
MANIFEST_BASE_TARGET = ".governance/manifest.base.json"
MANIFEST_TARGET = ".governance/manifest.json"
TARGET_OWNED_MANIFEST_PATHS = {
    ("$schema",),
    ("coordination", "workstreams"),
    ("coordination", "integration", "requiredForPaths"),
    ("delivery", "requiredForImplementation"),
    ("delivery", "publicInterfacePaths"),
}


def git_bytes(root: Path, revision: str, source: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{revision}:{source}"], cwd=root)


def package_files(root: Path, revision: str) -> list[dict[str, object]]:
    try:
        document = json.loads(git_bytes(root, revision, PACKAGE_MANIFEST))
    except json.JSONDecodeError as error:
        raise SystemExit(f"package manifest is not valid JSON: {error}") from error
    if set(document) != {"schema", "files"} or document["schema"] != "new-project.package-manifest/v1":
        raise SystemExit("package manifest must use new-project.package-manifest/v1")
    files = document["files"]
    if not isinstance(files, list) or not files:
        raise SystemExit("package manifest files must be a non-empty array")
    sources: set[str] = set()
    targets: set[str] = set()
    for index, item in enumerate(files):
        if not isinstance(item, dict) or set(item) != {"source", "target", "strategy", "executable"}:
            raise SystemExit(f"package manifest file {index} has invalid fields")
        source = item["source"]
        target = item["target"]
        strategy = item["strategy"]
        executable = item["executable"]
        if not isinstance(source, str) or not isinstance(target, str):
            raise SystemExit(f"package manifest file {index} paths must be strings")
        if any(Path(path).is_absolute() or ".." in Path(path).parts for path in (source, target)):
            raise SystemExit(f"package manifest file {index} paths must be repository-relative")
        if strategy not in {"managed", "seed", "extendable"} or not isinstance(executable, bool):
            raise SystemExit(f"package manifest file {index} has invalid strategy or executable flag")
        if strategy == "extendable" and (
            source != MANIFEST_SOURCE or target != MANIFEST_TARGET or executable
        ):
            raise SystemExit("extendable strategy currently supports only the target governance JSON manifest")
        if target in targets:
            raise SystemExit(f"duplicate package target: {target}")
        sources.add(source)
        targets.add(target)
        try:
            git_bytes(root, revision, source)
        except subprocess.CalledProcessError as error:
            raise SystemExit(f"package source is missing at {revision}: {source}") from error
    if PACKAGE_MANIFEST not in sources:
        raise SystemExit(f"package manifest must manage itself: {PACKAGE_MANIFEST}")
    entries = {str(item["target"]): item for item in files}
    extendable = entries.get(MANIFEST_TARGET)
    if extendable is not None and extendable["strategy"] == "extendable":
        base = entries.get(MANIFEST_BASE_TARGET)
        if base is None or base["strategy"] != "managed" or base["source"] != extendable["source"]:
            raise SystemExit("extendable target manifest requires a managed base from the same source")
    return files


def json_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def load_json_bytes(content: bytes, label: str) -> object:
    try:
        return json.loads(content)
    except json.JSONDecodeError as error:
        raise SystemExit(f"{label} is not valid JSON: {error}") from error


def manifest_projection(content: bytes) -> bytes:
    """Return the standard-owned, canonical portion of a target manifest."""
    document = load_json_bytes(content, "standard manifest")
    if not isinstance(document, dict):
        raise SystemExit("standard manifest must be a JSON object")
    projection = json.loads(json.dumps(document))
    for parts in TARGET_OWNED_MANIFEST_PATHS:
        parent = projection
        for part in parts[:-1]:
            if not isinstance(parent, dict) or part not in parent:
                parent = None
                break
            parent = parent[part]
        if isinstance(parent, dict):
            parent.pop(parts[-1], None)
    return json_bytes(projection)


def extension_error(required: object, candidate: object, path: str = "$") -> str | None:
    if isinstance(required, dict):
        if not isinstance(candidate, dict):
            return f"{path} must remain an object"
        for key, value in required.items():
            if key not in candidate:
                return f"{path}/{key} is required by the managed base"
            error = extension_error(value, candidate[key], f"{path}/{key}")
            if error:
                return error
        return None
    if isinstance(required, list):
        if not isinstance(candidate, list):
            return f"{path} must remain an array"
        for value in required:
            if value not in candidate:
                return f"{path} removed a value required by the managed base"
        return None
    if candidate != required:
        return f"{path} differs from the managed base"
    return None


def merge_projection(previous: object, current: object, target: object, path: str = "$") -> object:
    """Three-way merge managed values while retaining target-owned extensions."""
    error = extension_error(previous, target, path)
    if error:
        raise SystemExit(f"target manifest violates its installed managed base: {error}")
    if isinstance(previous, dict):
        if not isinstance(current, dict) or not isinstance(target, dict):
            if target != previous:
                raise SystemExit(f"managed manifest type change conflicts at {path}")
            return current
        result = json.loads(json.dumps(target))
        for key, value in current.items():
            child_path = f"{path}/{key}"
            if key in previous:
                result[key] = merge_projection(previous[key], value, target[key], child_path)
            elif key not in target:
                result[key] = json.loads(json.dumps(value))
            else:
                error = extension_error(value, target[key], child_path)
                if error:
                    raise SystemExit(f"new managed manifest value conflicts with target extension: {error}")
        return result
    if isinstance(previous, list):
        if not isinstance(current, list) or not isinstance(target, list):
            if target != previous:
                raise SystemExit(f"managed manifest type change conflicts at {path}")
            return current
        result = json.loads(json.dumps(target))
        for value in current:
            if value not in result:
                result.append(json.loads(json.dumps(value)))
        return result
    return json.loads(json.dumps(current))


def existing_manifest_base(target_root: Path) -> bytes | None:
    """Load a trusted installed base or authenticated legacy target projection."""
    base_path = target_root / MANIFEST_BASE_TARGET
    lock_path = target_root / ".governance/manifest.lock.json"
    if not lock_path.is_file():
        return None
    lock = load_json_bytes(lock_path.read_bytes(), "existing governance lock")
    if not isinstance(lock, dict) or not isinstance(lock.get("managedFiles"), dict):
        raise SystemExit("existing governance lock has invalid managedFiles")
    managed = lock["managedFiles"]
    if base_path.is_file():
        expected = managed.get(MANIFEST_BASE_TARGET)
        actual = hashlib.sha256(base_path.read_bytes()).hexdigest()
        if expected != actual:
            raise SystemExit("installed manifest base differs from its governance lock")
        return base_path.read_bytes()

    manifest_path = target_root / MANIFEST_TARGET
    expected = managed.get(MANIFEST_TARGET)
    actual = hashlib.sha256(manifest_path.read_bytes()).hexdigest() if manifest_path.is_file() else None
    standard = lock.get("standard")
    revision = standard.get("sourceRevision") if isinstance(standard, dict) else None
    if expected != actual or not isinstance(revision, str) or re.fullmatch(r"[0-9a-f]{40}", revision) is None:
        return None
    return manifest_projection(manifest_path.read_bytes())


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
    managed_targets: set[str],
) -> bytes:
    """Build the lock from expected payloads without requiring prior writes."""
    managed_hashes: dict[str, str] = {}
    for target in sorted(managed_targets):
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
    executable_targets: set[str],
) -> list[tuple[str, str]]:
    """Return deterministic (action, path) entries for adoption drift."""
    changes: list[tuple[str, str]] = []
    for target, content in sorted(payloads.items()):
        path = target_root / target
        if not path.exists():
            changes.append(("CREATE", target))
        elif path.read_bytes() != content:
            changes.append(("UPDATE", target))
        elif target in executable_targets and not os.access(path, os.X_OK):
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

    files = package_files(standard_root, args.source_revision)
    managed_targets = {
        str(item["target"]) for item in files if item["strategy"] == "managed"
    }
    executable_targets = {
        str(item["target"]) for item in files if item["executable"]
    }
    previous_base = existing_manifest_base(target_root)
    payloads: dict[str, bytes] = {}
    for item in files:
        target = str(item["target"])
        strategy = str(item["strategy"])
        source_content = git_bytes(standard_root, args.source_revision, str(item["source"]))
        if target == MANIFEST_BASE_TARGET:
            source_content = manifest_projection(source_content)
        target_path = target_root / target
        if strategy == "extendable" and not target_path.exists():
            payloads[target] = json_bytes(load_json_bytes(source_content, "standard manifest"))
        elif strategy == "managed" or not target_path.exists():
            payloads[target] = source_content
        elif strategy == "extendable":
            current_base = manifest_projection(source_content)
            target_document = load_json_bytes(target_path.read_bytes(), "target manifest")
            if previous_base is None:
                base_document = load_json_bytes(current_base, "managed manifest base")
                error = extension_error(base_document, target_document)
                if error:
                    raise SystemExit(f"target manifest does not extend the managed base: {error}")
                payloads[target] = target_path.read_bytes()
            else:
                payloads[target] = json_bytes(merge_projection(
                    load_json_bytes(previous_base, "previous managed manifest base"),
                    load_json_bytes(current_base, "current managed manifest base"),
                    target_document,
                ))
    manifest_path = target_root / ".governance/manifest.json"

    manifest_content = payloads.get(
        MANIFEST_TARGET,
        manifest_path.read_bytes() if manifest_path.exists() else b"",
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
        managed_targets,
    )
    changes = planned_changes(target_root, payloads, expected_lock, executable_targets)

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
        raise SystemExit(f"adoption files differ; rerun with --upgrade after review: {', '.join(sorted(conflicts))}")

    for target, content in sorted(payloads.items()):
        path = target_root / target
        if not path.exists() or path.read_bytes() != content:
            atomic_write(path, content, 0o755 if target in executable_targets else None)
        elif target in executable_targets and not os.access(path, os.X_OK):
            os.chmod(path, 0o755)
    atomic_write(
        target_root / ".governance/manifest.lock.json",
        expected_lock,
    )
    print(f"adopted wellmanifest/new-project {version} at {args.source_revision}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
