#!/usr/bin/env python3
"""Audit adopted governance instances across a fleet of local checkouts.

Every check here answers one question: does this repository's declared
governance describe *this* repository, or something else? A seed file copied
without adaptation, a required check no workflow publishes, a managed file that
drifted from its own pin, a gate no workflow invokes — each of them reads as
protection while providing none, and each is only visible when the declaration
and the thing it describes are compared side by side.

The rules live in ``governance/fleet-conformance.rules.json`` so that adding a
check is data, not code. This audit is read-only: it opens files, never a
network connection, and never writes to the repositories it inspects.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

SCHEMA = "new-project.fleet-conformance/v1"
REPORT_SCHEMA = "new-project.fleet-conformance-report/v1"
JOB_LINE = re.compile(r"^  ([A-Za-z0-9][A-Za-z0-9_-]*):\s*(?:#.*)?$")
JOB_NAME_LINE = re.compile(r"^    name:\s*(.+?)\s*$")
REMOTE_IDENTITY = re.compile(
    r"(?:git@|https://|ssh://git@)(?:[^/:]+)[/:]([^/]+)/(.+?)(?:\.git)?/?$"
)


def load_rules(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema") != SCHEMA:
        raise SystemExit(f"{path}: unsupported rule schema {data.get('schema')!r}")
    rules = data.get("rules")
    if not isinstance(rules, list) or not rules:
        raise SystemExit(f"{path}: rules must be a non-empty list")
    return rules


def read_json(path: Path) -> dict | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def origin_identity(repo: Path) -> str | None:
    """Resolve owner/name from the origin remote, which is the ground truth.

    A repository's directory name is a local convenience and can be renamed;
    the remote is what every other participant addresses it by.
    """
    try:
        completed = subprocess.run(
            ["git", "-C", str(repo), "remote", "get-url", "origin"],
            capture_output=True, text=True, check=False,
        )
    except OSError:
        return None
    if completed.returncode != 0:
        return None
    match = REMOTE_IDENTITY.match(completed.stdout.strip())
    return f"{match.group(1)}/{match.group(2)}" if match else None


def published_jobs(repo: Path) -> set[str]:
    """Collect the check names every workflow in this repository publishes.

    GitHub shows a job's ``name:`` when it has one and its key otherwise, and
    a ruleset matches on what is shown, so the display name is what counts.
    """
    names: set[str] = set()
    workflows = repo / ".github" / "workflows"
    if not workflows.is_dir():
        return names
    for workflow in sorted(workflows.glob("*.y*ml")):
        try:
            lines = workflow.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeDecodeError):
            continue
        in_jobs = False
        key: str | None = None
        display: str | None = None

        def flush() -> None:
            if key is not None:
                names.add(display or key)

        for line in lines:
            if line.startswith("jobs:"):
                in_jobs = True
                continue
            if not in_jobs:
                continue
            if line and not line.startswith(" ") and not line.startswith("#"):
                break
            match = JOB_LINE.match(line)
            if match:
                flush()
                key, display = match.group(1), None
                continue
            named = JOB_NAME_LINE.match(line)
            if named and key is not None and display is None:
                display = named.group(1).strip().strip("'\"")
        flush()
    return names


def required_names(data: dict) -> list[str]:
    bound = data.get("requiredChecks")
    if isinstance(bound, list):
        return [
            str(item.get("name")) for item in bound
            if isinstance(item, dict) and item.get("name")
        ]
    legacy = data.get("requiredCheckNames")
    return [str(name) for name in legacy] if isinstance(legacy, list) else []


def check_instance_identity(repo: Path, rule: dict) -> list[dict]:
    data = read_json(repo / rule["subject"])
    if data is None:
        return []
    declared = data.get(rule.get("identityField", "repository"))
    own = origin_identity(repo)
    if not isinstance(declared, str) or not declared or own is None:
        return []
    if declared.casefold() == own.casefold():
        return []
    return [{
        "detail": f"declares repository {declared!r} while its origin is {own!r}",
        "evidence": {"declared": declared, "origin": own},
    }]


def check_unprovidable_required_check(repo: Path, rule: dict) -> list[dict]:
    data = read_json(repo / rule["subject"])
    if data is None:
        return []
    required = required_names(data)
    if not required:
        return []
    published = published_jobs(repo)
    if not published:
        # No workflow at all is a different defect; do not report it twice.
        return []
    missing = [name for name in required if name not in published]
    if not missing:
        return []
    return [{
        "detail": (
            f"required {missing} but this repository publishes "
            f"{sorted(published)}"
        ),
        "evidence": {"missing": missing, "published": sorted(published)},
    }]


def check_managed_file_drift(repo: Path, rule: dict) -> list[dict]:
    lock = read_json(repo / ".governance" / "manifest.lock.json")
    managed = (lock or {}).get("managedFiles")
    if not isinstance(managed, dict) or not managed:
        return []
    drifted = []
    for name in sorted(managed):
        digest = managed[name]
        target = repo / name
        if not target.is_file():
            drifted.append(name)
            continue
        try:
            body = target.read_bytes()
        except OSError:
            drifted.append(name)
            continue
        if not isinstance(digest, str) or hashlib.sha256(body).hexdigest() != digest:
            drifted.append(name)
    if not drifted:
        return []
    return [{
        "detail": f"{len(drifted)} of {len(managed)} managed files drifted",
        "evidence": {"drifted": drifted[:20], "managed": len(managed)},
    }]


def check_gate_never_executed(repo: Path, rule: dict) -> list[dict]:
    if not (repo / rule["subject"]).is_file():
        return []
    workflows = repo / ".github" / "workflows"
    if not workflows.is_dir():
        return [{"detail": "declares a governance gate and has no workflows at all",
                 "evidence": {"workflows": 0}}]
    for workflow in workflows.glob("*.y*ml"):
        try:
            body = workflow.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if "governance-check.sh" in body or "governance_check.py" in body:
            return []
    return [{
        "detail": "declares a governance gate that no workflow invokes",
        "evidence": {"workflows": len(list(workflows.glob("*.y*ml")))},
    }]


CHECKS = {
    "instance_identity": check_instance_identity,
    "unprovidable_required_check": check_unprovidable_required_check,
    "managed_file_drift": check_managed_file_drift,
    "gate_never_executed": check_gate_never_executed,
}


def discover(roots: list[Path]) -> list[Path]:
    """Find governed checkouts: a Git repository carrying `.governance/`."""
    found: list[Path] = []
    for root in roots:
        if (root / ".git").exists() and (root / ".governance").is_dir():
            found.append(root)
            continue
        if not root.is_dir():
            continue
        for child in sorted(root.iterdir()):
            if (child / ".git").exists() and (child / ".governance").is_dir():
                found.append(child)
    return found


def audit(repos: list[Path], rules: list[dict]) -> dict:
    findings = []
    for repo in repos:
        for rule in rules:
            handler = CHECKS.get(rule["check"])
            if handler is None:
                raise SystemExit(f"unknown check {rule['check']!r} in {rule['code']}")
            for hit in handler(repo, rule):
                findings.append({
                    "code": rule["code"],
                    "severity": rule["severity"],
                    "repository": str(repo),
                    "title": rule["title"],
                    "remediation": rule["remediation"],
                    **hit,
                })
    errors = sum(1 for item in findings if item["severity"] == "error")
    return {
        "schema": REPORT_SCHEMA,
        "repositories": len(repos),
        "findings": findings,
        "errors": errors,
        "warnings": len(findings) - errors,
    }


def render(report: dict) -> str:
    lines = []
    for item in report["findings"]:
        lines.append(
            f"{item['code']} {item['severity'].upper()}: {item['repository']} "
            f"{item['detail']}"
        )
        lines.append(f"  remediation: {item['remediation']}")
    lines.append(
        f"FLEET: {report['repositories']} governed checkouts, "
        f"{report['errors']} errors, {report['warnings']} warnings"
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("roots", nargs="+", type=Path,
                        help="a governed checkout, or a directory holding several")
    parser.add_argument("--rules", type=Path, default=None)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--code", action="append", default=None,
                        help="report only these rule codes; repeatable")
    args = parser.parse_args(argv)

    rules_path = args.rules or (
        Path(__file__).resolve().parents[1] / "governance" / "fleet-conformance.rules.json"
    )
    rules = load_rules(rules_path)
    if args.code:
        wanted = set(args.code)
        rules = [rule for rule in rules if rule["code"] in wanted]
        if not rules:
            raise SystemExit(f"no rule matches {sorted(wanted)}")
    report = audit(discover(list(args.roots)), rules)
    if args.format == "json":
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(render(report))
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
