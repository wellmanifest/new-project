#!/usr/bin/env python3
"""Report how far each adopter has drifted from the published standard.

Every fact here already exists in the workspace: the adoption lock names the
version and revision an adopter accepted, the managed digests say whether its
copy is intact, and its workflows say whether anything runs the gate. Nothing
collects them, so a fleet spread across five minor versions looks healthy from
inside any single repository.

Read-only. Run from the workspace root that holds the sibling repositories.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

HUB = "new-project"
# The validator holds its own per-repository check names. required-checks.json
# names it an external consumer that must read from the repository, so any
# disagreement means the declared source of truth and the operational one have
# drifted apart -- and the consumer is usually the accurate side.
DEFAULT_VALIDATOR_REGISTRY = (
    Path.home() / "github/subactor/validator-agent/config/direct-pr-registry.json"
)
GATE_MARKERS = ("governance_check.py", "governance-check.sh", "governance-check.bat")
HOST_CONTRACT = ".governance/agent-hosts.json"


def git(root: Path, *args: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), *args],
            capture_output=True, text=True, check=False, timeout=20,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return result.stdout.strip() if result.returncode == 0 else None


def released_versions(hub: Path) -> list[str]:
    """Published tags, newest first, so 'releases behind' is a real number."""
    raw = git(hub, "tag", "--list", "v*", "--sort=-v:refname") or ""
    return [line[1:] for line in raw.splitlines() if re.fullmatch(r"v[0-9.]+", line)]


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def repository_name(root: Path) -> str | None:
    url = git(root, "remote", "get-url", "origin")
    if not url:
        return None
    match = re.search(r"[:/]([^/:]+/[^/]+?)(?:\.git)?$", url)
    return match.group(1) if match else None


def digest_drift(root: Path, lock: dict[str, Any]) -> list[str]:
    drifted = []
    for relative, expected in lock.get("managedFiles", {}).items():
        path = root / relative
        if not path.is_file():
            drifted.append(f"{relative}:MISSING")
            continue
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            drifted.append(f"{relative}:DRIFT")
    return drifted


def gate_workflows(root: Path) -> list[str]:
    directory = root / ".github/workflows"
    if not directory.is_dir():
        return []
    found = []
    for workflow in sorted(directory.glob("*.y*ml")):
        try:
            text = workflow.read_text(encoding="utf-8")
        except OSError:
            continue
        if any(marker in text for marker in GATE_MARKERS):
            found.append(workflow.name)
    return found


def required_checks_truth(root: Path, actual_repository: str | None) -> str:
    """The declared SSOT for check names is false when it describes another repo."""
    declaration = load_json(root / ".governance/required-checks.json")
    if declaration is None:
        return "absent"
    declared = declaration.get("repository")
    workflow = declaration.get("workflowFile")
    problems = []
    if actual_repository and declared and declared != actual_repository:
        problems.append(f"claims {declared}")
    if workflow and not (root / workflow).is_file():
        problems.append(f"no {workflow}")
    return "; ".join(problems) if problems else "true"


def validator_registry(path: Path | None) -> dict[str, list[str]]:
    """Absent or unreadable is not an error: the column reports 'unregistered'."""
    if path is None:
        return {}
    document = load_json(path)
    if not isinstance(document, dict):
        return {}
    return {
        name: entry.get("required_checks", [])
        for name, entry in document.get("repositories", {}).items()
        if isinstance(entry, dict)
    }


def checks_agreement(
    root: Path, repository: str | None, registry: dict[str, list[str]]
) -> str:
    if not repository or repository not in registry:
        return "unregistered"
    operational = registry[repository]
    declaration = load_json(root / ".governance/required-checks.json") or {}
    declared = declaration.get("requiredCheckNames")
    if declared is None:
        declared = [check.get("name") for check in declaration.get("requiredChecks", [])]
    return "agree" if sorted(declared or []) == sorted(operational) else "differ"


def inspect(
    root: Path, releases: list[str], registry: dict[str, list[str]]
) -> dict[str, Any] | None:
    lock = load_json(root / ".governance/manifest.lock.json")
    if lock is None:
        return None
    standard = lock.get("standard", {})
    version = standard.get("version")
    try:
        behind = releases.index(version) if version in releases else None
    except ValueError:
        behind = None
    repository = repository_name(root)
    return {
        "repository": root.name,
        "remote": repository,
        "version": version,
        "revision": (standard.get("sourceRevision") or "")[:8],
        "releasesBehind": behind,
        "digestDrift": digest_drift(root, lock),
        "gateWorkflows": gate_workflows(root),
        "hostContract": (root / HOST_CONTRACT).is_file(),
        "requiredChecks": required_checks_truth(root, repository),
        "checksVsValidator": checks_agreement(root, repository, registry),
        "tickets": (
            len(list((root / "project").glob("ticket-*")))
            if (root / "project").is_dir() else 0
        ),
    }


def classify(root: Path) -> str:
    """Three states, because 'not adopted' hides the dangerous middle one."""
    if (root / ".governance/manifest.lock.json").is_file():
        return "adopted"
    if (root / ".governance").is_dir() or (root / "AGENTS.md").is_file():
        return "claimed"  # follows the standard on paper, nothing pins it
    return "outside"


def collect(workspace: Path, registry_path: Path | None = None) -> dict[str, Any]:
    hub = workspace / HUB
    releases = released_versions(hub) if hub.is_dir() else []
    current = releases[0] if releases else None
    registry = validator_registry(registry_path)
    adopters: list[dict[str, Any]] = []
    claimed: list[str] = []
    outside: list[str] = []
    for child in sorted(workspace.iterdir()):
        # Symlinks alias a repository that is already listed under its real name.
        if child.is_symlink() or not child.is_dir() or child.name == HUB:
            continue
        if not (child / ".git").exists():
            continue
        state = classify(child)
        if state == "adopted":
            record = inspect(child, releases, registry)
            if record is not None:
                adopters.append(record)
                continue
            state = "claimed"
        (claimed if state == "claimed" else outside).append(child.name)
    return {
        "schema": "wellmanifest.fleet-report/v1",
        "currentStandard": current,
        "adopters": adopters,
        "claimed": claimed,
        "outside": outside,
    }


def render(report: dict[str, Any]) -> str:
    current = report["currentStandard"] or "unknown"
    rows = report["adopters"]
    width = max((len(r["repository"]) for r in rows), default=10)
    lines = [
        f"wellmanifest fleet report — published standard {current}",
        "",
        f"{'repository':<{width}}  {'adopted':<8} {'behind':>6}  {'drift':<6} "
        f"{'gate in CI':<12} {'hosts':<6} {'vs validator':<13} required-checks",
        "-" * (width + 60),
    ]
    for row in rows:
        behind = "current" if row["releasesBehind"] == 0 else (
            str(row["releasesBehind"]) if row["releasesBehind"] is not None else "?"
        )
        drift = "ok" if not row["digestDrift"] else f"{len(row['digestDrift'])}!"
        gate = ",".join(row["gateWorkflows"]) or "-"
        hosts = "yes" if row["hostContract"] else "-"
        lines.append(
            f"{row['repository']:<{width}}  {row['version'] or '?':<8} {behind:>6}  "
            f"{drift:<6} {gate[:12]:<12} {hosts:<6} "
            f"{row['checksVsValidator']:<13} {row['requiredChecks']}"
        )

    behind_counts = sorted(r["releasesBehind"] for r in rows if r["releasesBehind"] is not None)
    median = behind_counts[len(behind_counts) // 2] if behind_counts else "n/a"
    lines += [
        "",
        f"adopters: {len(rows)}",
        f"on the published standard: {sum(1 for b in behind_counts if b == 0)}",
        f"median releases behind: {median}",
        f"running the gate in CI: {sum(1 for r in rows if r['gateWorkflows'])}",
        f"carrying the host contract: {sum(1 for r in rows if r['hostContract'])}",
        f"with a truthful required-checks declaration: "
        f"{sum(1 for r in rows if r['requiredChecks'] == 'true')}",
        f"managed digest drift: {sum(len(r['digestDrift']) for r in rows)} files",
        f"declaration agreeing with the validator registry: "
        f"{sum(1 for r in rows if r['checksVsValidator'] == 'agree')}",
    ]
    if report["claimed"]:
        lines += [
            "",
            "claimed but not pinned (AGENTS.md or .governance without an adoption lock):",
            f"  {', '.join(report['claimed'])}",
        ]
    if report["outside"]:
        lines += ["", f"outside the standard: {', '.join(report['outside'])}"]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--workspace", default=".", help="Directory holding the sibling repositories"
    )
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument(
        "--validator-registry", default=None,
        help="direct-pr-registry.json to cross-check against; skipped when absent",
    )
    parser.add_argument(
        "--max-releases-behind", type=int, default=None,
        help="Exit non-zero when any adopter is further behind than this",
    )
    args = parser.parse_args(argv or sys.argv[1:])

    registry_path = (
        Path(args.validator_registry).expanduser()
        if args.validator_registry
        else DEFAULT_VALIDATOR_REGISTRY
    )
    report = collect(Path(args.workspace).resolve(), registry_path)
    sys.stdout.write(
        json.dumps(report, indent=2) + "\n" if args.format == "json" else render(report)
    )
    if args.max_releases_behind is None:
        return 0
    worst = max(
        (r["releasesBehind"] for r in report["adopters"] if r["releasesBehind"] is not None),
        default=0,
    )
    return 1 if worst > args.max_releases_behind else 0


if __name__ == "__main__":
    raise SystemExit(main())
