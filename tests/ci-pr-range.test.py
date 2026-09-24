#!/usr/bin/env python3
"""Run the CI gate bodies against an installed runtime and real detached Git PRs."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = {
    "adopter": ("template/files/new-project-governance.workflow.yml", "Run the managed governance gate"),
    "reusable": (".github/workflows/governance-gate-reusable.yml", "Run governance gate"),
}


def gate_body(path, step):
    """Extract the literal shell block, so tests exercise the delivered workflow."""
    lines = (ROOT / path).read_text().splitlines()
    start = next(i for i, line in enumerate(lines) if line.strip() == f"- name: {step}")
    start = next(i for i in range(start, len(lines)) if lines[i].strip() == "run: |") + 1
    body = []
    for line in lines[start:]:
        if line.strip() and not line.startswith("          "):
            break
        body.append(line[10:])
    return "\n".join(body) + "\n"


class CIRangeTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="wellman-pr-range-")
        self.addCleanup(self.temp.cleanup)
        # Spaces exercise shell quoting of target-root in the reusable workflow.
        self.root = Path(self.temp.name) / "governed repository"
        self.root.mkdir()
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.name", "CI fixture")
        self.git("config", "user.email", "ci@example.invalid")
        self.git("config", "commit.gpgsign", "false")
        self.write("README.md", "Fixture\n")
        seed = self.commit("seed")
        shutil.copytree(ROOT / "scripts", self.root / ".governance")
        manifest = json.loads((ROOT / "governance/manifest.hub.json").read_text())
        manifest["coordination"]["maxActiveTicketsPerWorkstream"] = 2
        manifest["delivery"]["requiredForImplementation"] = False
        for name in manifest["requiredFiles"]:
            self.write(name, "Fixture\n")
        self.write_json(".governance/manifest.json", manifest)
        for name in ("stack-profiles.json", "work-classification.dsl.json", "standard-packs.json", "required-checks.json"):
            shutil.copy2(ROOT / "governance" / name, self.root / ".governance" / name)
        self.write(".github/workflows/ci.yml", """name: fixture
on: push
jobs:
  test:
    name: test
    runs-on: ubuntu-latest
    steps:
      - run: 'true'
  windows:
    name: windows-governance
    runs-on: windows-latest
    steps:
      - run: 'true'
