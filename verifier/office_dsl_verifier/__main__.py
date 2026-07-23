from __future__ import annotations

import argparse
import json

from .core import verify


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--nl", required=True)
    parser.add_argument("--dsl", required=True)
    parser.add_argument("--plan", required=True)
    parser.add_argument("--mode", default="mock")
    args = parser.parse_args()
    with open(args.dsl, "r", encoding="utf-8") as file:
        dsl = json.load(file)
    with open(args.plan, "r", encoding="utf-8") as file:
        plan = json.load(file)
    print(verify(args.nl, dsl, plan, mode=args.mode).model_dump_json(indent=2))


if __name__ == "__main__":
    main()
