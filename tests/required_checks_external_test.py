#!/usr/bin/env python3
"""Public CLI checks for the existing protected OneDev context and hosted jobs."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
CHECKERS = [ROOT / 'scripts/check_required_checks.py',
            ROOT / 'packages/wellman/src/wellman/_bundled/check_required_checks.py']
EXTERNAL = {'name': 'onedev/local-verify', 'provider': 'onedev'}
WORKFLOW = '''name: verification
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: true
  windows-governance:
    runs-on: windows-latest
    steps:
      - run: true
'''


class ExternalCheckTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        subprocess.run(['git', 'init', '-q', str(self.root)], check=True)
        subprocess.run(['git', '-C', str(self.root), 'remote', 'add', 'origin',
                        'git@github.com:wellmanifest/new-project.git'], check=True)
        self.source = self.root / 'governance/required-checks.json'
        self.source.parent.mkdir()
        self.workflow = self.root / '.github/workflows/ci.yml'
        self.workflow.parent.mkdir(parents=True)
        self.workflow.write_text(WORKFLOW)
        self.document = {'schema': 'new-project.required-checks/v1', 'version': 1,
                         'repository': 'wellmanifest/new-project',
                         'workflowFile': '.github/workflows/ci.yml',
                         'requiredCheckNames': ['onedev/local-verify', 'test', 'windows-governance'],
                         'externalChecks': [copy.deepcopy(EXTERNAL)]}

    def run_checker(self, checker, *extra):
        self.source.write_text(json.dumps(self.document))
        return subprocess.run([sys.executable, str(checker), '--root', str(self.root),
                               '--source', str(self.source), *extra], cwd=self.root,
                              env=os.environ.copy(), capture_output=True, text=True)

    def assert_result(self, success, *extra):
        for checker in CHECKERS:
            with self.subTest(checker=checker.relative_to(ROOT).as_posix()):
                result = self.run_checker(checker, *extra)
                if success:
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                else:
                    self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_explicit_onedev_and_both_hosted_jobs_are_valid(self):
        self.assert_result(True)

    def test_single_workflow_override_keeps_external_binding(self):
        self.assert_result(True, '--workflow', str(self.workflow))

    def test_existing_hosted_only_declaration_is_unchanged(self):
        self.document.pop('externalChecks')
        self.document['requiredCheckNames'].remove('onedev/local-verify')
        self.assert_result(True)

    def test_missing_external_binding_is_not_inferred(self):
        self.document.pop('externalChecks')
        self.assert_result(False)

    def test_missing_windows_job_is_still_refused(self):
        self.workflow.write_text(WORKFLOW.split('  windows-governance:')[0])
        self.assert_result(False)

    def test_omitted_hosted_requirement_is_still_refused(self):
        self.document['requiredCheckNames'].remove('windows-governance')
        self.assert_result(False)

    def test_a_hosted_job_cannot_masquerade_as_external(self):
        self.document['externalChecks'] = [{'name': 'windows-governance', 'provider': 'onedev'}]
        self.assert_result(False)

    def test_unknown_provider_is_refused(self):
        self.document['externalChecks'][0]['provider'] = 'untrusted'
        self.assert_result(False)

    def test_external_context_must_remain_a_required_check(self):
        self.document['requiredCheckNames'].remove('onedev/local-verify')
        self.assert_result(False)

    def test_duplicate_external_bindings_are_refused(self):
        self.document['externalChecks'].append(copy.deepcopy(EXTERNAL))
        self.assert_result(False)

    def test_duplicate_required_external_names_are_refused(self):
        self.document['requiredCheckNames'].append('onedev/local-verify')
        self.assert_result(False)

    def test_malformed_or_open_ended_bindings_are_refused(self):
        for value in [None, {}, 'onedev', [None], ['onedev/local-verify'],
                      [{'name': 'onedev/local-verify'}],
                      [{**EXTERNAL, 'workflowFile': '.github/workflows/ci.yml'}]]:
            with self.subTest(value=value):
                self.document['externalChecks'] = value
                self.assert_result(False)

    def test_external_declaration_does_not_hide_undeclared_hosted_jobs(self):
        self.document['requiredCheckNames'] = ['onedev/local-verify']
        self.assert_result(False)

    def test_a_workflow_cannot_publish_the_external_context(self):
        self.workflow.write_text(WORKFLOW + '''  bridge:
    name: onedev/local-verify
    runs-on: ubuntu-latest
    steps:
      - run: true
''')
        self.assert_result(False)

    def host_findings(self):
        self.source.write_text(json.dumps(self.document))
        contract = {'hosts': [], 'anomalyChecks': {'maxInstructionBytes': 1024, 'requiredTerms': [],
                    'contradictions': [], 'ci': {'requiredChecksCandidates':
                                                ['governance/required-checks.json']}}}
        for index, checker in enumerate(CHECKERS):
            path = checker.with_name('agent_host_check.py')
            spec = importlib.util.spec_from_file_location(f'external_host_{index}', path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module
            spec.loader.exec_module(module)
            yield module.check_guidance_anomalies(self.root, contract)

    def test_host_anomaly_audit_accepts_the_same_closed_binding(self):
        for findings in self.host_findings():
            self.assertEqual(findings, [])

    def test_host_anomaly_audit_refuses_unknown_external_producer(self):
        self.document['externalChecks'][0]['provider'] = 'untrusted'
        for findings in self.host_findings():
            self.assertTrue(any(f.code == 'GOV-AGENT-HOST-004' for f in findings))

    def test_host_anomaly_audit_still_requires_the_windows_job(self):
        self.workflow.write_text(WORKFLOW.split('  windows-governance:')[0])
        for findings in self.host_findings():
            self.assertTrue(any(f.code == 'GOV-AGENT-HOST-004' for f in findings))


if __name__ == '__main__':
    unittest.main()