""")
        shutil.copy2(ROOT / "governance/standard-adoption.default.json", self.root / ".governance/standard-adoption.json")
        self.write("policy.txt", "Pinned policy\n")
        self.write_json(".governance/manifest.lock.json", {
            "schema": "new-project.lock/v1",
            "standard": {**manifest["standard"], "sourceRepository": "wellmanifest/new-project",
                         "sourceRevision": "1" * 40, "publicationStatus": "published"},
            "managedFiles": {"policy.txt": hashlib.sha256((self.root / "policy.txt").read_bytes()).hexdigest()},
        })
        adoption = self.ticket("001", [".governance/**"])
        # Historical publication retains IN_PROGRESS prose until the external
        # controller closes it. This must not become the product PR's ticket.
        adoption["delivery"] = {
            "acceptedBaseSha": seed, "targetBranch": "main", "outcome": "Adopt the standard",
            "nonGoals": ["Product changes"], "complexity": "S", "estimatedMinutes": 10,
            "budgets": {"maxImplementationFiles": 4, "maxAffectedComponents": 1,
                        "maxPublicInterfaceChanges": 0, "maxRuntimeDependencies": 0},
            "architecture": {"status": "accepted", "decision": "Adopt immutable governance files",
                "components": [{"name": "standard", "paths": [".governance/**"]}],
                "responsibilityChanges": False, "interfaceChanges": [], "dataChanges": [],
                "ui": {"impact": "none", "states": [], "evidence": []}, "rollback": "Restore prior pin"},
            "runtimeDependencies": [], "validation": [{"criterion": "AC-01", "commands": ["wellman check"], "evidence": "Fixture"}],
            "standardAdoption": {"sourceRepository": "wellmanifest/new-project", "fromRevision": None, "toRevision": "1" * 40},
        }
        self.write_json("project/ticket-001/intent.json", adoption)
        self.base = self.commit("published historical adoption")
        self.git("update-ref", "refs/remotes/origin/main", self.base)
        self.git("checkout", "-qb", "ticket/002-product")
        self.ticket("002", ["src/**", "policy.txt"])
        self.write("src/product.txt", "product change\n")
        self.head = self.commit("product PR")
        self.git("checkout", "--detach", "-q", self.head)

    def git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.root), *args], stderr=subprocess.PIPE, text=True).strip()

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def write_json(self, name, value):
        self.write(name, json.dumps(value, indent=2) + "\n")

    def commit(self, message):
        self.git("add", ".")
        self.git("commit", "-qm", message)
        return self.git("rev-parse", "HEAD")

    def ticket(self, number, paths):
        name = "ticket-" + number
        self.write(f"project/{name}/README.md", f"# {name}\n- **Status**: IN_PROGRESS\n- **Workflow state**: EDIT\n")
        intent = {"schema": "new-project.intent/v3", "ticket": name, "summary": "Fixture delivery",
                  "workstream": "governance", "allowedPaths": paths + [f"project/{name}/**"],
                  "forbiddenPaths": ["project/ticket-*/user-*.md"], "stacks": [], "dependsOn": [],
                  "conflictsWith": [], "integrationTicket": None,
                  "classification": {"kind": "FEATURE", "priority": "P2", "origin": "requested"}}
        self.write_json(f"project/{name}/intent.json", intent)
        return intent

    def run_gate(self, name, base=None, head=None, body=None):
        env = dict(os.environ, GOVERNANCE_ROOT=str(self.root), CI="true")
        env["PATH"] = str(Path(sys.executable).parent) + os.pathsep + env["PATH"]
        for key, value in (("BASE_SHA", base), ("HEAD_SHA", head)):
            env.pop(key, None)
            if value is not None:
                env[key] = value
        return subprocess.run(["bash", "-c", body or gate_body(*WORKFLOWS[name])],
                              cwd=self.root, env=env, capture_output=True, text=True)

    def assert_pass(self, result):
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_detached_product_after_historical_adoption(self):
        old = self.run_gate("adopter", body="wellman check --root . --actor ci --json")
        self.assertNotEqual(0, old.returncode)
        self.assertIn("Atomic standard adoption preconditions are invalid", old.stdout)
        for name in WORKFLOWS:
            with self.subTest(workflow=name):
                self.assert_pass(self.run_gate(name, self.base, self.head))

    def test_partial_ranges_fail_before_validation(self):
        for name in WORKFLOWS:
            for base, head in ((self.base, None), (None, self.head)):
                with self.subTest(workflow=name, base=base):
                    result = self.run_gate(name, base, head)
                    self.assertNotEqual(0, result.returncode)
                    self.assertIn("Both BASE_SHA and HEAD_SHA are required", result.stderr)
                    self.assertEqual("", result.stdout)

    def test_scheduled_check_keeps_no_range_semantics(self):
        # A published checkout without outstanding adoption has no PR range.
        self.write("project/ticket-001/README.md", "# Historical ticket\n- **Status**: DONE\n- **Workflow state**: DONE\n")
        self.commit("external closure projected in fixture")
        self.git("update-ref", "refs/remotes/origin/main", "HEAD")
        for name in WORKFLOWS:
            with self.subTest(workflow=name):
                self.assert_pass(self.run_gate(name))

    def test_managed_gate_rejects_committed_drift_with_exact_range(self):
        self.write("policy.txt", "Unauthorized changed policy\n")
        drift_head = self.commit("managed drift in product PR")
        result = self.run_gate("adopter", self.base, drift_head)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("Managed governance file digest differs: policy.txt", result.stdout)

    def test_reusable_checks_out_event_head(self):
        text = (ROOT / WORKFLOWS["reusable"][0]).read_text()
        self.assertIn("ref: ${{ github.event.pull_request.head.sha || github.sha }}", text)


if __name__ == "__main__":
    unittest.main()
