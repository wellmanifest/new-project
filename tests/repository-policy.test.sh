#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
python3 - "$root" <<'PY'
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

root = Path(sys.argv[1])
spec = importlib.util.spec_from_file_location("repository_policy", root / "scripts/repository_policy.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

assert module.policy_error(module.default_policy()) is None
planfile = {
    "profile": "main-only-planfile",
    "enforcement": "enforce",
    "delivery": {"mode": "main-only", "checkout": "primary", "targetBranches": ["main"]},
    "tickets": {
        "backend": "planfile", "idPattern": r"^PLF-[0-9]+$", "referenceRequired": True,
        "adapterPath": ".governance/ticket-adapter.json", "sourcePaths": [".planfile/events.jsonl"],
    },
}
assert module.policy_error(planfile) is None

with tempfile.TemporaryDirectory() as directory:
    fixture = Path(directory)
    (fixture / ".governance").mkdir()
    (fixture / ".planfile").mkdir()
    (fixture / ".planfile/events.jsonl").write_text(
        json.dumps({"event": {"ticket_id": "PLF-7", "status": "open"}}) + "\n",
        encoding="utf-8",
    )
    (fixture / ".governance/ticket-adapter.json").write_text(json.dumps({
        "schema": "wellmanifest.external-ticket-adapter/v1",
        "ticket": "PLF-7", "summary": "test", "status": "IN_PROGRESS", "workflow": "EDIT",
        "workstream": "governance", "allowedPaths": [".governance/manifest.json", "src/**"], "forbiddenPaths": ["src/private/**"],
        "sourcePaths": [".planfile/events.jsonl"],
    }), encoding="utf-8")
    manifest = {"repositoryPolicy": planfile}
    adapter, error = module.load_adapter(fixture, manifest)
    assert error is None and adapter["ticket"] == "PLF-7"
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=fixture, check=True)
    (fixture / ".governance/manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=fixture, check=True)
    ok, message = module.check_staged(fixture)
    assert ok, message

print("repository-policy.test.sh OK")
PY
