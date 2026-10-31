#!/usr/bin/env python3
import importlib.util
import json
import shutil
import subprocess
import textwrap
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_governance_workflow_carrier_fallback_removed():
    wf_path = REPO_ROOT / "template/files/new-project-governance.workflow.yml"
    assert wf_path.exists(), "Governance template workflow must exist"
    content = wf_path.read_text(encoding="utf-8")
    assert "--changed-file project/TICKETS.md" not in content, (
        "Scheduled governance run must not fall back to --changed-file project/TICKETS.md"
    )

def test_branch_hygiene_template_workflow():
    wf_path = REPO_ROOT / "template/files/new-project-branch-hygiene.workflow.yml"
    assert wf_path.exists(), "Branch hygiene template workflow must exist"
    content = wf_path.read_text(encoding="utf-8")
    assert "name: new-project-branch-hygiene" in content
    assert "types: [closed]" in content
    assert "contents: write" not in content
    assert "permissions: write-all" not in content
    assert "contents: read" in content

def test_package_manifest_includes_branch_hygiene():
    manifest_path = REPO_ROOT / "governance/package-manifest.json"
    assert manifest_path.exists()
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    targets = {entry["target"]: entry for entry in data.get("files", [])}
    assert ".github/workflows/new-project-branch-hygiene.yml" in targets, (
        "Branch hygiene workflow must be registered in package-manifest.json"
    )
    entry = targets[".github/workflows/new-project-branch-hygiene.yml"]
    assert entry["source"] == "template/files/new-project-branch-hygiene.workflow.yml"
    assert entry["strategy"] == "managed"

def test_close_only_workflow_not_in_required_checks():
    """The generator must skip workflows that only trigger on PR close."""
    spec = importlib.util.spec_from_file_location(
        "generate_required_checks",
        REPO_ROOT / "scripts/generate_required_checks.py",
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    hygiene_text = (
        REPO_ROOT / "template/files/new-project-branch-hygiene.workflow.yml"
    ).read_text(encoding="utf-8")
    callers: list[str] = []
    assert module.published_checks_text(hygiene_text, callers) == [], (
        "A close-only pull_request workflow must not produce required checks"
    )
    assert callers == []

    multiline_close_only_workflow = """name: close-only
on:
  pull_request:
    types:
      - closed
jobs:
  noop:
    runs-on: ubuntu-latest
    steps:
      - run: echo noop
"""
    callers_multiline: list[str] = []
    assert module.published_checks_text(
        multiline_close_only_workflow, callers_multiline
    ) == [], (
        "A close-only pull_request workflow using multi-line types must not produce required checks"
    )
    assert callers_multiline == []

    governance_text = (
        REPO_ROOT / "template/files/new-project-governance.workflow.yml"
    ).read_text(encoding="utf-8")
    callers2: list[str] = []
    governance_checks = module.published_checks_text(governance_text, callers2)
    assert len(governance_checks) > 0, (
        "Governance workflow must still produce required checks"
    )

def test_closed_pr_preserves_branches_without_write_api_calls():
    """Execute the distributed script: event shape must never authorize deletion."""
    node = shutil.which("node")
    assert node, "Node is required to execute the GitHub-script workflow regression"
    content = (REPO_ROOT / "template/files/new-project-branch-hygiene.workflow.yml").read_text()
    script = textwrap.dedent(content.split("          script: |\n", 1)[1])
    harness = r"""
const assert = require('node:assert/strict');
const fs = require('node:fs');
const script = fs.readFileSync(0, 'utf8');
const AsyncFunction = Object.getPrototypeOf(async function() {}).constructor;
(async () => {
  for (const head of ['ticket/387-fix', 'develop', 'release/1.2', 'main', 'topic/quote\"\nline']) {
    for (const merged of [false, true]) for (const fork of [false, true]) {
      let writes = 0; const notices = [];
      const github = {
        paginate: async () => [],
        rest: { pulls: { list: () => [] }, git: { deleteRef: async () => { writes++; } } }
      };
      const context = {repo:{owner:'owner',repo:'repo'}, payload:{
        repository:{default_branch:'main'}, pull_request:{merged,
          head:{ref:head,repo:{full_name:fork?'other/repo':'owner/repo'}}}
      }};
      const core = {notice:x=>notices.push(x),info:()=>{}};
      await new AsyncFunction('context','core','github',script)(context,core,github);
      assert.equal(writes,0,`closing ${head} (merged=${merged},fork=${fork}) must not delete`);
      assert.ok(notices.length,'preservation must be observable');
    }
  }
})().catch(e=>{console.error(e);process.exitCode=1});
"""
    result = subprocess.run([node, "-e", harness], input=script, text=True,
                            capture_output=True, timeout=10)
    assert result.returncode == 0, result.stderr


if __name__ == "__main__":
    test_governance_workflow_carrier_fallback_removed()
    test_branch_hygiene_template_workflow()
    test_package_manifest_includes_branch_hygiene()
    test_close_only_workflow_not_in_required_checks()
    test_closed_pr_preserves_branches_without_write_api_calls()
    print("PASS")
