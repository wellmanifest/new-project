"""Actual Git terminal ownership, CAS and interrupted local controller writes."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / (name + '.py'))
    value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value
    spec.loader.exec_module(value)
    return value


release = module('terminal_lease_release')
activity = module('ticket_activity')
canonical = module('change_lease_check')


@unittest.skipUnless(os.name == 'posix', 'POSIX local controller adapter; unsupported hosts tested separately')
class TerminalOwnerRelease(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'repo'
        self.root.mkdir()
        self.git('init', '-q', '-b', 'main')
        for key, value in [('user.email', 'fixture@example.invalid'), ('user.name', 'Fixture'), ('commit.gpgsign', 'false')]:
            self.git('config', key, value)
        (self.root / '.governance').mkdir()
        for name in ('ticket-activity.json', 'ticket-allocation.json'):
            (self.root / '.governance' / name).write_bytes((ROOT / 'governance' / name).read_bytes())
        (self.root / '.gitignore').write_text('/.subactor/\n/.worktrees/\n')
        (self.root / 'source.txt').write_text('base')
        self.git('add', '.')
        self.git('commit', '-qm', 'base')
        base = self.git('rev-parse', 'HEAD')
        self.tree = self.root / '.worktrees/ticket-123--example'
        self.git('worktree', 'add', '-qb', 'ticket/123-example', str(self.tree))
        (self.tree / 'project/ticket-123').mkdir(parents=True)
        (self.tree / 'project/ticket-123/README.md').write_text('Status: IN_PROGRESS')
        (self.tree / 'source.txt').write_text('feature')
        self.git('add', '.', root=self.tree)
        self.git('commit', '-qm', 'feature', root=self.tree)
        self.head = self.git('rev-parse', 'HEAD', root=self.tree)
        self.git('merge', '--no-ff', '-qm', 'merged', 'ticket/123-example')
        terminal = self.git('rev-parse', 'HEAD')
        self.receipt = {'receiptRef': 'receipt:test/merged-123', 'ticket': 'ticket-123', 'outcome': 'merged',
            'headSha': self.head, 'terminalSha': terminal, 'targetBranch': 'main', 'occurredAt': '2026-10-28T01:00:00Z'}
        activity.record(self.root, self.receipt)
        self.lease = self.root / '.subactor/leases/ticket-123--example.json'
        self.lease.parent.mkdir(parents=True)
        self.value = {'schema': canonical.LEASE_SCHEMA, 'leaseId': 'allocation-123',
            'repositoryRef': 'local/' + hashlib.sha256(str(self.root).encode()).hexdigest(),
            'targetBranch': 'main', 'ticketId': 'ticket-123', 'workstream': 'governance', 'scopeHash': 'a'*64,
            'branchRef': 'refs/heads/ticket/123-example', 'worktreeId': 'ticket-123--example',
            'ownerActor': 'agent:fixture', 'ownerSession': 'fixture-session', 'phase': 'claimed',
            'leaseRevision': 1, 'fencingToken': 1, 'issuedAt': '2026-10-28T00:00:00Z',
            'heartbeatAt': '2026-10-28T00:00:00Z', 'expiresAt': '2026-10-28T00:30:00Z',
            'headSha': base, 'pullRequest': None, 'validatorRunId': None, 'publicationFrozen': False,
            'planHash': 'b'*64, 'previousReceiptRef': None, 'eventSequence': 1}
        self.write_lease()
        self.request = {'schema': release.REQUEST_SCHEMA, 'requestId': 'owner-finished-123',
            'worktreeId': 'ticket-123--example', 'ownerActor': 'agent:fixture', 'ownerSession': 'fixture-session',
            'ownerHandoff': True, 'expectedRevision': 1, 'expectedFencingToken': 1,
            'expectedLeaseSha256': hashlib.sha256(self.lease.read_bytes()).hexdigest(),
            'terminalReceiptRef': self.receipt['receiptRef']}

    def git(self, *args, root=None):
        return subprocess.check_output(['git', '-C', str(root or self.root), *args], stderr=subprocess.DEVNULL, text=True).strip()

    def write_lease(self):
        self.lease.write_text(json.dumps(self.value))

    def invoke(self, apply=True):
        return release.release_owner(self.root, self.request, apply=apply, actor='agent:fixture', session='fixture-session')

    def refused(self):
        before = self.lease.read_bytes()
        with self.assertRaises((ValueError, PermissionError, OSError)):
            self.invoke()
        self.assertEqual(self.lease.read_bytes(), before)

    def test_plan_then_apply_and_repeat_are_canonical_and_do_not_change_git(self):
        before = self.lease.read_bytes()
        self.assertEqual(self.invoke(False)['status'], 'planned')
        self.assertEqual(self.lease.read_bytes(), before)
        head = self.git('rev-parse', 'HEAD')
        result = self.invoke()
        current = json.loads(self.lease.read_bytes())
        self.assertEqual(result['status'], 'released')
        self.assertEqual((current['phase'], current['leaseRevision'], current['fencingToken']), ('released', 3, 3))
        self.assertEqual(canonical.validate_lease(current), [])
        self.assertEqual(self.invoke()['status'], 'idempotent')
        self.assertEqual(self.git('rev-parse', 'HEAD'), head)
        self.assertTrue(self.tree.exists())

    def test_isolated_cli_defaults_to_plan_and_applies_only_explicitly(self):
        request = self.root.parent / 'request.json'
        request.write_text(json.dumps(self.request))
        for name in ('terminal_lease_release.py', 'change_lease_check.py', 'ticket_activity.py'):
            (self.root / '.governance' / name).write_bytes((ROOT / 'scripts' / name).read_bytes())
        (self.root / '.governance/change-lease.schema.json').write_bytes(
            (ROOT / 'subprojects/change-lease/change-lease.schema.json').read_bytes())
        command = [sys.executable, '-I', str(self.root / '.governance/terminal_lease_release.py'),
                   '--root', str(self.root), '--request', str(request)]
        before = self.lease.read_bytes()
        planned = subprocess.run(command, capture_output=True, text=True, check=True, timeout=20)
        self.assertEqual(json.loads(planned.stdout)['status'], 'planned')
        self.assertEqual(self.lease.read_bytes(), before)
        env = dict(os.environ, NEW_PROJECT_WRITER_ACTOR='agent:fixture', NEW_PROJECT_WRITER_SESSION='fixture-session')
        rejected = subprocess.run(command + ['--apply'], env={k:v for k,v in env.items() if not k.startswith('NEW_PROJECT_WRITER_')}, capture_output=True, timeout=20)
        self.assertEqual(rejected.returncode, 2)
        self.assertEqual(self.lease.read_bytes(), before)
        applied = subprocess.run(command + ['--apply'], env=env, capture_output=True, text=True, check=True, timeout=20)
        self.assertEqual(json.loads(applied.stdout)['status'], 'released')

    def test_foreign_owner_stale_fences_and_missing_handoff_refuse(self):
        for field, value in [('ownerActor', 'agent:other'), ('ownerSession', 'other'),
                ('expectedRevision', 2), ('expectedFencingToken', 2), ('expectedLeaseSha256', 'c'*64),
                ('ownerHandoff', False)]:
            with self.subTest(field=field):
                original = self.request[field]
                self.request[field] = value
                self.refused()
                self.request[field] = original

    def test_noncanonical_and_frozen_phases_are_not_normalized(self):
        for phase in ('completed', 'expired', 'publication_frozen', 'dispatching'):
            with self.subTest(phase=phase):
                self.value.update(phase=phase, publicationFrozen=phase in canonical.FROZEN_PHASES,
                                  headSha=self.head, pullRequest=1)
                self.write_lease()
                self.request['expectedLeaseSha256'] = hashlib.sha256(self.lease.read_bytes()).hexdigest()
                self.refused()

    def test_missing_receipt_and_registered_controller_refuse(self):
        self.request['terminalReceiptRef'] = 'receipt:missing'
        self.refused()
        self.request['terminalReceiptRef'] = self.receipt['receiptRef']
        policy = self.root / '.governance/ticket-allocation.json'
        policy.write_text('{"schema":"new-project.ticket-allocation/v1","mode":"registered"}')
        self.refused()

    def test_dirty_or_advanced_worktree_refuses_but_dirty_primary_is_preserved(self):
        (self.tree / 'retained.txt').write_text('unpublished')
        self.refused()
        (self.tree / 'retained.txt').unlink()
        (self.root / 'unrelated.txt').write_text('primary work')
        self.assertEqual(self.invoke()['status'], 'released')
        self.assertEqual((self.root / 'unrelated.txt').read_text(), 'primary work')

    def test_advanced_branch_and_wrong_repository_refuse(self):
        (self.tree / 'source.txt').write_text('another change')
        self.git('commit', '-qam', 'unmerged', root=self.tree)
        self.refused()

    def test_wrong_repository_and_hardlinked_lease_refuse(self):
        self.value['repositoryRef'] = 'local/' + 'f'*64
        self.write_lease()
        self.request['expectedLeaseSha256'] = hashlib.sha256(self.lease.read_bytes()).hexdigest()
        self.refused()
        self.value['repositoryRef'] = 'local/' + hashlib.sha256(str(self.root).encode()).hexdigest()
        self.write_lease()
        self.request['expectedLeaseSha256'] = hashlib.sha256(self.lease.read_bytes()).hexdigest()
        os.link(self.lease, self.lease.parent / 'hardlink')
        self.refused()

    def test_existing_approved_phase_advances_without_inventing_approval(self):
        self.value.update(phase='approved', publicationFrozen=True, headSha=self.head, pullRequest=1, validatorRunId='fixture-validator')
        self.write_lease()
        self.request['expectedLeaseSha256'] = hashlib.sha256(self.lease.read_bytes()).hexdigest()
        self.assertEqual(self.invoke()['leaseRevision'], 4)
        self.assertEqual(json.loads(self.lease.read_bytes())['phase'], 'released')

    def test_concurrent_lock_and_replaced_lock_refuse(self):
        import fcntl
        lock = self.lease.with_name(self.lease.name + '.lock')
        with lock.open('w') as held:
            fcntl.flock(held, fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.refused()
        original = release._verify_terminal
        def changed(*args):
            result = original(*args)
            lock.rename(lock.with_suffix('.old'))
            lock.write_text('replacement')
            return result
        with patch.object(release, '_verify_terminal', side_effect=changed): self.refused()

    def test_write_ahead_record_recovers_after_interrupted_replace(self):
        before = self.lease.read_bytes()
        with patch.object(release, '_replace_lease', side_effect=OSError('injected interruption')):
            with self.assertRaises(OSError): self.invoke()
        self.assertEqual(self.lease.read_bytes(), before)
        self.assertEqual(self.invoke()['status'], 'released')
        self.assertEqual(self.invoke()['status'], 'idempotent')

    def test_changed_owner_bytes_and_unsafe_paths_refuse(self):
        original = release._verify_terminal
        def changed(*args):
            result = original(*args)
            self.value['heartbeatAt'] = '2026-10-28T00:01:00Z'
            self.write_lease()
            return result
        with patch.object(release, '_verify_terminal', side_effect=changed):
            with self.assertRaises(PermissionError): self.invoke()
        self.assertEqual(json.loads(self.lease.read_bytes())['phase'], 'claimed')
        target = self.lease.parent / 'retained'
        self.lease.rename(target)
        self.lease.symlink_to(target)
        self.refused()


class PlatformBoundary(unittest.TestCase):
    def test_unsupported_controller_refuses_before_filesystem_effect(self):
        request = {'schema': release.REQUEST_SCHEMA, 'requestId': 'unsupported', 'worktreeId': 'ticket-123--example',
            'ownerActor': 'agent:fixture', 'ownerSession': 'session', 'ownerHandoff': True,
            'expectedRevision': 1, 'expectedFencingToken': 1, 'expectedLeaseSha256': 'a'*64,
            'terminalReceiptRef': 'receipt:test/terminal'}
        with patch.object(release.os, 'name', 'unsupported'):
            with self.assertRaisesRegex(PermissionError, 'posix_controller_required'):
                release.release_owner('unavailable', request, apply=True)


if __name__ == '__main__':
    unittest.main()
