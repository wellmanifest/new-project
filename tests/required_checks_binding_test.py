#!/usr/bin/env python3
"""Adoption binds required checks to the real repository on the first pass; disposable fixtures only."""
from contextlib import redirect_stderr, redirect_stdout
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import unittest.mock

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


adopter = load("binding_adopter", ROOT / "scripts/create_adoption_lock.py")
SEED = (ROOT / "template/files/required-checks.template.json").read_bytes()
WORKFLOW = (ROOT / "template/files/new-project-governance.workflow.yml").read_bytes()


class RequiredChecksBindingTest(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)

    def project(self, repository=None):
        payloads = {adopter.CHECKS_TARGET: SEED, ".github/workflows/new-project-governance.yml": WORKFLOW}
        output, diagnostics = io.StringIO(), io.StringIO()
        with redirect_stdout(output), redirect_stderr(diagnostics):
            adopter.project_inherited_required_checks(self.root, payloads, repository=repository)
        # Plan exports print JSON on stdout, so the projection must keep it clean.
        self.assertEqual(output.getvalue(), "")
        return json.loads(payloads[adopter.CHECKS_TARGET])["repository"], diagnostics.getvalue()

    def remote(self, url):
        subprocess.run(["git", "-C", str(self.root), "remote", "add", "origin", url], check=True)

    def test_existing_remote_binds_the_real_name_on_the_first_pass(self):
        self.remote("https://github.com/paxlet-com/willcore.git")
        self.assertEqual(self.project(), ("paxlet-com/willcore", ""))
        self.assertEqual(self.project("Paxlet-Com/WillCore")[0], "Paxlet-Com/WillCore")

    def test_explicit_repository_binds_before_the_remote_exists(self):
        self.assertEqual(self.project("paxlet-com/shellmux"), ("paxlet-com/shellmux", ""))

    def test_repository_disagreeing_with_origin_is_refused(self):
        self.remote("git@github.com:paxlet-com/willcore.git")
        with self.assertRaisesRegex(SystemExit, "disagrees with origin paxlet-com/willcore"):
            self.project("paxlet-com/other")

    def test_without_identity_the_placeholder_is_kept_and_reported(self):
        repository, output = self.project()
        self.assertEqual(repository, adopter.UNRESOLVED_ADOPTER)
        self.assertIn("UNBOUND .governance/required-checks.json keeps unresolved/adopter", output)
        self.assertIn("--repository OWNER/NAME", output)

    def test_cli_rejects_a_malformed_or_placeholder_repository(self):
        for value in ("not-a-ref", "unresolved/adopter", "a/b/c"):
            with self.subTest(value=value), redirect_stdout(io.StringIO()), \
                    self.assertRaises(SystemExit) as raised, \
                    unittest.mock.patch("sys.stderr", io.StringIO()):
                adopter.main(["--target-root", str(self.root), "--source-revision", "0" * 40,
                              "--repository", value])
            self.assertEqual(raised.exception.code, 2)

    def test_gate_states_the_deterministic_remedy(self):
        checkers = [load(f"binding_checker_{index}", ROOT / path) for index, path in enumerate((
            "scripts/check_required_checks.py", "packages/wellman/src/wellman/_bundled/check_required_checks.py"))]
        source = self.root / "required-checks.json"
        source.write_bytes(SEED)
        for remote, expected in ((None, "no origin remote detected; add it or pass --repository OWNER/NAME"),
                                 ("https://github.com/paxlet-com/willenvs.git",
                                  "detected 'paxlet-com/willenvs'; rerun the managed updater")):
            if remote:
                self.remote(remote)
            for checker in checkers:
                with self.subTest(remote=remote, checker=checker.__name__):
                    message = checker.check_instance_identity(self.root, json.loads(SEED), source)[0]
                    self.assertIn(expected, message)
                    self.assertIn("create_adoption_lock.py --target-root . --source-revision", message)


if __name__ == "__main__":
    unittest.main()
