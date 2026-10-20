#!/usr/bin/env python3
"""Adopters receive the pinned Policy DSL runtime and plain CONTRIBUTING.md is not policy (issue 479)."""

from __future__ import annotations

import importlib.util
import json
import pathlib
import shutil
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
LOCK = json.loads((ROOT / "governance/policy-dsl.lock.json").read_text(encoding="utf-8"))
PACKAGE = json.loads((ROOT / "governance/package-manifest.json").read_text(encoding="utf-8"))
PLAIN_CONTRIBUTING = "# Contributing\n\nOpen a pull request.\n\n```bash\nmake test\n```\n"
BROKEN_POLICY = "# Contributing\n\n```dsl\nDOCUMENT broken\nRULE\n```\n"


def install_managed_payload(target: pathlib.Path) -> None:
    """Copy every managed package entry the way adoption lays out the target."""
    for entry in PACKAGE["files"]:
        if entry["strategy"] != "managed":
            continue
        destination = target / entry["target"]
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / entry["source"], destination)


def load_installed_checker(target: pathlib.Path):
    path = target / ".governance/governance_check.py"
    spec = importlib.util.spec_from_file_location(f"adopted_governance_check_{id(target)}", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        sys.modules.pop(spec.name, None)
        raise
    return module


def policy_findings(checker, target: pathlib.Path) -> list:
    report = checker.Report(target)
    checker.check_policy_dsl(target, report)
    return [finding for finding in report.findings if finding.code == "GOV-POLICY-DSL-001"]


class PolicyDslAdoptionTest(unittest.TestCase):
    def test_package_installs_runtime_at_lock_declared_targets(self):
        managed = {entry["target"]: entry["source"] for entry in PACKAGE["files"] if entry["strategy"] == "managed"}
        installation = LOCK["installation"]
        self.assertEqual(managed.get(installation["managedTargetPath"]), installation["packageSourcePath"])
        self.assertEqual(managed.get(installation["lockTargetPath"]), "governance/policy-dsl.lock.json")

    def test_adopter_contributing_without_dsl_fence_passes(self):
        with tempfile.TemporaryDirectory(prefix="policy-dsl-adopter-") as directory:
            target = pathlib.Path(directory)
            install_managed_payload(target)
            (target / "CONTRIBUTING.md").write_text(PLAIN_CONTRIBUTING, encoding="utf-8")
            checker = load_installed_checker(target)
            self.assertEqual(policy_findings(checker, target), [])

    def test_plain_contributing_passes_even_without_runtime(self):
        with tempfile.TemporaryDirectory(prefix="policy-dsl-legacy-") as directory:
            target = pathlib.Path(directory)
            install_managed_payload(target)
            for name in (LOCK["installation"]["managedTargetPath"], LOCK["installation"]["lockTargetPath"]):
                (target / name).unlink()
            (target / "CONTRIBUTING.md").write_text(PLAIN_CONTRIBUTING, encoding="utf-8")
            checker = load_installed_checker(target)
            self.assertEqual(policy_findings(checker, target), [])

    def test_installed_runtime_still_rejects_invalid_policy_fence(self):
        with tempfile.TemporaryDirectory(prefix="policy-dsl-invalid-") as directory:
            target = pathlib.Path(directory)
            install_managed_payload(target)
            (target / "CONTRIBUTING.md").write_text(BROKEN_POLICY, encoding="utf-8")
            checker = load_installed_checker(target)
            findings = policy_findings(checker, target)
            self.assertEqual(len(findings), 1)
            self.assertNotIn("No such file", findings[0].message)

    def test_dsl_fence_without_runtime_fails_closed(self):
        with tempfile.TemporaryDirectory(prefix="policy-dsl-missing-") as directory:
            target = pathlib.Path(directory)
            install_managed_payload(target)
            (target / LOCK["installation"]["managedTargetPath"]).unlink()
            shutil.copyfile(ROOT / "CONTRIBUTING.md", target / "CONTRIBUTING.md")
            checker = load_installed_checker(target)
            self.assertEqual(len(policy_findings(checker, target)), 1)

    def test_hub_contributing_policy_validates_with_installed_runtime(self):
        with tempfile.TemporaryDirectory(prefix="policy-dsl-hub-") as directory:
            target = pathlib.Path(directory)
            install_managed_payload(target)
            shutil.copyfile(ROOT / "CONTRIBUTING.md", target / "CONTRIBUTING.md")
            checker = load_installed_checker(target)
            self.assertEqual(policy_findings(checker, target), [])


if __name__ == "__main__":
    unittest.main()
