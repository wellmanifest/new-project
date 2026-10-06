"""A bootstrap plan describes future CI; it never edits the target caller."""
import base64
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
CALLEE = b'on:\n  workflow_call:\njobs:\n  test:\n    name: Linux tests\n    runs-on: ubuntu-latest\n    steps:\n      - run: true\n'
PIN = 'a' * 40
ORIGINAL = 'owner/ci/.github/workflows/test.yml@main'
USES = ORIGINAL.replace('@main', '@' + PIN)


def load(path):
    spec = importlib.util.spec_from_file_location('bootstrap_plan_adopter', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class BootstrapReusablePlanTest(unittest.TestCase):
    def command(self, root, *args, check=True):
        result = subprocess.run(args, cwd=root, capture_output=True, text=True,
                                env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
        if check and result.returncode:
            self.fail(result.stdout + result.stderr)
        return result

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.target = self.base / 'product'
        self.command(self.base, 'git', 'init', '-q', '-b', 'main', str(self.target))
        self.command(self.target, 'git', 'config', 'user.name', 'Fixture')
        self.command(self.target, 'git', 'config', 'user.email', 'fixture@example.invalid')
        self.command(self.target, 'git', 'remote', 'add', 'origin', 'https://github.com/owner/product.git')
        self.caller = self.target / '.github/workflows/ci.yml'
        self.caller.parent.mkdir(parents=True)
        self.original = f'on: [pull_request]\njobs:\n  ci:\n    name: CI\n    uses: {ORIGINAL}\n'.encode()
        self.caller.write_bytes(self.original)
        for rel in ['README.md', 'VERSION', 'CHANGELOG.md', 'TODO.md', 'project/TICKETS.md']:
            path = self.target / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('0.1.0\n' if rel == 'VERSION' else '# Product\n')
        self.command(self.target, 'git', 'add', '.')
        self.command(self.target, 'git', 'commit', '-q', '-m', 'Fixture product')
        self.head = self.command(self.target, 'git', 'rev-parse', 'HEAD').stdout.strip()
        self.plan = self.base / 'plan.json'
        self.document = {
            'schema': 'new-project.bootstrap-reusable-plan/v1',
            'baseSha': self.head, 'callerFile': '.github/workflows/ci.yml',
            'callerSha256': hashlib.sha256(self.original).hexdigest(),
            'originalUses': ORIGINAL, 'uses': USES,
            'sourceFile': '.github/reusable-workflows/test.yml',
            'sourceSha256': hashlib.sha256(CALLEE).hexdigest(),
            'sourceBase64': base64.b64encode(CALLEE).decode(),
        }
        self.plan.write_text(json.dumps(self.document))
        self.adopter = load(ROOT / 'scripts/create_adoption_lock.py')

    def resolve(self):
        return self.adopter.bootstrap_reusable_declaration(self.target, {}, self.plan)

    def test_offline_plan_resolves_without_changing_target(self):
        declaration = self.resolve()
        self.assertEqual(declaration['repository'], 'owner/product')
        self.assertEqual(declaration['requiredChecks'][0]['name'], 'CI / Linux tests')
        self.assertEqual(self.caller.read_bytes(), self.original)
        self.assertFalse((self.target / self.document['sourceFile']).exists())
        self.assertFalse((self.target / '.github/reusable-workflows.lock.json').exists())
        self.assertEqual(self.command(self.target, 'git', 'status', '--porcelain').stdout, '')

    def test_invalid_or_unbound_plans_refuse(self):
        variants = [
            {'baseSha': 'b' * 40}, {'callerSha256': '0' * 64},
            {'callerFile': '../outside.yml'}, {'callerFile': '.github/workflows/absent.yml'},
            {'uses': ORIGINAL}, {'uses': 'different/ci/.github/workflows/test.yml@' + PIN},
            {'originalUses': ORIGINAL.replace('@main', '@other')},
            {'sourceFile': '../outside.yml'}, {'sourceSha256': '0' * 64},
            {'sourceBase64': 'invalid !'}, {'sourceBase64': base64.b64encode(b'not a workflow').decode()},
            {'approval': True}, {'schema': 'unknown'},
        ]
        for changes in variants:
            with self.subTest(changes=changes):
                document = copy.deepcopy(self.document)
                document.update(changes)
                self.plan.write_text(json.dumps(document))
                with self.assertRaises(SystemExit):
                    self.resolve()
                self.assertEqual(self.caller.read_bytes(), self.original)

    def test_uncommitted_caller_and_existing_contract_refuse(self):
        self.caller.write_bytes(self.original + b'# another writer\n')
        self.document['callerSha256'] = hashlib.sha256(self.caller.read_bytes()).hexdigest()
        self.plan.write_text(json.dumps(self.document))
        with self.assertRaises(SystemExit):
            self.resolve()
        self.caller.write_bytes(self.original)
        self.document['callerSha256'] = hashlib.sha256(self.original).hexdigest()
        self.plan.write_text(json.dumps(self.document))
        (self.target / '.github/reusable-workflows.lock.json').write_text('{}')
        with self.assertRaises(SystemExit):
            self.resolve()

    def test_duplicate_keys_and_symlinked_plan_refuse(self):
        raw = self.plan.read_text()
        self.plan.write_text(raw[:-1] + ', "baseSha": "' + self.head + '"}')
        with self.assertRaises(SystemExit):
            self.resolve()
        self.plan.write_text(raw)
        other = self.base / 'other-plan.json'
        self.plan.rename(other)
        self.plan.symlink_to(other)
        with self.assertRaises(SystemExit):
            self.resolve()

    def test_plan_requires_explicit_fresh_bootstrap(self):
        result = self.command(ROOT, sys.executable, 'scripts/create_adoption_lock.py',
                              '--target-root', str(self.target), '--source-revision', self.head,
                              '--bootstrap-reusable-plan', str(self.plan), '--check', check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('requires explicit fresh native bootstrap', result.stderr)
        self.assertEqual(self.command(self.target, 'git', 'status', '--porcelain').stdout, '')

    def test_managed_workflow_overlap_refuses(self):
        with self.assertRaises(SystemExit):
            self.adopter.bootstrap_reusable_declaration(
                self.target, {self.document['callerFile']: b'managed workflow'}, self.plan)
        self.assertEqual(self.caller.read_bytes(), self.original)

    def test_multiple_callers_and_internal_plan_refuse(self):
        original_plan = self.plan
        self.plan = self.target / 'plan.json'
        self.plan.write_text(json.dumps(self.document))
        with self.assertRaises(SystemExit):
            self.resolve()
        self.plan.unlink()
        self.plan = original_plan
        self.caller.write_bytes(self.original + f'  other:\n    uses: {ORIGINAL}\n'.encode())
        self.command(self.target, 'git', 'add', '.')
        self.command(self.target, 'git', 'commit', '-q', '-m', 'Fixture two callers')
        self.document['baseSha'] = self.command(self.target, 'git', 'rev-parse', 'HEAD').stdout.strip()
        self.document['callerSha256'] = hashlib.sha256(self.caller.read_bytes()).hexdigest()
        self.plan.write_text(json.dumps(self.document))
        with self.assertRaises(SystemExit):
            self.resolve()

    def test_installer_and_real_first_allocation_preserve_caller(self):
        source = self.base / 'standard'
        self.command(self.base, 'git', 'clone', '-q', '--no-hardlinks', str(ROOT), str(source))
        shutil.copy2(ROOT / 'scripts/create_adoption_lock.py', source / 'scripts/create_adoption_lock.py')
        self.command(source, 'git', 'config', 'user.name', 'Fixture')
        self.command(source, 'git', 'config', 'user.email', 'fixture@example.invalid')
        self.command(source, 'git', 'add', 'scripts/create_adoption_lock.py')
        self.command(source, 'git', 'commit', '-q', '--allow-empty', '-m', 'Fixture source')
        revision = self.command(source, 'git', 'rev-parse', 'HEAD').stdout.strip()
        module = load(source / 'scripts/create_adoption_lock.py')
        args = ['adopter', '--target-root', str(self.target), '--source-revision', revision,
                '--bootstrap-native-adoption', '--bootstrap-reusable-plan', str(self.plan), '--upgrade']
        with patch.object(sys, 'argv', args), patch.object(module, 'verify_publication_evidence'):
            self.assertEqual(module.main(), 0)
        self.assertEqual(self.caller.read_bytes(), self.original)
        owned = json.loads((self.target / '.governance/manifest.json').read_text())['coordination']['workstreams']['governance']['ownedPaths']
        planned_paths = [self.document['callerFile'], self.document['sourceFile'],
                         '.github/reusable-workflows.lock.json']
        self.assertTrue(all(path in owned for path in planned_paths))
        self.assertNotIn('.github/**', owned)
        scope = ['--path', '.governance/**']
        for path in planned_paths:
            scope.extend(['--path', path])
        checker = self.command(self.target, 'python3', '.governance/check_required_checks.py',
                               '--root', '.', check=False)
        self.assertNotEqual(checker.returncode, 0, 'planned CI is not yet verified actual CI')
        observed = self.command(self.target, 'python3', '.governance/work_start_check.py',
                                '--root', '.', '--workstream', 'governance',
                                *scope,
                                '--allocation-check', check=False)
        dirty = json.loads(observed.stdout)['worktrees'][0]['dirtyDigest']
        self.command(self.target, 'bash', 'project/new-ticket.sh', '--title', 'Adopt immutable CI',
                     '--agent', 'fixture', '--workstream', 'governance', *scope,
                     '--worktree-slug', 'immutable-ci',
                     '--bootstrap-adoption-digest', dirty)
        wt = self.target / '.worktrees/ticket-001--immutable-ci'
        self.assertTrue((wt / 'project/ticket-001/intent.json').is_file())
        self.assertEqual((wt / '.github/workflows/ci.yml').read_bytes(), self.original)
        self.assertEqual(self.caller.read_bytes(), self.original)
        self.assertEqual(self.command(wt, 'git', 'rev-parse', 'HEAD').stdout.strip(), self.head)
        # Only the isolated fixture implements the accepted future plan after allocation.
        (wt / '.github/workflows/ci.yml').write_bytes(self.original.replace(ORIGINAL.encode(), USES.encode()))
        callee = wt / self.document['sourceFile']
        callee.parent.mkdir(parents=True)
        callee.write_bytes(CALLEE)
        entry = {key: self.document[key] for key in ['uses', 'sourceFile', 'sourceSha256']}
        (wt / '.github/reusable-workflows.lock.json').write_text(json.dumps({
            'schema': 'new-project.reusable-workflows/v1', 'workflows': [entry]}))
        args = ['adopter', '--target-root', str(wt), '--source-revision', revision, '--upgrade']
        with patch.object(sys, 'argv', args), patch.object(module, 'verify_publication_evidence'):
            self.assertEqual(module.main(), 0)
        self.command(wt, 'python3', '.governance/check_required_checks.py', '--root', '.')
        self.assertEqual(self.caller.read_bytes(), self.original)


if __name__ == '__main__':
    unittest.main()
