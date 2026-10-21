#!/usr/bin/env python3
"""Isolated bootstrap regressions; fixture pins convey no production authority."""
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
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / 'scripts'))
import governance_check


class SeedTest(unittest.TestCase):
    def cmd(self, *args, check=True, env=None):
        result = subprocess.run(args, cwd=self.target, capture_output=True, text=True,
                                env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1', **(env or {})})
        if check and result.returncode:
            self.fail(result.stdout + result.stderr)
        return result

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.target = Path(self.temp.name) / 'product'
        self.target.mkdir()
        self.cmd('git', 'init', '-q', '-b', 'main')
        self.cmd('git', 'config', 'user.name', 'Fixture')
        self.cmd('git', 'config', 'user.email', 'fixture@example.invalid')
        self.cmd('git', 'config', 'core.hooksPath', '.githooks')
        mapping = json.loads((ROOT / 'governance/package-manifest.json').read_text())
        managed = {}
        for row in mapping['files']:
            source = ROOT / row['source']
            target = self.target / row['target']
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
            target.chmod(0o755 if row['executable'] else 0o644)
            if row['strategy'] == 'managed':
                managed[row['target']] = hashlib.sha256(target.read_bytes()).hexdigest()
        for name, text in {'README.md': '# Product\n', 'VERSION': '0.1.0\n',
                           'CHANGELOG.md': '# Changes\n', 'TODO.md': '# Tasks\n',
                           'project/TICKETS.md': '# Tickets\n',
                           '.gitignore': '/.worktrees/\n/.subactor/receipts/\n/.subactor/leases/\n/.subactor/sessions/\n/.subactor/recovery/\n'}.items():
            target = self.target / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text)
        (self.target / '.governance/required-checks.json').write_text(json.dumps({
            'schema': 'new-project.required-checks/v1', 'repository': 'paxlet-com/fixture',
            'version': 1, 'requiredChecks': []}))
        lock = {'schema': 'new-project.lock/v1', 'standard': {
            'id': 'wellmanifest/new-project', 'sourceRepository': 'wellmanifest/new-project',
            'version': '0.20.109', 'sourceRevision': 'a' * 40,
            'publicationStatus': 'published'}, 'managedFiles': managed}
        (self.target / '.governance/manifest.lock.json').write_text(json.dumps(lock))
        names = [str(p.relative_to(self.target)) for p in self.target.rglob('*')
                 if p.is_file() and '.git' not in p.relative_to(self.target).parts]
        self.cmd('git', 'add', '--', *names)
        self.request = Path(self.temp.name) / 'request.json'
        self.payload = {'schema': 'new-project.seed-baseline-request/v1', 'root': str(self.target),
            'repositoryRef': 'paxlet-com/fixture', 'authorizationRef': 'authorization:session/fixture',
            'createRepository': True, 'execute': True, 'sourceRevision': 'a' * 40,
            'lockSha256': hashlib.sha256((self.target / '.governance/manifest.lock.json').read_bytes()).hexdigest(),
            'seedProfileRef': 'seed-profile:new-project-native', 'ownerActor': 'agent:fixture',
            'ownerSession': 'fixture-seed-session', 'files': {
                name: hashlib.sha256((self.target / name).read_bytes()).hexdigest() for name in names}}
        self.save_request()

    def save_request(self):
        self.request.write_text(json.dumps(self.payload))

    def allocate(self, check=False):
        result = self.cmd('bash', 'project/new-ticket.sh', '--title', 'First product task',
                        '--agent', 'fixture', '--writer-actor', 'agent:fixture',
                        '--writer-session', 'fixture-seed-session', '--workstream', 'application',
                        '--path', 'src/**', '--seed-baseline-request', str(self.request),
                        '--worktree-slug', 'first-product', check=check)
        if result.returncode:
            output = result.stdout + result.stderr
            self.assertNotIn('Traceback (most recent call last)', output)
            self.assertTrue('"status": "refused"' in output or 'GOV-' in output, output)
        return result

    def unborn(self):
        self.assertNotEqual(self.cmd('git', 'rev-parse', '--verify', 'HEAD', check=False).returncode, 0)

    def test_real_first_seed_and_canonical_allocation_then_refuse_second_seed(self):
        self.allocate(check=True)
        receipt = json.loads((self.target / '.subactor/receipts/seed-baseline.json').read_text())
        head = self.cmd('git', 'rev-parse', 'HEAD').stdout.strip()
        self.assertEqual(receipt['baselineSha'], head)
        self.assertEqual(self.cmd('git', 'rev-list', '--all', '--count').stdout.strip(), '1')
        checkout = self.target / '.worktrees/ticket-001--first-product'
        self.assertTrue((checkout / 'project/ticket-001/intent.json').is_file())
        self.assertFalse(Path((checkout / '.git').read_text().strip().removeprefix('gitdir: ')).is_absolute())
        self.assertEqual(self.cmd('git', 'config', '--get', 'core.hooksPath').stdout.strip(), '.githooks')
        self.assertFalse((self.target / 'src').exists())
        lease = json.loads((self.target / '.subactor/leases/ticket-001--first-product.json').read_text())
        self.assertEqual((lease['ownerActor'], lease['ownerSession']), ('agent:fixture', 'fixture-seed-session'))
        self.assertEqual(lease['headSha'], head)
        self.assertNotEqual(self.allocate().returncode, 0)
        self.assertEqual(self.cmd('git', 'rev-parse', 'HEAD').stdout.strip(), head)

    def test_ordinary_root_commit_and_unprepared_seed_cannot_skip_the_hook(self):
        self.assertNotEqual(self.cmd('git', 'commit', '-m', 'unauthorized', check=False).returncode, 0)
        self.unborn()
        env = {'NEW_PROJECT_SEED_REQUEST': str(self.request), 'NEW_PROJECT_WRITER_ACTOR': 'agent:fixture',
               'NEW_PROJECT_WRITER_SESSION': 'fixture-seed-session'}
        self.assertNotEqual(self.cmd('git', 'commit', '-m', 'unprepared', check=False, env=env).returncode, 0)
        self.unborn()

    def test_refuse_missing_authority_and_wrong_owner_before_reservation(self):
        for field, value in [('createRepository', False), ('execute', False),
                             ('authorizationRef', ''), ('ownerActor', 'agent:other'),
                             ('ownerSession', 'different'), ('lockSha256', '0' * 64)]:
            with self.subTest(field=field):
                previous = self.payload[field]
                self.payload[field] = value
                self.save_request()
                self.assertNotEqual(self.allocate().returncode, 0)
                self.unborn()
                self.assertFalse((self.target / '.git/new-project-ticket-high-water').exists())
                self.payload[field] = previous
        self.save_request()

    def test_refuse_unknown_product_and_untracked_paths(self):
        source = self.target / 'product.py'
        source.write_text('print("implementation")\n')
        self.assertNotEqual(self.allocate().returncode, 0)
        (self.target / '.git/info/exclude').write_text('/product.py\n')
        self.assertNotEqual(self.allocate().returncode, 0)
        (self.target / '.git/info/exclude').write_text('')
        self.cmd('git', 'add', 'product.py')
        self.payload['files']['product.py'] = hashlib.sha256(source.read_bytes()).hexdigest()
        self.save_request()
        self.assertNotEqual(self.allocate().returncode, 0)
        self.unborn()

    def test_refuse_secret_even_in_an_authorized_document(self):
        readme = self.target / 'README.md'
        readme.write_text('ghp_' + 'A' * 40 + '\n')
        self.cmd('git', 'add', 'README.md')
        self.payload['files']['README.md'] = hashlib.sha256(readme.read_bytes()).hexdigest()
        self.save_request()
        self.assertNotEqual(self.allocate().returncode, 0)
        self.unborn()

    def test_refuse_symlink_and_disabled_hook(self):
        self.cmd('git', 'config', 'core.hooksPath', 'elsewhere')
        self.assertNotEqual(self.allocate().returncode, 0)
        self.cmd('git', 'config', 'core.hooksPath', '.githooks')
        path = self.target / 'README.md'
        path.unlink()
        path.symlink_to(self.request)
        self.cmd('git', 'add', 'README.md')
        self.assertNotEqual(self.allocate().returncode, 0)
        self.unborn()

    def test_refuse_index_drift_and_existing_remote(self):
        path = self.target / 'README.md'
        path.write_text('# Changed since request\n')
        self.assertNotEqual(self.allocate().returncode, 0)
        path.write_text('# Product\n')
        self.cmd('git', 'remote', 'add', 'origin', 'https://github.com/paxlet-com/fixture.git')
        self.assertNotEqual(self.allocate().returncode, 0)
        self.unborn()


class PlacementTest(unittest.TestCase):
    def test_explicit_paxlet_owner_and_preserved_domain_boundary(self):
        self.assertIsNone(governance_check.placement_error({'home': 'paxlet-com',
            'runtimeOwner': 'paxlet-com', 'shape': 'runtime_service', 'adopt': ['wellmanifest/new-project']}))
        self.assertIsNotNone(governance_check.placement_error({'home': 'unknown', 'shape': 'runtime_service'}))
        self.assertIsNotNone(governance_check.placement_error({'home': 'wellmanifest', 'shape': 'runtime_service'}))
        self.assertIsNone(governance_check.placement_error({'home': 'wellmanifest', 'shape': 'domain_pack'}))
        schema = json.loads((ROOT / 'governance/intent.schema.json').read_text())
        for field in ('home', 'runtimeOwner'):
            self.assertIn('paxlet-com', schema['properties']['placement']['properties'][field]['enum'])


if __name__ == '__main__':
    unittest.main()
