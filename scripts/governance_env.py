#!/usr/bin/env python3
"""Resolve explicitly declared governance DSL variables from process env and .env."""

from __future__ import annotations

import argparse
import json
import math
import os
from dataclasses import dataclass
from pathlib import Path
import re
import shlex
import subprocess
import sys
from typing import Sequence
from urllib.parse import urlsplit


NAME_PATTERN = re.compile(r"[A-Z][A-Z0-9_]*")
TYPES = {"STRING", "INTEGER", "NUMBER", "BOOLEAN", "URL", "PATH"}


class ContractError(ValueError):
    pass


@dataclass(frozen=True)
class VariableSpec:
    name: str
    value_type: str
    secret: bool
    required: bool
    default: str | None


@dataclass(frozen=True)
class EnvironmentContract:
    path: Path
    env_file: Path
    env_file_required: bool
    variables: tuple[VariableSpec, ...]


@dataclass(frozen=True)
class ResolvedVariable:
    spec: VariableSpec
    value: str
    source: str


def _contract_member(base: Path, raw: str, label: str) -> Path:
    candidate = Path(raw)
    if candidate.is_absolute():
        raise ContractError(f"{label} must be a relative path")
    resolved = (base / candidate).resolve()
    try:
        resolved.relative_to(base)
    except ValueError as exc:
        raise ContractError(f"{label} escapes the contract directory") from exc
    return resolved


def _tokens(line: str, line_number: int) -> list[str]:
    try:
        return shlex.split(line, comments=False, posix=True)
    except ValueError as exc:
        raise ContractError(f"invalid DSL quoting at line {line_number}") from exc


def parse_contract(path: Path) -> EnvironmentContract:
    contract_path = path.resolve()
    env_declaration: tuple[str, bool] | None = None
    variables: list[VariableSpec] = []
    names: set[str] = set()

    for line_number, raw_line in enumerate(contract_path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw_line.strip()
        if line.startswith(("ENV_FILE <", "VARIABLE <", "SECRET <")):
            continue
        if line.startswith("ENV_FILE "):
            tokens = _tokens(line, line_number)
            if len(tokens) != 3 or tokens[2] not in {"OPTIONAL", "REQUIRED"}:
                raise ContractError(f"invalid ENV_FILE declaration at line {line_number}")
            if env_declaration is not None:
                raise ContractError("the contract must declare exactly one ENV_FILE")
            env_declaration = (tokens[1], tokens[2] == "REQUIRED")
            continue
        if not (line.startswith("VARIABLE ") or line.startswith("SECRET ")):
            continue
        tokens = _tokens(line, line_number)
        secret = tokens[0] == "SECRET"
        if len(tokens) < 6 or tokens[2] != "TYPE" or tokens[4:6] != ["FROM", "ENV"]:
            raise ContractError(f"invalid variable declaration at line {line_number}")
        name, value_type = tokens[1], tokens[3]
        if NAME_PATTERN.fullmatch(name) is None or value_type not in TYPES:
            raise ContractError(f"invalid variable name or type at line {line_number}")
        if name in names:
            raise ContractError(f"duplicate variable declaration: {name}")
        suffix = tokens[6:]
        required = suffix == ["REQUIRED"] or (secret and suffix == ["REQUIRED", "REDACT"])
        default = suffix[1] if len(suffix) == 2 and suffix[0] == "DEFAULT" else None
        if secret and suffix != ["REQUIRED", "REDACT"]:
            raise ContractError(f"SECRET {name} must be REQUIRED REDACT")
        if not secret and suffix not in ([], ["REQUIRED"]) and default is None:
            raise ContractError(f"invalid source policy for {name}")
        names.add(name)
        variables.append(VariableSpec(name, value_type, secret, required, default))

    if env_declaration is None:
        raise ContractError("the contract does not declare ENV_FILE")
    if not variables:
        raise ContractError("the contract does not declare environment variables")
    env_file = _contract_member(contract_path.parent, env_declaration[0], "ENV_FILE")
    return EnvironmentContract(
        contract_path,
        env_file,
        env_declaration[1],
        tuple(variables),
    )


def _dotenv_value(raw: str, line_number: int) -> str:
    value = raw.strip()
    if not value:
        return ""
    if value[0] in {"'", '"'}:
        tokens = _tokens(value, line_number)
        if len(tokens) != 1:
            raise ContractError(f"invalid quoted .env value at line {line_number}")
        return tokens[0]
    return re.split(r"\s+#", value, maxsplit=1)[0].rstrip()


def load_dotenv(path: Path, required: bool) -> dict[str, str]:
    if not path.exists():
        if required:
            raise ContractError("required ENV_FILE is missing")
        return {}
    values: dict[str, str] = {}
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].lstrip()
        if "=" not in line:
            raise ContractError(f"invalid .env assignment at line {line_number}")
        name, raw_value = line.split("=", 1)
        name = name.strip()
        if NAME_PATTERN.fullmatch(name) is None:
            raise ContractError(f"invalid .env name at line {line_number}")
        if name in values:
            raise ContractError(f"duplicate .env assignment: {name}")
        values[name] = _dotenv_value(raw_value, line_number)
    return values


