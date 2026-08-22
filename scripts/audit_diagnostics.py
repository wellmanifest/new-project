#!/usr/bin/env python3
"""Verify stable GOV codes, canonical remediations and linked error runbooks."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path, PurePosixPath
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = Path("governance/diagnostics.json")
CATALOG_SCHEMA = "new-project.diagnostics/v2"
GOV_CODE = re.compile(r"GOV-[A-Z]+(?:-[A-Z]+)*-[0-9]{3}")
RUNTIME_SUFFIXES = {".bat", ".py", ".ps1", ".sh", ".yaml", ".yml"}
RUNTIME_DIRECTORIES = (
    Path("project"),
    Path("scripts"),
    Path("template/files"),
    Path(".github/workflows"),
)
# Git hooks are executable contract surface but carry no file suffix, so they
# are collected separately; ticket-106 added them after GOV-AGENT-HOST codes
# emitted by .githooks/pre-commit escaped the catalog entirely.
RUNTIME_UNSUFFIXED_DIRECTORIES = (Path(".githooks"),)
RUNBOOK_SECTIONS = (
    "## Situation",
    "## Meaning",
    "## Safe resolution",
    "## Verification",
    "## Do not",
    "## Related rules",
)


def runtime_paths(root: Path) -> tuple[Path, ...]:
    paths = {Path("project.sh"), Path("project.bat")}
    for directory in RUNTIME_DIRECTORIES:
        absolute = root / directory
        if not absolute.is_dir():
            continue
        paths.update(
            path.relative_to(root)
            for path in absolute.iterdir()
            if path.is_file() and path.suffix in RUNTIME_SUFFIXES
        )
    for directory in RUNTIME_UNSUFFIXED_DIRECTORIES:
        absolute = root / directory
        if not absolute.is_dir():
            continue
        paths.update(
            path.relative_to(root) for path in absolute.iterdir() if path.is_file()
        )
    return tuple(sorted(paths, key=str))


def emitted_codes(root: Path, paths: tuple[Path, ...]) -> set[str]:
    codes: set[str] = set()
    for relative in paths:
        source = (root / relative).read_text(encoding="utf-8")
        codes.update(GOV_CODE.findall(source))
    return codes


def valid_documentation_path(raw: str) -> bool:
    path = PurePosixPath(raw)
    return (
        len(path.parts) == 2
        and path.parts[0] == "error"
        and path.suffix == ".md"
        and ".." not in path.parts
    )


def catalog_findings(
    root: Path,
    paths: tuple[Path, ...],
) -> tuple[list[str], list[str], dict[str, Any]]:
    catalog_errors: list[str] = []
    runbook_errors: list[str] = []
    try:
        catalog = json.loads((root / CATALOG_PATH).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return [f"catalog is unreadable: {error}"], [], {}

    if not isinstance(catalog, dict) or set(catalog) != {"schema", "codes"}:
        return ["catalog fields must be exactly schema and codes"], [], catalog
    if catalog.get("schema") != CATALOG_SCHEMA:
        catalog_errors.append(f"schema must be {CATALOG_SCHEMA}")
    entries = catalog.get("codes")
    if not isinstance(entries, dict):
        return catalog_errors + ["codes must be an object"], [], catalog

    for code, entry in entries.items():
        if GOV_CODE.fullmatch(code) is None:
            catalog_errors.append(f"invalid code key: {code}")
            continue
        if not isinstance(entry, dict) or set(entry) != {
            "message", "remediation", "documentation",
        }:
            catalog_errors.append(f"{code}: fields must be message, remediation, documentation")
            continue
        for field in ("message", "remediation"):
            if not isinstance(entry.get(field), str) or not entry[field].strip():
                catalog_errors.append(f"{code}: {field} must be non-empty")
        documentation = entry.get("documentation")
        if documentation is None:
            continue
        if not isinstance(documentation, str) or not valid_documentation_path(documentation):
            runbook_errors.append(f"{code}: documentation must match error/*.md")
            continue
        path = root / documentation
        try:
            content = path.read_text(encoding="utf-8")
        except OSError as error:
            runbook_errors.append(f"{code}: runbook is unreadable: {error}")
            continue
        missing = [section for section in RUNBOOK_SECTIONS if section not in content]
        if missing:
            runbook_errors.append(f"{code}: runbook missing sections: {', '.join(missing)}")

    emitted = emitted_codes(root, paths)
    registered = set(entries)
    for code in sorted(emitted - registered):
        catalog_errors.append(f"emitted code is not registered: {code}")
    for code in sorted(registered - emitted):
        catalog_errors.append(f"registered code is not emitted: {code}")
    return catalog_errors, runbook_errors, catalog


def audit(root: Path = REPO_ROOT) -> dict[str, Any]:
    paths = runtime_paths(root)
    catalog_errors, runbook_errors, catalog = catalog_findings(root, paths)
    codes = catalog.get("codes", {}) if isinstance(catalog, dict) else {}
    findings = [
        {"code": "GOV-DIAGNOSTIC-001", "message": message}
        for message in catalog_errors
    ] + [
        {"code": "GOV-DIAGNOSTIC-002", "message": message}
        for message in runbook_errors
    ]
    return {
        "schema": "new-project.diagnostic-audit/v1",
        "codes": len(codes) if isinstance(codes, dict) else 0,
        "runtimePaths": [str(path) for path in paths],
        "findings": findings,
        "ok": not findings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=str(REPO_ROOT))
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args()
    report = audit(Path(args.root))
    if args.format == "json":
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(
            f"diagnostic-catalog: {report['codes']} codes, "
            f"{len(report['findings'])} findings"
        )
        for finding in report["findings"]:
            print(f"{finding['code']}: {finding['message']}")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
