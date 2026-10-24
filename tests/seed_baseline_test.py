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
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / 'scripts'))
import governance_check
import seed_baseline


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

    def preparation_fixture(self):
        # Model the allocator's state between preflight and prepare, without
        # invoking its commit/publication path in these rejection tests.
        self.ticket = 'ticket-001'
        directory = self.target / 'project' / self.ticket
        directory.mkdir()
        self.ticket_readme = directory / 'README.md'
        self.ticket_intent = directory / 'intent.json'
        self.ticket_readme.write_text('# First product task\n')
        self.ticket_intent.write_text(json.dumps({'ticket': self.ticket}))
        (self.target / '.git/new-project-ticket-high-water').write_text('1\n')
        (self.target / '.git/new-project-ticket-allocation.lock').mkdir()
        self.reservation = self.target / '.git/new-project-seed-reservation.json'

    def preparation_state(self):
        return (self.ticket_readme.read_bytes(), self.ticket_intent.read_bytes(),
                (self.target / '.git/index').read_bytes(),
                self.cmd('git', 'ls-files', '--stage', '-z').stdout,
                self.reservation.read_bytes() if self.reservation.exists() else None)

    def prepare(self):
        return seed_baseline.prepare(self.target, self.request, 'agent:fixture',
                                     'fixture-seed-session', self.ticket)

    def assert_preparation_refused(self, reason, *, unread_ticket=False):
        before = self.preparation_state()
        original_open = Path.open

        def guarded_open(path, *args, **kwargs):
            if unread_ticket and path in (self.ticket_readme, self.ticket_intent):
                self.fail('ticket content accessed before validation')
            return original_open(path, *args, **kwargs)

        with patch.object(Path, 'open', guarded_open):
            with self.assertRaisesRegex(seed_baseline.SeedError, reason):
                self.prepare()
        self.assertEqual(self.preparation_state(), before)
        self.unborn()

    def test_prepare_validates_request_before_ticket_content_access(self):
        self.preparation_fixture()
        cases = [('schema', 'unknown', 'request_shape'),
                 ('extra', True, 'request_shape'),
                 ('root', '/different', 'request_binding'),
                 ('createRepository', False, 'explicit_new_repository_authority_required'),
                 ('execute', False, 'explicit_new_repository_authority_required'),
                 ('authorizationRef', '', 'explicit_new_repository_authority_required'),
                 ('ownerActor', 'agent:other', 'writer_binding'),
                 ('ownerSession', 'other', 'writer_binding'),
                 ('repositoryRef', 'invalid', 'repository_binding'),
                 ('repositoryRef', 'paxlet-com/other', 'check_repository_binding'),
                 ('lockSha256', '0' * 64, 'adoption_lock_drift')]
        valid = dict(self.payload)
        for field, value, reason in cases:
            with self.subTest(field=field, value=value):
                self.payload = {**valid, field: value}
                self.save_request()
                self.assert_preparation_refused(reason, unread_ticket=True)

    def test_prepare_rejects_malformed_json_before_ticket_content_access(self):
        self.preparation_fixture()
        self.request.write_text('{')
        before = self.preparation_state()
        with patch.object(Path, 'read_text', side_effect=AssertionError('premature ticket read')):
            with self.assertRaises(json.JSONDecodeError):
                self.prepare()
        self.assertEqual(self.preparation_state(), before)

    def test_prepare_rejects_symlinked_ticket_components_before_content_access(self):
        self.preparation_fixture()
        paths = [self.target / 'project', self.ticket_readme.parent,
                 self.ticket_readme, self.ticket_intent]
        for number, path in enumerate(paths):
            with self.subTest(path=path.relative_to(self.target)):
                external = Path(self.temp.name) / f'external-{number}'
                path.rename(external)
                path.symlink_to(external, target_is_directory=external.is_dir())
                sentinels = list(external.rglob('*')) if external.is_dir() else [external]
                before = {p: p.read_bytes() for p in sentinels if p.is_file()}
                try:
                    self.assert_preparation_refused('symlink_path', unread_ticket=True)
                    self.assertEqual({p: p.read_bytes() for p in before}, before)
                finally:
                    path.unlink()
                    external.rename(path)

    def test_prepare_rejects_invalid_reservation_before_mutation(self):
        self.preparation_fixture()
        counter = self.target / '.git/new-project-ticket-high-water'
        counter.write_text('2\n')
        self.assert_preparation_refused('native_reservation_required', unread_ticket=True)
        counter.write_text('1\n')
        lock = self.target / '.git/new-project-ticket-allocation.lock'
        lock.rmdir()
        self.assert_preparation_refused('allocator_lock_required', unread_ticket=True)
        lock.mkdir()
        self.reservation.write_text('{"existing": true}\n')
        self.assert_preparation_refused('seed_already_reserved', unread_ticket=True)

    def test_prepare_rejects_invalid_intent_before_mutation(self):
        self.preparation_fixture()
        for intent in ({'ticket': 'ticket-002'}, {'ticket': self.ticket, 'delivery': {}}):
            with self.subTest(intent=intent):
                self.ticket_intent.write_text(json.dumps(intent))
                self.assert_preparation_refused('unborn_ticket_binding')

    def test_prepare_rejects_seed_drift_before_mutation(self):
        self.preparation_fixture()
        readme = self.target / 'README.md'
        readme.write_text('# Changed seed\n')
        self.assert_preparation_refused('index_worktree_drift')
        self.cmd('git', 'add', 'README.md')
        self.assert_preparation_refused('seed_content_drift')

    def test_prepare_rejects_extra_inventory_before_mutation(self):
        self.preparation_fixture()
        extra = self.ticket_readme.parent / 'extra.md'
        extra.write_text('not an allocator carrier\n')
        self.assert_preparation_refused('untracked_path', unread_ticket=True)
        # Ignoring the extra file does not hide it from the inventory check.
        (self.target / '.git/info/exclude').write_text('/project/ticket-001/extra.md\n')
        self.assert_preparation_refused('untracked_path', unread_ticket=True)
        self.cmd('git', 'add', '-f', str(extra))
        self.assert_preparation_refused('exact_seed_stage_required')

    def test_prepare_rejects_secret_carriers_before_mutation(self):
        self.preparation_fixture()
        self.ticket_readme.write_text('ghp_' + 'A' * 40 + '\n')
        self.assert_preparation_refused('secret_material')

    def test_prepare_accepts_exact_untracked_carriers_and_keeps_other_callers_strict(self):
        self.preparation_fixture()
        for operation in (seed_baseline.context, seed_baseline.preflight, seed_baseline.hook_check):
            with self.subTest(operation=operation.__name__):
                with self.assertRaisesRegex(seed_baseline.SeedError, 'untracked_path'):
                    operation(self.target, self.request, 'agent:fixture', 'fixture-seed-session')
        record = self.prepare()
        self.assertEqual(set(record['files']), set(self.payload['files']) | {
            'project/ticket-001/README.md', 'project/ticket-001/intent.json'})
        self.assertEqual(self.ticket_readme.read_text().count('SESSION_EXECUTION_AUTHORIZATION'), 1)
        self.assertEqual(json.loads(self.reservation.read_text()), record)
        self.assertEqual(seed_baseline.hook_check(self.target, self.request, 'agent:fixture',
                                                'fixture-seed-session'), record)
        self.assert_preparation_refused('seed_already_reserved', unread_ticket=True)

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
