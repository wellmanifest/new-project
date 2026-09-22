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
audit_policy = {
    "profile": "local-audit", "enforcement": "audit",
    "delivery": {"mode": "main-only", "checkout": "primary", "targetBranches": ["main"]},
    "tickets": {"backend": "files", "idPattern": r"^ticket-[0-9]+$", "referenceRequired": True},
}
assert module.policy_error(audit_policy) is None
assert module.relative_path_error("../outside") is not None
assert module.relative_path_error(".governance/../outside") is not None
assert module.relative_path_error("/outside") is not None
assert module.relative_path_error("src/**", pattern=False) is not None
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
unsafe_planfile = json.loads(json.dumps(planfile))
unsafe_planfile["tickets"]["sourcePaths"] = ["../events.jsonl"]
assert module.policy_error(unsafe_planfile) is not None

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
        "workstream": "governance", "allowedPaths": [".governance/manifest.json", ".planfile/events.jsonl", "src/**"], "forbiddenPaths": ["src/private/**"],
        "sourcePaths": [".planfile/events.jsonl"],
    }), encoding="utf-8")
    manifest = {"repositoryPolicy": planfile}
    adapter, error = module.load_adapter(fixture, manifest)
    assert error is None and adapter["ticket"] == "PLF-7"
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=fixture, check=True)
    (fixture / ".governance/manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=fixture, check=True)
    subprocess.run(["git", "add", "-f", ".planfile/events.jsonl"], cwd=fixture, check=True)
    ok, message = module.check_staged(fixture)
    assert ok, message

with tempfile.TemporaryDirectory() as directory:
    fixture = Path(directory)
    (fixture / ".governance").mkdir()
    (fixture / ".planfile").mkdir()
    (fixture / "src").mkdir()
    (fixture / ".planfile/events.jsonl").write_text(
        json.dumps({"event": {"ticket_id": "PLF-8", "status": "open"}}) + "\n",
        encoding="utf-8",
    )
    policy = json.loads(json.dumps(planfile))
    policy["tickets"]["adapterPath"] = ".governance/ticket-adapter.json"
    policy["tickets"]["sourcePaths"] = [".planfile/events.jsonl"]
    (fixture / ".governance/manifest.json").write_text(
        json.dumps({"repositoryPolicy": policy}), encoding="utf-8"
    )
    adapter = {
        "schema": "wellmanifest.external-ticket-adapter/v1",
        "ticket": "PLF-8", "summary": "test", "status": "IN_PROGRESS", "workflow": "EDIT",
        "workstream": "governance", "allowedPaths": [".governance/manifest.json", "README.md"],
        "forbiddenPaths": [], "sourcePaths": [".planfile/events.jsonl"],
    }
    (fixture / ".governance/ticket-adapter.json").write_text(json.dumps(adapter), encoding="utf-8")
    (fixture / "README.md").write_text("initial\n", encoding="utf-8")
    (fixture / "src/outside.txt").write_text("outside\n", encoding="utf-8")
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=fixture, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=fixture, check=True)
    subprocess.run(["git", "config", "user.name", "Repository Policy Test"], cwd=fixture, check=True)
    subprocess.run(["git", "add", "."], cwd=fixture, check=True)
    subprocess.run(["git", "add", "-f", ".planfile/events.jsonl"], cwd=fixture, check=True)
    subprocess.run(["git", "commit", "-qm", "fixture"], cwd=fixture, check=True)

    # The hook must inspect the staged adapter, not an unstaged working-tree adapter.
    (fixture / "README.md").write_text("allowed staged change\n", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=fixture, check=True)
    worktree_adapter = json.loads(json.dumps(adapter))
    worktree_adapter["allowedPaths"] = ["src/**"]
    (fixture / ".governance/ticket-adapter.json").write_text(
        json.dumps(worktree_adapter), encoding="utf-8"
    )
    ok, message = module.check_staged(fixture)
    assert ok, message

    # Deletions are material paths and must not bypass the external scope.
    subprocess.run(["git", "reset", "-q", "HEAD", "README.md"], cwd=fixture, check=True)
    (fixture / ".governance/ticket-adapter.json").write_text(json.dumps(adapter), encoding="utf-8")
    (fixture / "src/outside.txt").unlink()
    subprocess.run(["git", "add", "-A"], cwd=fixture, check=True)
    ok, message = module.check_staged(fixture)
    assert not ok and "outside" in message, message

    # A changed adapter cannot authorize delivery files in the same commit.
    subprocess.run(["git", "reset", "-q", "HEAD", "."], cwd=fixture, check=True)
    (fixture / "src/new.txt").write_text("new\n", encoding="utf-8")
    expanded_adapter = json.loads(json.dumps(adapter))
    expanded_adapter["allowedPaths"] = ["src/**"]
    (fixture / ".governance/ticket-adapter.json").write_text(
        json.dumps(expanded_adapter), encoding="utf-8"
    )
    subprocess.run(["git", "add", ".governance/ticket-adapter.json", "src/new.txt"], cwd=fixture, check=True)
    ok, message = module.check_staged(fixture)
    assert not ok and "adapter changes must be committed separately" in message, message

print("repository-policy.test.sh OK")
PY
