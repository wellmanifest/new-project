#!/usr/bin/env python3
"""Audit a workspace root for temporary worktrees and duplicate repository clones."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


REPORT_SCHEMA = "new-project.workspace-lifecycle-report/v1"
MAX_REPOSITORIES = 10_000
SCP_REMOTE_RE = re.compile(r"^(?:[^@/]+@)?([^:/]+):(.+)$")


@dataclass(order=True)
class Finding:
    code: str
    severity: str
    message: str
    remediation: str
    evidence: dict[str, Any]


@dataclass(frozen=True)
class Checkout:
    path: Path
    common_git_dir: Path
    identity: str
    head: str
    branch: str | None
    dirty: bool


class AuditError(RuntimeError):
    """The local workspace could not be audited safely."""


def run_git(root: Path, *arguments: str) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), *arguments],
            capture_output=True,
            check=False,
            text=True,
            timeout=15,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise AuditError(f"git failed for {root}: {error}") from error
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        raise AuditError(f"git {' '.join(arguments)} failed for {root}: {detail}")
    return result.stdout.strip()


def local_remote_path(root: Path, remote: str) -> Path | None:
    if remote.startswith("file://"):
        parsed = urlparse(remote)
        return Path(parsed.path).resolve()
    candidate = Path(remote).expanduser()
    if candidate.is_absolute() or remote.startswith(("./", "../")):
        if not candidate.is_absolute():
            candidate = root / candidate
        return candidate.resolve()
    return None


def normalized_network_remote(remote: str) -> str:
    value = remote.strip().rstrip("/")
    parsed = urlparse(value)
    if parsed.scheme and parsed.hostname:
        path = parsed.path.lstrip("/")
        host = parsed.hostname.lower()
    else:
        match = SCP_REMOTE_RE.fullmatch(value)
        if not match:
            return f"remote:{value.removesuffix('.git').lower()}"
        host, path = match.groups()
        host = host.lower()
    return f"remote:{host}/{path.removesuffix('.git').lower()}"


def repository_identity(root: Path, seen: set[Path] | None = None) -> str:
    resolved = root.resolve()
    visited = set() if seen is None else set(seen)
    if resolved in visited:
        raise AuditError(f"local origin cycle detected at {resolved}")
    visited.add(resolved)
    try:
        remote = run_git(resolved, "remote", "get-url", "origin")
    except AuditError as error:
        if "No such remote" not in str(error):
            raise
        return f"local-repository:{resolved}"
    local = local_remote_path(resolved, remote)
    if local is not None and (local / ".git").exists():
        return repository_identity(local, visited)
    if local is not None:
        return f"local:{local}"
    return normalized_network_remote(remote)


def inspect_checkout(path: Path) -> Checkout:
    common = Path(
        run_git(path, "rev-parse", "--path-format=absolute", "--git-common-dir")
    ).resolve()
    head = run_git(path, "rev-parse", "HEAD")
    branch = run_git(path, "branch", "--show-current") or None
    dirty = bool(run_git(path, "status", "--porcelain=v1", "--untracked-files=all"))
    identity = repository_identity(path)
    return Checkout(
        path=path.resolve(),
        common_git_dir=common,
        identity=identity,
        head=head,
        branch=branch,
        dirty=dirty,
    )


def choose_primary(checkouts: list[Checkout]) -> Checkout:
    slug = checkouts[0].identity.rsplit("/", 1)[-1]
    named = [checkout for checkout in checkouts if checkout.path.name.lower() == slug]
    if len(named) == 1:
        return named[0]
    common_owners = [
        checkout
        for checkout in checkouts
        if checkout.common_git_dir == checkout.path / ".git"
    ]
    return sorted(common_owners or checkouts, key=lambda item: str(item.path))[0]


def evaluate(workspace_root: Path, allowed: set[Path]) -> list[Finding]:
    if not workspace_root.is_dir():
        raise AuditError(f"workspace root is not a directory: {workspace_root}")
    candidates = sorted(
        (
            child
            for child in workspace_root.iterdir()
            if child.is_dir() and (child / ".git").exists()
        ),
        key=lambda item: str(item),
    )
    if len(candidates) > MAX_REPOSITORIES:
        raise AuditError(f"workspace contains more than {MAX_REPOSITORIES} repositories")
    checkouts = [inspect_checkout(candidate) for candidate in candidates]
    groups: dict[str, list[Checkout]] = {}
    for checkout in checkouts:
        groups.setdefault(checkout.identity, []).append(checkout)

    findings: list[Finding] = []
    for identity in sorted(groups):
        group = groups[identity]
        if len(group) < 2:
            continue
        primary = choose_primary(group)
        for checkout in sorted(group, key=lambda item: str(item.path)):
            if checkout == primary or checkout.path in allowed:
                continue
            linked = checkout.common_git_dir == primary.common_git_dir
            kind = "linked worktree" if linked else "duplicate clone"
            findings.append(Finding(
                code=(
                    "GOV-WORKSPACE-LIFECYCLE-001"
                    if linked
                    else "GOV-WORKSPACE-LIFECYCLE-002"
                ),
                severity="error",
                message=f"A terminal workspace still contains a {kind}.",
                remediation=(
                    "Verify dirty state and HEAD reachability. Preserve unknown or unique data; "
                    "then remove this exact workspace and its disposable local branch."
                ),
                evidence={
                    "branch": checkout.branch,
                    "dirty": checkout.dirty,
                    "head": checkout.head,
                    "identity": identity,
                    "path": str(checkout.path),
                    "primary": str(primary.path),
                },
            ))
    return sorted(findings)


def report_payload(findings: list[Finding]) -> dict[str, Any]:
    return {
        "schema": REPORT_SCHEMA,
        "status": "passed" if not findings else "failed",
        "summary": {"errors": len(findings), "warnings": 0, "findings": len(findings)},
        "findings": [asdict(item) for item in findings],
    }


def render_text(payload: dict[str, Any]) -> str:
    lines: list[str] = []
    for finding in payload["findings"]:
        evidence = json.dumps(
            finding["evidence"],
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        lines.append(f"{finding['code']} ERROR: {finding['message']} [{evidence}]")
        lines.append(f"  remediation: {finding['remediation']}")
    summary = payload["summary"]
    label = "GOV-WORKSPACE-PASS" if payload["status"] == "passed" else "GOV-WORKSPACE-FAIL"
    lines.append(
        f"{label}: {payload['status']} "
        f"({summary['errors']} errors, {summary['warnings']} warnings)"
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace-root", required=True, type=Path)
    parser.add_argument(
        "--allow",
        action="append",
        default=[],
        type=Path,
        help="Exact active secondary checkout allowed during this non-terminal audit.",
    )
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)

    findings: list[Finding]
    try:
        allowed = {path.expanduser().resolve() for path in args.allow}
        findings = evaluate(args.workspace_root.expanduser().resolve(), allowed)
    except AuditError as error:
        findings = [Finding(
            code="GOV-WORKSPACE-LIFECYCLE-003",
            severity="error",
            message="The local workspace audit could not be completed safely.",
            remediation="Repair repository metadata or narrow the explicit workspace root.",
            evidence={"reason": str(error)},
        )]

    payload = report_payload(findings)
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    else:
        print(render_text(payload))
    return 0 if payload["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
