"""Offline reusable check contracts bind the reference and the source bytes."""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import generate_required_checks as generator
import check_required_checks as checker

PIN = 'a' * 40
USES = f'owner/ci/.github/workflows/test.yml@{PIN}'
CALLEE = 'on:\n  workflow_call:\njobs:\n  test:\n    name: Linux tests\n    runs-on: ubuntu-latest\n    steps:\n      - run: true\n'


class ReusableChecksTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        subprocess.run(['git', 'init', '-q', str(self.root)], check=True)
        subprocess.run(['git', '-C', str(self.root), 'remote', 'add', 'origin',
                        'https://github.com/owner/product.git'], check=True)
        (self.root / '.github/workflows').mkdir(parents=True)
        self.caller = self.root / '.github/workflows/ci.yml'
        self.source = self.root / '.github/reusable-workflows/test.yml'
        self.source.parent.mkdir()
        self.lock = self.root / '.github/reusable-workflows.lock.json'
        self.caller.write_text(f'on: [push, pull_request]\njobs:\n  ci:\n    name: CI\n    uses: {USES}\n')
        self.install_source(CALLEE)

    def install_source(self, content):
        self.source.write_text(content)
        self.entry = {'uses': USES, 'sourceFile': '.github/reusable-workflows/test.yml',
                      'sourceSha256': hashlib.sha256(self.source.read_bytes()).hexdigest()}
        self.write_lock()

    def write_lock(self):
        self.lock.write_text(json.dumps({'schema': 'new-project.reusable-workflows/v1',
                                         'workflows': [self.entry]}))

    def test_generator_and_checker_derive_same_caller_leaf_names(self):
        doc = generator.declaration_for(self.root)
        self.assertEqual(doc['requiredChecks'], [{'name': 'CI / Linux tests',
                                                 'workflowFile': '.github/workflows/ci.yml'}])
        self.assertNotIn('reusableWorkflowCallers', doc)
        self.assertEqual(checker.workflow_job_names(self.caller), ['CI / Linux tests'])
        declaration = self.root / 'required-checks.json'
        declaration.write_text(json.dumps(doc))
        self.assertEqual(checker.main(['--root', str(self.root), '--source', str(declaration)]), 0)

    def test_bundled_checker_resolves_reusable_sources(self):
        path = ROOT / 'packages/wellman/src/wellman/_bundled/check_required_checks.py'
        spec = importlib.util.spec_from_file_location('bundled_reusable_checker', path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertEqual(module.workflow_job_names(self.caller), ['CI / Linux tests'])

    def host_reader(self, bundled=False):
        location = ('packages/wellman/src/wellman/_bundled/agent_host_check.py'
                    if bundled else 'scripts/agent_host_check.py')
        name = 'reusable_host_bundled' if bundled else 'reusable_host_managed'
        spec = importlib.util.spec_from_file_location(name, ROOT / location)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        return module

    def host_ci_findings(self, module):
        declaration = self.root / 'required-checks.json'
        declaration.write_text(json.dumps({'requiredChecks': [
            {'name': 'CI / Linux tests', 'workflowFile': '.github/workflows/ci.yml'}]}))
        contract = {'hosts': [], 'anomalyChecks': {
            'maxInstructionBytes': 65536, 'requiredTerms': [], 'contradictions': [],
            'ci': {'requiredChecksCandidates': ['required-checks.json']}}}
        return module.check_guidance_anomalies(self.root, contract)

    def test_host_audit_resolves_valid_reusable_checks_in_both_packages(self):
        for bundled in (False, True):
            with self.subTest(bundled=bundled):
                module = self.host_reader(bundled)
                self.assertEqual(module.workflow_job_names(self.caller), ['CI / Linux tests'])
                self.assertEqual(self.host_ci_findings(module), [])

    def test_host_audit_refuses_invalid_reusable_contracts_without_exiting(self):
        original = self.caller.read_text()
        for bundled in (False, True):
            for kind in ('missing-lock', 'mutable', 'wrong-digest', 'missing-source', 'local-call'):
                with self.subTest(bundled=bundled, kind=kind):
                    self.caller.write_text(original)
                    self.install_source(CALLEE)
                    if kind == 'missing-lock':
                        self.lock.unlink()
                    elif kind == 'mutable':
                        self.caller.write_text(original.replace(PIN, 'main'))
                    elif kind == 'wrong-digest':
                        self.source.write_text(CALLEE + '# modified\n')
                    elif kind == 'missing-source':
                        self.source.unlink()
                    else:
                        self.caller.write_text(original.replace(USES, './.github/workflows/local.yml'))
                    findings = self.host_ci_findings(self.host_reader(bundled))
                    self.assertEqual(len(findings), 1)
                    self.assertEqual(findings[0].code, 'GOV-AGENT-HOST-004')
                    self.assertIn('cannot be resolved', findings[0].message)

    def test_host_reader_shares_unicode_and_quoted_direct_job_names(self):
        self.caller.write_text('on: [pull_request]\njobs:\n  test:\n    name: "Test # \\u03b1" # comment\n    runs-on: ubuntu-latest\n')
        for bundled in (False, True):
            self.assertEqual(self.host_reader(bundled).workflow_job_names(self.caller), ['Test # α'])

    def test_quoted_hash_unicode_and_escaped_apostrophes(self):
        self.caller.write_text(self.caller.read_text().replace('name: CI', 'name: "CI # gate" # caller comment'))
        self.install_source(CALLEE.replace('name: Linux tests', "name: 'Linux # it''s tests' # callee comment"))
        expected = ["CI # gate / Linux # it's tests"]
        self.assertEqual([item['name'] for item in generator.declaration_for(self.root)['requiredChecks']], expected)
        self.assertEqual(checker.workflow_job_names(self.caller), expected)
        self.install_source(CALLEE.replace('name: Linux tests', 'name: "Test \\u03b1"'))
        self.assertEqual(checker.workflow_job_names(self.caller), ['CI # gate / Test α'])

    def test_direct_job_scalar_interpretation_matches_generator(self):
        self.caller.write_text('on: [pull_request]\njobs:\n  test:\n    name: "Test # \\u03b1" # comment\n    runs-on: ubuntu-latest\n')
        self.assertEqual(checker.workflow_job_names(self.caller), ['Test # α'])
        self.assertEqual(generator.declaration_for(self.root)['requiredChecks'][0]['name'], 'Test # α')

    def test_invalid_quoted_names_refuse(self):
        for name in ['"unterminated', "'unterminated", '"valid" invalid suffix', '"unsupported \\x01"']:
            with self.subTest(name=name):
                self.install_source(CALLEE.replace('name: Linux tests', f'name: {name}'))
                with self.assertRaises(SystemExit):
                    generator.declaration_for(self.root)

    def test_adoption_projects_contract_with_workflow_overlay(self):
        spec = importlib.util.spec_from_file_location('reusable_adopter', ROOT / 'scripts/create_adoption_lock.py')
        adopter = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(adopter)
        payloads = {adopter.CHECKS_TARGET: json.dumps({'repository': 'unresolved/adopter'}).encode()}
        adopter.project_inherited_required_checks(self.root, payloads)
        self.assertEqual(json.loads(payloads[adopter.CHECKS_TARGET])['requiredChecks'][0]['name'],
                         'CI / Linux tests')
        payloads = {adopter.CHECKS_TARGET: json.dumps({'repository': 'unresolved/adopter'}).encode(),
                    '.github/workflows/ci.yml': self.caller.read_bytes().replace(PIN.encode(), b'b' * 40)}
        with self.assertRaises(SystemExit):
            adopter.project_inherited_required_checks(self.root, payloads)

    def test_missing_contract_keeps_unresolved_caller_and_checker_refuses(self):
        self.lock.unlink()
        self.assertEqual(generator.declaration_for(self.root)['reusableWorkflowCallers'], ['CI'])
        with self.assertRaises(SystemExit):
            checker.workflow_job_names(self.caller)

    def test_mutable_reference_refuses(self):
        self.entry['uses'] = USES.replace(PIN, 'main')
        self.write_lock()
        self.caller.write_text(self.caller.read_text().replace(PIN, 'main'))
        with self.assertRaises(SystemExit):
            generator.declaration_for(self.root)

    def test_changed_source_bytes_refuse(self):
        self.source.write_text(CALLEE + '# tampered\n')
        with self.assertRaises(SystemExit):
            generator.declaration_for(self.root)

    def test_changed_pin_is_not_resolved(self):
        self.caller.write_text(self.caller.read_text().replace(PIN, 'b' * 40))
        self.assertEqual(generator.declaration_for(self.root)['reusableWorkflowCallers'], ['CI'])

    def test_flow_callers_are_not_misreported_as_direct_checks(self):
        self.caller.write_text(f'on: [pull_request]\njobs:\n  ci: {{uses: {USES}}}\n')
        with self.assertRaises(SystemExit):
            generator.declaration_for(self.root)
        with self.assertRaises(SystemExit):
            checker.workflow_job_names(self.caller)

    def test_closed_only_reusable_caller_never_gates_pre_merge(self):
        self.caller.write_text(f'on:\n  pull_request:\n    types: [closed]\njobs:\n  release:\n    uses: {USES}\n')
        self.assertIsNone(generator.declaration_for(self.root))
        self.assertEqual(checker.workflow_job_names(self.caller), [])

    def test_script_text_is_not_a_reusable_workflow_caller(self):
        self.caller.write_text(f'on: [pull_request]\njobs:\n  test:\n    runs-on: ubuntu-latest\n    steps:\n      - run: echo "uses: {USES}"\n')
        self.assertEqual(checker.workflow_job_names(self.caller), ['test'])
        self.assertEqual(generator.declaration_for(self.root)['requiredChecks'][0]['name'], 'test')

    def test_unsupported_quoted_uses_field_refuses(self):
        self.caller.write_text(self.caller.read_text().replace('uses:', '"uses":'))
        with self.assertRaises(SystemExit):
            generator.declaration_for(self.root)
        with self.assertRaises(SystemExit):
            checker.workflow_job_names(self.caller)

    def test_local_reusable_call_is_unresolved_until_supported(self):
        self.caller.write_text('on: [pull_request]\njobs:\n  ci:\n    uses: ./.github/workflows/test.yml\n')
        self.assertEqual(generator.declaration_for(self.root)['reusableWorkflowCallers'], ['ci'])
        with self.assertRaises(SystemExit):
            checker.workflow_job_names(self.caller)

    def test_unsafe_source_paths_refuse(self):
        for path in ['../outside.yml', '/tmp/outside.yml', '.github/workflows/ci.yml']:
            with self.subTest(path=path):
                self.entry['sourceFile'] = path
                self.write_lock()
                with self.assertRaises(SystemExit):
                    generator.declaration_for(self.root)

    def test_symlinked_source_refuses(self):
        original = self.root / 'original.yml'
        self.source.rename(original)
        self.source.symlink_to(original)
        with self.assertRaises(SystemExit):
            generator.declaration_for(self.root)

    def test_unsupported_callee_shapes_refuse(self):
        variants = [CALLEE.replace('name: Linux tests', 'name: ${{ matrix.os }}'),
                    CALLEE.replace('runs-on:', 'strategy:\n      matrix: {os: [linux, windows]}\n    runs-on:'),
                    CALLEE.replace('runs-on: ubuntu-latest', f'uses: {USES}'),
                    CALLEE.replace('workflow_call:', 'push:'),
                    CALLEE.replace('runs-on:', 'if: false\n    runs-on:'),
                    CALLEE.replace('runs-on:', '"strategy": {matrix: {os: [linux, windows]}}\n    runs-on:'),
                    CALLEE.replace('runs-on:', 'runs-on: windows-latest\n    runs-on:'),
                    'on: push\n' + CALLEE,
                    CALLEE.replace('jobs:\n  test:', 'jobs: {test: {runs-on: ubuntu-latest}}\nnot_jobs:\n  test:'),
                    CALLEE + '  duplicate:\n    name: Linux tests\n    runs-on: ubuntu-latest\n']
        for content in variants:
            with self.subTest(content=content):
                self.install_source(content)
                with self.assertRaises(SystemExit):
                    generator.declaration_for(self.root)

    def test_duplicate_or_unknown_lock_fields_refuse(self):
        self.entry['approved'] = True
        self.write_lock()
        with self.assertRaises(SystemExit):
            generator.declaration_for(self.root)
        del self.entry['approved']
        self.lock.write_text(json.dumps({'schema': 'new-project.reusable-workflows/v1',
                                         'workflows': [self.entry, self.entry]}))
        with self.assertRaises(SystemExit):
            generator.declaration_for(self.root)
        self.lock.write_text('{"schema":"wrong","schema":"new-project.reusable-workflows/v1","workflows":[]}')
        with self.assertRaises(SystemExit):
            generator.declaration_for(self.root)

    def test_named_steps_do_not_become_jobs(self):
        self.install_source(CALLEE.replace('- run: true', '- name: Ignore this\n        uses: owner/action@main'))
        self.assertEqual(checker.workflow_job_names(self.caller), ['CI / Linux tests'])

    def test_actual_installer_and_installed_checker_share_resolver(self):
        source_root = self.root / 'fixture-standard'
        subprocess.run(['git', 'clone', '-q', '--no-hardlinks', str(ROOT), str(source_root)], check=True)
        changed = ['scripts/generate_required_checks.py', 'scripts/check_required_checks.py',
                   'governance/package-manifest.json', 'governance/reusable-workflows.schema.json']
        for relative in changed:
            shutil.copy2(ROOT / relative, source_root / relative)
        for repo in [source_root, self.root]:
            subprocess.run(['git', '-C', str(repo), 'config', 'user.name', 'Fixture'], check=True)
            subprocess.run(['git', '-C', str(repo), 'config', 'user.email', 'fixture@example.invalid'], check=True)
        subprocess.run(['git', '-C', str(source_root), 'add', *changed], check=True)
        subprocess.run(['git', '-C', str(source_root), 'commit', '-q', '--allow-empty', '-m', 'Fixture contract source'], check=True)
        revision = subprocess.check_output(['git', '-C', str(source_root), 'rev-parse', 'HEAD'], text=True).strip()
        for relative in ['README.md', 'VERSION', 'CHANGELOG.md', 'TODO.md', 'project/TICKETS.md']:
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('# Target-owned prerequisite\n')
        subprocess.run(['git', '-C', str(self.root), 'add', '.github', 'README.md',
                        'VERSION', 'CHANGELOG.md', 'TODO.md', 'project/TICKETS.md'], check=True)
        subprocess.run(['git', '-C', str(self.root), 'commit', '-q', '-m', 'Fixture product'], check=True)
        original = (self.lock.read_bytes(), self.source.read_bytes(), self.caller.read_bytes())
        command = [sys.executable, str(source_root / 'scripts/create_adoption_lock.py'),
                   '--target-root', str(self.root), '--source-revision', revision,
                   '--allow-unpublished-for-testing', '--bootstrap-native-adoption', '--upgrade']
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        checks = json.loads((self.root / '.governance/required-checks.json').read_text())
        self.assertIn('CI / Linux tests', [item['name'] for item in checks['requiredChecks']])
        result = subprocess.run([sys.executable, str(self.root / '.governance/check_required_checks.py'),
                                 '--root', str(self.root)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual((self.lock.read_bytes(), self.source.read_bytes(), self.caller.read_bytes()), original)
        self.assertTrue((self.root / '.governance/reusable-workflows.schema.json').is_file())

    def test_governance_display_name_cannot_hide_an_unknown_source(self):
        self.lock.unlink()
        self.caller.write_text(self.caller.read_text().replace('name: CI', 'name: governance'))
        spec = importlib.util.spec_from_file_location('unknown_source_adopter', ROOT / 'scripts/create_adoption_lock.py')
        adopter = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(adopter)
        payloads = {adopter.CHECKS_TARGET: json.dumps({'repository': 'unresolved/adopter'}).encode()}
        with self.assertRaises(SystemExit):
            adopter.project_inherited_required_checks(self.root, payloads)


if __name__ == '__main__':
    unittest.main()
