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
        subprocess.run(['git', '-C', str(source_root), 'commit', '-q', '-m', 'Fixture contract source'], check=True)
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


if __name__ == '__main__':
    unittest.main()
