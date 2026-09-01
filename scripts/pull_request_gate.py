#!/usr/bin/env python3
"""Resolve a closed live pull-request snapshot into enforce or terminal."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


SNAPSHOT_SCHEMA = "new-project.pull-request-gate-snapshot/v1"
REPORT_SCHEMA = "new-project.pull-request-gate-report/v1"
REPOSITORY_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")


class SnapshotError(ValueError):
    """The live snapshot is malformed, inconsistent or bound elsewhere."""


@dataclass(frozen=True)
class GateDecision:
    schema: str
    repository: str
    pullRequest: int
    headSha: str
    gate: str
    outcome: str


def require_exact_fields(value: dict[str, Any], fields: set[str]) -> None:
    observed = set(value)
    if observed != fields:
        missing = sorted(fields - observed)
        extra = sorted(observed - fields)
        raise SnapshotError(
            f"snapshot fields are invalid (missing={missing}, extra={extra})"
        )


def require_repository(value: Any, label: str) -> str:
    if not isinstance(value, str) or not REPOSITORY_RE.fullmatch(value):
        raise SnapshotError(f"{label} must be an owner/repository identifier")
    return value


def require_sha(value: Any, label: str) -> str:
    if not isinstance(value, str) or not SHA_RE.fullmatch(value):
        raise SnapshotError(f"{label} must be a full lowercase commit SHA")
    return value


def require_pull_request(value: Any, label: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise SnapshotError(f"{label} must be a positive integer")
    return value


def resolve_gate(
    value: Any,
    *,
    expected_repository: str,
    expected_pull_request: int,
    expected_head: str,
) -> GateDecision:
    if not isinstance(value, dict):
        raise SnapshotError("snapshot root must be an object")
    require_exact_fields(
        value,
        {"schema", "repository", "pullRequest", "state", "merged", "headSha"},
    )
    if value["schema"] != SNAPSHOT_SCHEMA:
        raise SnapshotError(f"unsupported snapshot schema: {value['schema']!r}")

    repository = require_repository(value["repository"], "repository")
    pull_request = require_pull_request(value["pullRequest"], "pullRequest")
    head_sha = require_sha(value["headSha"], "headSha")
    if repository.lower() != expected_repository.lower():
        raise SnapshotError("snapshot repository differs from the workflow repository")
    if pull_request != expected_pull_request:
        raise SnapshotError("snapshot pull request differs from the workflow event")
    if head_sha != expected_head:
        raise SnapshotError("live pull-request head differs from the workflow event head")

    state = value["state"]
    merged = value["merged"]
    if state not in {"open", "closed"}:
        raise SnapshotError("state must be open or closed")
    if not isinstance(merged, bool):
        raise SnapshotError("merged must be a boolean")
    if state == "open" and merged:
        raise SnapshotError("an open pull request cannot be merged")

    if state == "open":
        gate, outcome = "enforce", "open"
    else:
        gate, outcome = "terminal", "merged" if merged else "closed-unmerged"
    return GateDecision(
        schema=REPORT_SCHEMA,
        repository=repository,
        pullRequest=pull_request,
        headSha=head_sha,
        gate=gate,
        outcome=outcome,
    )


def render_text(decision: GateDecision) -> str:
    if decision.gate == "terminal":
        return (
            "GOV-PULL-REQUEST-TERMINAL: neutral "
            f"(outcome={decision.outcome}, pullRequest={decision.pullRequest})"
        )
    return f"GOV-PULL-REQUEST-GATE: enforce (pullRequest={decision.pullRequest})"


def render_github(decision: GateDecision) -> str:
    return f"gate={decision.gate}\noutcome={decision.outcome}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", required=True, type=Path)
    parser.add_argument("--expected-repository", required=True)
    parser.add_argument("--expected-pull-request", required=True, type=int)
    parser.add_argument("--expected-head", required=True)
    parser.add_argument("--format", choices=("text", "json", "github"), default="text")
    args = parser.parse_args(argv)

    try:
        expected_repository = require_repository(
            args.expected_repository, "expected repository"
        )
        expected_pull_request = require_pull_request(
            args.expected_pull_request, "expected pull request"
        )
        expected_head = require_sha(args.expected_head, "expected head")
        with args.snapshot.open("r", encoding="utf-8") as stream:
            snapshot = json.load(stream)
        decision = resolve_gate(
            snapshot,
            expected_repository=expected_repository,
            expected_pull_request=expected_pull_request,
            expected_head=expected_head,
        )
    except (OSError, json.JSONDecodeError, SnapshotError) as error:
        print(
            "GOV-PULL-REQUEST-STATE-001 ERROR: "
            f"live pull-request state is missing, invalid or stale: {error}",
            file=sys.stderr,
        )
        return 1

    if args.format == "json":
        print(json.dumps(asdict(decision), sort_keys=True, separators=(",", ":")))
    elif args.format == "github":
        print(render_github(decision))
    else:
        print(render_text(decision))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
