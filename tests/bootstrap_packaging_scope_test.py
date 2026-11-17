"""Real first-adoption scope correction under the allocating owner."""
from contextlib import redirect_stdout
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import shutil
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tests'))
import scaffold_bootstrap_test as fixtures


class PackagingScopeTest(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.BootstrapTest()
        with redirect_stdout(io.StringIO()):
            self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.primary = self.fixture.target
        self.git = lambda *args: self.fixture.command(self.primary, 'git', *args).stdout.strip()
        # Only this test's disposable fixture is reset; no production paths.
        self.git('reset', '--hard', 'HEAD')
        self.git('clean', '-fdx')
        (self.primary / 'pyproject.toml').write_text('[project]\nname = "fixture"\nversion = "0.1.0"\n')
        self.git('add', 'pyproject.toml')
        self.git('commit', '--quiet', '-m', 'Existing Python package')
        self.head = self.git('rev-parse', 'HEAD')
        package_files = ('scripts/bootstrap_packaging_scope.py', 'governance/package-manifest.json',
                         'VERSION', 'governance/manifest.default.json', 'governance/manifest.hub.json',
                         'packages/wellman/pyproject.toml')
        for name in package_files:
            shutil.copy2(ROOT / name, self.fixture.source / name)
        self.fixture.command(self.fixture.source, 'git', 'add', *package_files)
        self.fixture.command(self.fixture.source, 'git', 'commit', '--quiet', '--allow-empty', '-m', 'Packaging controller fixture')
        self.revision = self.fixture.command(self.fixture.source, 'git', 'rev-parse', 'HEAD').stdout.strip()
        self.install(self.primary)
        receipt = json.loads((self.primary / '.subactor/receipts/bootstrap-adoption.json').read_text())
        args = ['bash', './project/new-ticket.sh', '--title', 'Packaging fixture', '--agent', 'fixture',
                '--writer-actor', 'agent:fixture', '--writer-session', 'scope-test',
                '--workstream', 'governance', '--worktree-slug', 'packaging-fixture',
                '--bootstrap-adoption-digest', self.fixture.checksum()]
        for name in receipt['files']:
            args += ['--path', name]
        self.fixture.command(self.primary, *args)
        self.root = self.primary / '.worktrees/ticket-001--packaging-fixture'
        self.install(self.root)
        self.intent = self.root / 'project/ticket-001/intent.json'
        value = json.loads(self.intent.read_text())
        value['delivery'] = {'acceptedBaseSha': self.head, 'targetBranch': 'main',
                             'standardAdoption': {'sourceRepository': 'wellmanifest/new-project',
                                 'fromRevision': None, 'toRevision': self.revision}}
        self.intent.write_text(json.dumps(value, indent=2) + '\n')
        self.lease = self.primary / '.subactor/leases/ticket-001--packaging-fixture.json'
        self.receipt = self.root / '.subactor/receipts/bootstrap-adoption.json'
        self.request_path = self.fixture.base / 'scope-request.json'
        self.request = {'schema': 'new-project.bootstrap-packaging-scope/v1', 'requestId': 'packaging-test',
                        'ticket': 'ticket-001', 'headSha': self.head, 'paths': ['pyproject.toml'],
                        'leaseRevision': 1, 'fencingToken': 1,
                        'leaseSha256': self.sha(self.lease), 'intentSha256': self.sha(self.intent),
                        'bootstrapReceiptSha256': self.sha(self.receipt)}
        self.save()
        self.before = {'lease': self.lease.read_bytes(), 'intent': self.intent.read_bytes(),
                       'package': (self.root / 'pyproject.toml').read_bytes()}

    def install(self, root):
        for name in ('VERSION', 'CHANGELOG.md', 'TODO.md', 'project/TICKETS.md'):
            p = root / name
            if not p.exists():
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text('0.1.0\n' if name == 'VERSION' else '# Fixture\n')
        args = ['adopter', '--target-root', str(root), '--source-revision', self.revision,
                '--migrate-wellman-scaffold', '--upgrade']
        with patch.object(sys, 'argv', args), patch.object(self.fixture.adopter, 'verify_publication_evidence'), redirect_stdout(io.StringIO()):
            self.assertEqual(self.fixture.adopter.main(), 0)

    @staticmethod
    def sha(path):
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def save(self):
        self.request_path.write_text(json.dumps(self.request))

    def module(self):
        spec = importlib.util.spec_from_file_location('scope_controller', ROOT / 'scripts/bootstrap_packaging_scope.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def amend(self, **kwargs):
        return self.module().amend(self.root, self.request_path,
                                   kwargs.pop('actor', 'agent:fixture'), kwargs.pop('session', 'scope-test'), **kwargs)

    def assert_refused(self, **kwargs):
        lease, intent = self.lease.read_bytes(), self.intent.read_bytes()
        with self.assertRaises((PermissionError, ValueError, OSError)):
            self.amend(**kwargs)
        self.assertEqual(self.lease.read_bytes(), lease)
        self.assertEqual(self.intent.read_bytes(), intent)

    def test_live_owner_adds_only_packaging_scope_and_preserves_expiry_and_source(self):
        result = self.amend(apply=True)
        old = json.loads(self.before['lease']); new = json.loads(self.lease.read_text())
        intent = json.loads(self.intent.read_text())
        self.assertEqual(intent['allowedPaths'][-1], 'pyproject.toml')
        self.assertEqual(intent['allowedPaths'][:-1], json.loads(self.before['intent'])['allowedPaths'])
        self.assertEqual(new['scopeHash'], hashlib.sha256(json.dumps(intent['allowedPaths'], sort_keys=True, separators=(',', ':')).encode()).hexdigest())
        self.assertEqual((new['leaseRevision'], new['fencingToken']), (2, 2))
        self.assertEqual(new['expiresAt'], old['expiresAt'])
        self.assertEqual(new['ownerSession'], old['ownerSession'])
        self.assertEqual((self.root / 'pyproject.toml').read_bytes(), self.before['package'])
        self.assertFalse(result['grantsMergeAuthority'])
        self.assertEqual(self.amend(apply=True)['writerEnvironment'], result['writerEnvironment'])

    def test_plan_is_read_only(self):
        self.assertEqual(self.amend(apply=False)['status'], 'planned')
        result = self.fixture.command(self.root, sys.executable,
            '.governance/bootstrap_packaging_scope.py', '--root', str(self.root),
            '--request', str(self.request_path), '--actor', 'agent:fixture', '--session', 'scope-test')
        self.assertEqual(json.loads(result.stdout)['status'], 'planned')
        self.assertEqual(self.lease.read_bytes(), self.before['lease'])
        self.assertEqual(self.intent.read_bytes(), self.before['intent'])
        self.assertFalse((self.primary / '.subactor/receipts/bootstrap-packaging-scope').exists())

    def test_wrong_actor_and_session_are_refused(self):
        self.assert_refused(actor='agent:other', apply=True)
        self.assert_refused(session='other-session', apply=True)

    def test_stale_lease_and_intent_cas_are_refused(self):
        for key in ('leaseSha256', 'intentSha256', 'bootstrapReceiptSha256'):
            old = self.request[key]; self.request[key] = '0' * 64; self.save()
            self.assert_refused(apply=True)
            self.request[key] = old

    def test_arbitrary_duplicate_and_wildcard_paths_are_refused(self):
        for paths in (['auth.py'], ['pyproject.toml', 'pyproject.toml'], ['*.toml'], ['../pyproject.toml'], []):
            self.request['paths'] = paths; self.save(); self.assert_refused(apply=True)

    def test_packaging_source_changes_are_refused(self):
        (self.root / 'pyproject.toml').write_text('[project]\nname="changed"\n')
        self.assert_refused(apply=True)

    def test_expired_and_frozen_owner_is_refused(self):
        old = json.loads(self.before['lease'])
        for field, value in (('expiresAt', '2000-01-01T00:00:00Z'), ('phase', 'publication_frozen')):
            current = dict(old); current[field] = value
            if field == 'phase': current['publicationFrozen'] = True
            self.lease.write_text(json.dumps(current)); self.request['leaseSha256'] = self.sha(self.lease); self.save()
            self.assert_refused(apply=True)

    def test_contract_drift_and_receipt_drift_are_refused(self):
        path = self.root / '.governance/agent-hosts.json'
        raw = path.read_bytes(); path.write_bytes(raw + b'\n')
        self.assert_refused(apply=True); path.write_bytes(raw)
        value = json.loads(self.receipt.read_text()); value['sourceRevision'] = '0' * 40
        self.receipt.write_text(json.dumps(value)); self.request['bootstrapReceiptSha256'] = self.sha(self.receipt); self.save()
        self.assert_refused(apply=True)

    def test_rewritten_target_pin_cannot_turn_product_source_into_packaging(self):
        contract_path = self.root / '.governance/agent-hosts.json'
        contract = json.loads(contract_path.read_text())
        contract['packaging']['python']['marker'] = 'foreign.txt'
        contract_path.write_text(json.dumps(contract))
        lock_path = self.root / '.governance/manifest.lock.json'
        lock = json.loads(lock_path.read_text())
        lock['managedFiles']['.governance/agent-hosts.json'] = self.sha(contract_path)
        lock_path.write_text(json.dumps(lock))
        receipt = json.loads(self.receipt.read_text())
        receipt['files']['.governance/agent-hosts.json'] = self.sha(contract_path)
        receipt['files']['.governance/manifest.lock.json'] = self.sha(lock_path)
        self.receipt.write_text(json.dumps(receipt))
        self.request.update(paths=['foreign.txt'], bootstrapReceiptSha256=self.sha(self.receipt)); self.save()
        self.assert_refused(apply=True)
        result = self.fixture.command(self.root, sys.executable,
            '.governance/bootstrap_packaging_scope.py', '--root', str(self.root),
            '--request', str(self.request_path), '--actor', 'agent:fixture', '--session', 'scope-test',
            '--apply', check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.lease.read_bytes(), self.before['lease'])
        self.assertEqual(self.intent.read_bytes(), self.before['intent'])

    def test_changed_head_is_refused(self):
        self.request['headSha'] = '0' * 40; self.save(); self.assert_refused(apply=True)
        self.request['headSha'] = self.head
        lease = json.loads(self.before['lease']); lease['headSha'] = '0' * 40
        self.lease.write_text(json.dumps(lease)); self.request['leaseSha256'] = self.sha(self.lease); self.save()
        self.assert_refused(apply=True)

    def test_clone_allocator_lock_serializes_scope_effect(self):
        lock = self.primary / '.git/new-project-ticket-allocation.lock'
        lock.mkdir()
        try:
            self.assert_refused(apply=True)
            self.assertTrue(lock.is_dir())
        finally:
            lock.rmdir()
        module = self.module(); original = module.transaction
        def observed(*args, **kwargs):
            self.assertTrue(lock.is_dir())
            with self.assertRaises(FileExistsError):
                lock.mkdir()
            return original(*args, **kwargs)
        with patch.object(module, 'transaction', side_effect=observed):
            module.amend(self.root, self.request_path, 'agent:fixture', 'scope-test', apply=True)
        self.assertFalse(lock.exists())

    def test_interrupted_fencing_resumes_once_and_rejects_later_lease_change(self):
        module = self.module()
        original = module.store.atomic_at
        def interrupt(fd, name, value, **kwargs):
            if name == 'intent.json':
                raise OSError('simulated interruption after fencing')
            return original(fd, name, value, **kwargs)
        with patch.object(module.store, 'atomic_at', side_effect=interrupt):
            with self.assertRaisesRegex(OSError, 'simulated interruption'):
                module.amend(self.root, self.request_path, 'agent:fixture', 'scope-test', apply=True)
        self.assertEqual(json.loads(self.lease.read_bytes())['fencingToken'], 2)
        self.assertEqual(self.intent.read_bytes(), self.before['intent'])
        self.assertEqual(self.amend(apply=True)['fencingToken'], 2)
        lease = json.loads(self.lease.read_bytes())
        lease['leaseRevision'] += 1; lease['fencingToken'] += 1
        self.lease.write_text(json.dumps(lease))
        self.assert_refused(apply=True)

    def test_foreign_primary_edit_is_contested(self):
        path = self.primary / 'pyproject.toml'
        path.write_text(path.read_text() + '# foreign change\n')
        with self.assertRaisesRegex(PermissionError, 'packaging_scope_contested'):
            self.amend(apply=True)
        self.assertEqual(self.lease.read_bytes(), self.before['lease'])
        self.assertEqual(self.intent.read_bytes(), self.before['intent'])

    def test_registered_peer_reservation_is_contested(self):
        peer = self.primary / '.worktrees/ticket-002--peer'
        self.git('worktree', 'add', '--relative-paths', '-b', 'ticket/002-peer', str(peer), 'HEAD')
        ticket = peer / 'project/ticket-002'; ticket.mkdir(parents=True)
        intent = json.loads(self.before['intent'])
        intent.update(ticket='ticket-002', allowedPaths=['pyproject.toml'])
        (ticket / 'intent.json').write_text(json.dumps(intent))
        (ticket / 'README.md').write_text('# Peer\n\n- **Status**: IN_PROGRESS\n')
        self.assert_refused(apply=True)
        self.assertEqual(json.loads((ticket / 'intent.json').read_text()), intent)

    def test_symlink_and_hardlink_marker_are_refused(self):
        path = self.root / 'pyproject.toml'
        external = self.fixture.base / 'external-package.toml'
        external.write_bytes(path.read_bytes())
        path.unlink(); path.symlink_to(external)
        self.assert_refused(apply=True)
        path.unlink(); path.hardlink_to(external)
        self.assert_refused(apply=True)
        self.assertEqual(external.read_bytes(), self.before['package'])

    def test_source_drift_after_prepare_is_refused_without_scope_write(self):
        module = self.module()
        original = module.store.atomic_at
        def drift(fd, name, value, **kwargs):
            result = original(fd, name, value, **kwargs)
            if name.endswith('.prepared'):
                path = self.root / 'pyproject.toml'
                path.write_text(path.read_text() + '# raced edit\n')
            return result
        with patch.object(module.store, 'atomic_at', side_effect=drift):
            with self.assertRaisesRegex(PermissionError, 'packaging_source_changed'):
                module.amend(self.root, self.request_path, 'agent:fixture', 'scope-test', apply=True)
        self.assertEqual(self.lease.read_bytes(), self.before['lease'])
        self.assertEqual(self.intent.read_bytes(), self.before['intent'])


if __name__ == '__main__':
    unittest.main()