def _validate_value(spec: VariableSpec, raw: str) -> str:
    if "\x00" in raw:
        raise ContractError(f"{spec.name} contains a NUL byte")
    if spec.required and not raw:
        raise ContractError(f"required variable {spec.name} is empty")
    try:
        if spec.value_type == "INTEGER":
            int(raw)
        elif spec.value_type == "NUMBER":
            if not math.isfinite(float(raw)):
                raise ValueError
        elif spec.value_type == "BOOLEAN":
            normalized = raw.lower()
            if normalized not in {"1", "0", "true", "false", "yes", "no", "on", "off"}:
                raise ValueError
            return "true" if normalized in {"1", "true", "yes", "on"} else "false"
        elif spec.value_type == "URL":
            parsed = urlsplit(raw)
            if not parsed.scheme or not parsed.netloc:
                raise ValueError
    except ValueError as exc:
        raise ContractError(f"variable {spec.name} is not a valid {spec.value_type}") from exc
    return raw


def resolve_contract(contract: EnvironmentContract) -> tuple[ResolvedVariable, ...]:
    dotenv = load_dotenv(contract.env_file, contract.env_file_required)
    resolved: list[ResolvedVariable] = []
    for spec in contract.variables:
        if spec.name in os.environ:
            raw, source = os.environ[spec.name], "process"
        elif spec.name in dotenv:
            raw, source = dotenv[spec.name], "env_file"
        elif spec.default is not None:
            raw, source = spec.default, "default"
        elif spec.required:
            raise ContractError(f"required variable {spec.name} is unresolved")
        else:
            continue
        resolved.append(ResolvedVariable(spec, _validate_value(spec, raw), source))
    return tuple(resolved)


def report(contract: EnvironmentContract, resolved: tuple[ResolvedVariable, ...]) -> dict[str, object]:
    return {
        "schema": "new-project.environment-resolution/v1",
        "status": "resolved",
        "contract": contract.path.as_posix(),
        "envFile": contract.env_file.as_posix(),
        "variables": {
            item.spec.name: {
                "type": item.spec.value_type.lower(),
                "source": item.source,
                "secret": item.spec.secret,
                "value": "[REDACTED]" if item.spec.secret else item.value,
            }
            for item in resolved
        },
    }


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--contract",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "CONTRIBUTING.md",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("check", help="validate and print a redacted resolution report")
    run_parser = subparsers.add_parser("run", help="run a command with declared variables")
    run_parser.add_argument("child", nargs=argparse.REMAINDER)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        contract = parse_contract(args.contract)
        resolved = resolve_contract(contract)
        if args.command == "check":
            print(json.dumps(report(contract, resolved), ensure_ascii=True, sort_keys=True))
            return 0
        child = list(args.child)
        if child[:1] == ["--"]:
            child = child[1:]
        if not child:
            raise ContractError("run requires a command after --")
        environment = os.environ.copy()
        environment.update({item.spec.name: item.value for item in resolved})
        return subprocess.run(child, env=environment, check=False).returncode
    except (ContractError, OSError) as exc:
        print(f"GOV-ENV-001: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
