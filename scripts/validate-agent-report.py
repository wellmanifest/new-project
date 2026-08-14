#!/usr/bin/env python3
"""Validate wellmanifest.agent/report/v1. Schema plus fail-closed identity checks; not a runtime."""

from __future__ import annotations

import json
import sys
from fnmatch import fnmatch
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "governance" / "agent-report.schema.json"


def glob_allows(path: str, pattern: str) -> bool:
    if fnmatch(path, pattern):
        return True
    if pattern.endswith("/**"):
        prefix = pattern[:-3]
        return path == prefix or path.startswith(prefix + "/")
    return False


def semantic_errors(document: dict[str, object]) -> list[str]:
    errors: list[str] = []
    workspace = document.get("workspaceRoot")
    toplevel = document.get("gitToplevel")
    if isinstance(workspace, str) and isinstance(toplevel, str) and workspace != toplevel:
        errors.append("workspaceRoot must equal gitToplevel")
    if document.get("shape") == "runtime_service" and document.get("home") == "wellmanifest":
        errors.append("shape=runtime_service must not home=wellmanifest")
    allowed = document.get("allowedPaths")
    touched = document.get("filesTouched")
    if isinstance(allowed, list) and allowed and isinstance(touched, list):
        patterns = [item for item in allowed if isinstance(item, str)]
        for path in touched:
            if not isinstance(path, str) or not any(
                glob_allows(path, pattern) for pattern in patterns
            ):
                errors.append(f"filesTouched path outside allowedPaths: {path}")
    return errors


def validate_document(document: object) -> list[str]:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    errors = [
        f"{'.'.join(str(part) for part in error.path) or '<root>'}: {error.message}"
        for error in validator.iter_errors(document)
    ]
    if isinstance(document, dict):
        errors.extend(semantic_errors(document))
    return errors


def self_test() -> int:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    example = schema["examples"][0]
    failed = validate_document(example)
    if failed:
        print("self-test valid example failed:", *failed, sep="\n", file=sys.stderr)
        return 1
    missing = dict(example)
    del missing["workspaceRoot"]
    if not validate_document(missing):
        print("self-test missing workspaceRoot must reject", file=sys.stderr)
        return 1
    wrong_home = dict(example)
    wrong_home["home"] = "wellmanifest"
    if not validate_document(wrong_home):
        print("self-test runtime_service+wellmanifest must reject", file=sys.stderr)
        return 1
    drift = dict(example)
    drift["gitToplevel"] = "/workspace/other-repo"
    if not validate_document(drift):
        print("self-test workspaceRoot/gitToplevel drift must reject", file=sys.stderr)
        return 1
    scoped = dict(example)
    scoped["filesTouched"] = ["docs/README.md"]
    if not validate_document(scoped):
        print("self-test filesTouched outside allowedPaths must reject", file=sys.stderr)
        return 1
    print("agent-report self-test: ok")
    return 0


def main(argv: list[str]) -> int:
    if len(argv) != 2 or argv[1] in {"-h", "--help"}:
        print(
            "usage: validate-agent-report.py <report.json>|--self-test",
            file=sys.stderr,
        )
        return 2
    if argv[1] == "--self-test":
        return self_test()
    path = Path(argv[1])
    document = json.loads(path.read_text(encoding="utf-8"))
    errors = validate_document(document)
    if errors:
        print(f"invalid {path}:", *errors, sep="\n", file=sys.stderr)
        return 1
    print(f"valid {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
