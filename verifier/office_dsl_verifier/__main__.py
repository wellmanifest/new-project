from __future__ import annotations

import argparse
import re

from .core import verify


def _extract_dsl_block(text: str) -> str:
    match = re.search(r"```dsl\n(.*?)\n```", text, re.DOTALL)
    return match.group(1) if match else text


def _parse_actions(text: str) -> list[str]:
    block = _extract_dsl_block(text)
    actions: set[str] = set()
    for line in block.splitlines():
        line = line.strip()
        if line.startswith("DO "):
            actions.add(line.split(None, 1)[1].strip())
        elif line.startswith("ACTION "):
            actions.add(line.split(None, 1)[1].strip())
    return sorted(actions)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--nl", required=True)
    parser.add_argument("--dsl", required=True)
    parser.add_argument("--plan", required=True)
    parser.add_argument("--mode", default="mock")
    args = parser.parse_args()
    with open(args.dsl, "r", encoding="utf-8") as file:
        dsl_text = file.read()
    with open(args.plan, "r", encoding="utf-8") as file:
        plan_text = file.read()
    dsl_actions = _parse_actions(dsl_text)
    plan_actions = _parse_actions(plan_text)
    print(
        verify(
            args.nl,
            dsl_text,
            plan_text,
            dsl_actions,
            plan_actions,
            mode=args.mode,
        ).model_dump_json(indent=2)
    )


if __name__ == "__main__":
    main()
