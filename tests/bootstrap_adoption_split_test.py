"""Replay a committed mixed first bootstrap in a disposable clone."""
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import shutil
import sys
import unittest
from unittest.mock import patch

import scaffold_bootstrap_test as fixtures

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import bootstrap_adoption_split as controller


class BootstrapAdoptionSplitTest(unittest.TestCase):
    def setUp(self):
        fixture = fixtures.FreshBootstrapTest()
        self.addCleanup(fixture.doCleanups)
        with redirect_stdout(io.StringIO()):
            fixture.setUp()
        self.fixture, self.primary = fixture, fixture.target
        self.base = fixture.head
        self.product = 'docs/installer.sh'
        self.command(self.primary, 'git', 'remote', 'add', 'origin', 'https://github.com/example/bootstrap-fixture.git')
        self.command(self.primary, 'git', 'update-ref', 'refs/remotes/origin/main', self.base)
        result = fixture.integration_allocator(fixture.checksum(), extra=('docs/**',))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        allocation = json.loads(next(line for line in result.stdout.splitlines() if line.startswith('{')))
        self.root = Path(allocation['worktreePath'])
        self.lease = Path(allocation['leasePath'])
        self.intent = self.root / 'project/ticket-001/intent.json'
        receipt = self.load(fixture.receipt)
        self.files = set(receipt['files'])
        for name in self.files:
            (self.root / name).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(self.primary / name, self.root / name)
        # The fixture's temporary primary had the installer staging payload.
        # Real continuation starts from a clean seed checkout and its receipt.
        self.command(self.primary, 'git', 'reset', '--hard', self.base)
        self.command(self.primary, 'git', 'clean', '-fd')
        (self.root / self.product).parent.mkdir()
        (self.root / self.product).write_text('#!/bin/sh\nexit 0\n')
        (self.root / self.product).chmod(0o755)
        intent = self.load(self.intent)
        delivery = self.load(ROOT / 'project/ticket-468/intent.json')['delivery']
        delivery.update(acceptedBaseSha=self.base, standardAdoption={
            'sourceRepository': 'wellmanifest/new-project', 'fromRevision': None,
            'toRevision': receipt['sourceRevision']})
        intent['delivery'] = delivery
        self.write(self.intent, intent)
        self.git('add', '--', *sorted(self.files), self.product, str(self.intent.parent))
        # Recreate the old mixed commit here, before enabling the new controller.
        self.git('-c', 'core.hooksPath=/dev/null', 'commit', '--quiet', '-m', 'Original mixed commit')
        self.head = self.git('rev-parse', 'HEAD')
        branch = self.git('symbolic-ref', 'HEAD')
        lease = self.load(self.lease)
        lease['headSha'] = self.head
        self.write(self.lease, lease)
        self.bundle = fixture.base / 'preservation.bundle'
        self.git('bundle', 'create', str(self.bundle), branch, 'refs/heads/main')
        self.git('rm', '--', self.product)
        self.path = fixture.base / 'request.json'
        self.request = {
            'schema': 'new-project.bootstrap-adoption-split/v1', 'requestId': 'fixture-split',
            'ticket': 'ticket-001', 'headSha': self.head, 'baseSha': self.base,
            'leaseRevision': lease['leaseRevision'], 'fencingToken': lease['fencingToken'],
            'paths': [self.product], 'leaseSha256': self.sha(self.lease), 'intentSha256': self.sha(self.intent),
            'bootstrapReceiptSha256': self.sha(fixture.receipt), 'bundlePath': str(self.bundle),
            'bundleSha256': self.sha(self.bundle),
        }
        self.write(self.path, self.request)

    def command(self, root, *args):
        return self.fixture.command(root, *args).stdout.strip()

    def git(self, *args):
        return self.command(self.root, 'git', *args)

    @staticmethod
    def load(path):
        return json.loads(path.read_bytes())

    @staticmethod
    def write(path, value):
        path.write_bytes(controller.encoded(value))

    @staticmethod
    def sha(path):
        return controller.sha(path.read_bytes())

    def split(self, *, apply=False, session='fixture-integration-bootstrap'):
        return controller.split(self.root, self.path, 'agent:fixture', session, apply=apply)

    def assert_refusal(self, message, **kwargs):
        before = (self.lease.read_bytes(), self.intent.read_bytes(), self.git('status', '--short'))
        with self.assertRaisesRegex((PermissionError, ValueError), message):
            self.split(apply=True, **kwargs)
        self.assertEqual(before, (self.lease.read_bytes(), self.intent.read_bytes(), self.git('status', '--short')))

    def test_fenced_split_is_retryable_and_preserves_original_commit(self):
        before = self.load(self.lease)
        self.assertEqual(self.split()['status'], 'planned')
        self.assertEqual(self.load(self.lease), before)
        result = self.split(apply=True)
        self.assertEqual(self.split(apply=True), result)
        lease, intent = self.load(self.lease), self.load(self.intent)
        self.assertEqual((lease['workstream'], intent['workstream']), ('governance', 'governance'))
        self.assertEqual(set(intent['allowedPaths']), self.files | {'project/ticket-001/**'})
        self.assertEqual(lease['scopeHash'], controller.start.digest(intent['allowedPaths']))
        self.assertEqual(lease['planHash'], self.sha(self.intent))
        for key in ('expiresAt', 'ownerActor', 'ownerSession', 'branchRef', 'headSha'):
            self.assertEqual(lease[key], before[key])
        for key in ('leaseRevision', 'fencingToken'):
            self.assertEqual(lease[key], before[key] + 1)
        self.assertFalse(result['grantsMergeAuthority'])
        self.assertEqual(self.git('rev-parse', 'HEAD'), self.head)
        self.assertEqual(self.git('show', self.head + ':' + self.product), '#!/bin/sh\nexit 0')

    def test_wrong_owner_and_stale_fencing_are_refused(self):
        self.assert_refusal('current_fenced_owner_required', session='another-session')
        self.request['fencingToken'] += 1
        self.write(self.path, self.request)
        self.assert_refusal('current_fenced_owner_required')

    def test_product_refuses_unstaged_removals_and_invalid_backup(self):
        self.git('restore', '--staged', '--worktree', '--', self.product)
        self.assert_refusal('stage_only_the_exact_product_removals')
        self.git('rm', '--', self.product)
        self.request['bundleSha256'] = '0' * 64
        self.write(self.path, self.request)
        self.assert_refusal('bundle_digest_changed')

    def test_retry_recovers_a_lease_written_before_the_intent(self):
        original = controller.store.atomic_at

        def fail_intent(fd, path, data, **kwargs):
            if path == 'intent.json':
                raise OSError('fixture interruption')
            return original(fd, path, data, **kwargs)

        with patch.object(controller.store, 'atomic_at', side_effect=fail_intent):
            with self.assertRaisesRegex(OSError, 'fixture interruption'):
                self.split(apply=True)
        self.assertEqual(self.load(self.lease)['workstream'], 'governance')
        self.assertEqual(self.load(self.intent)['workstream'], 'integration')
        self.assertEqual(self.split(apply=True)['status'], 'amended')
        self.assertEqual(self.load(self.intent)['workstream'], 'governance')


if __name__ == '__main__':
    unittest.main()
