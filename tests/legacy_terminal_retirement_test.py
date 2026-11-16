"""Legacy retirement uses real merged Git fixtures, never host lease data."""
import base64
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    sys.modules[name] = result
    spec.loader.exec_module(result)
    return result


fixtures = load('_legacy_git_fixtures', ROOT / 'tests/terminal_lease_release_test.py')
retirement = load('_legacy_retirement', ROOT / 'scripts/legacy_terminal_retirement.py')


@unittest.skipUnless(os.name == 'posix', 'POSIX adapter only')
class LegacyTerminalRetirement(unittest.TestCase):
    def git(self, *args, **kwargs):
        result = fixtures.TerminalOwnerRelease.git(self, *args, **kwargs)
        if args[0] == 'init':
            fixtures.TerminalOwnerRelease.git(
                self, 'remote', 'add', 'origin', 'https://github.com/owner/repo.git')
        return result

    write_lease = fixtures.TerminalOwnerRelease.write_lease

    def setUp(self):
        fixtures.TerminalOwnerRelease.setUp(self)
        self.value['repositoryRef'] = 'repo'
        self.write_lease()
        self.request.update(schema=retirement.SCHEMA, legacyRepositoryRef='repo',
                            canonicalRepositoryRef='owner/repo')
        self.bind()

    def bind(self):
        self.request['expectedLeaseSha256'] = hashlib.sha256(self.lease.read_bytes()).hexdigest()

    def invoke(self, apply=False, **context):
        return retirement.retire_owner(self.root, self.request, apply=apply,
                                      actor=context.get('actor', 'agent:fixture'),
                                      session=context.get('session', 'fixture-session'))

    def refused(self, apply=False):
        before = self.lease.read_bytes()
        with self.assertRaises((ValueError, PermissionError, OSError, subprocess.SubprocessError)):
            self.invoke(apply)
        self.assertEqual(self.lease.read_bytes(), before)

    def test_plan_has_no_writes_then_apply_preserves_original_and_git(self):
        original = self.lease.read_bytes()
        head = self.git('rev-parse', 'HEAD')
        branch = self.git('rev-parse', 'ticket/123-example')
        plan = self.invoke()
        self.assertEqual(plan['status'], 'planned')
        self.assertFalse(plan['grantsAuthority'])
        self.assertEqual(self.lease.read_bytes(), original)
        self.assertFalse(self.lease.with_suffix('.json.lock').exists())
        self.assertFalse((self.root / '.subactor/receipts/legacy-terminal-retirement').exists())
        applied = self.invoke(True)
        self.assertEqual(applied['status'], 'retired')
        self.assertFalse(applied['grantsAuthority'])
        self.assertFalse(self.lease.exists())
        receipt = Path(applied['receipt'])
        journal_bytes = receipt.read_bytes()
        journal = json.loads(journal_bytes)
        self.assertEqual(base64.b64decode(journal['original']), original)
        self.assertEqual(json.loads(original)['repositoryRef'], 'repo')
        self.assertEqual(journal['terminal'], self.receipt)
        self.assertEqual(self.invoke(True)['status'], 'idempotent')
        self.assertEqual(receipt.read_bytes(), journal_bytes)
        self.assertTrue(self.tree.exists())
        self.assertEqual(self.git('rev-parse', 'HEAD'), head)
        self.assertEqual(self.git('rev-parse', 'ticket/123-example'), branch)

    def test_ordinary_controller_and_validator_still_reject_bare_identity(self):
        original = self.lease.read_bytes()
        self.assertTrue(fixtures.canonical.validate_lease(json.loads(original)))
        request = {k: self.request[k] for k in retirement.release.FIELDS}
        request['schema'] = retirement.release.REQUEST_SCHEMA
        with self.assertRaisesRegex(PermissionError, '^invalid_canonical_lease$'):
            retirement.release.release_owner(self.root, request)
        self.assertEqual(self.lease.read_bytes(), original)

    def test_owner_context_is_mandatory_for_apply(self):
        for context in ({'actor': None}, {'session': None}, {'actor': 'agent:other'},
                        {'session': 'another-session'}):
            with self.subTest(context=context), self.assertRaises(PermissionError):
                self.invoke(True, **context)
        self.assertTrue(self.lease.exists())

    def test_foreign_owner_and_stale_cas_requests_refuse(self):
        for field, value in [('ownerActor', 'agent:other'), ('ownerSession', 'other'),
                             ('expectedRevision', 2), ('expectedFencingToken', 2),
                             ('expectedLeaseSha256', 'c' * 64), ('ownerHandoff', False),
                             ('legacyRepositoryRef', 'other'),
                             ('canonicalRepositoryRef', 'other/repo')]:
            with self.subTest(field=field):
                prior = self.request[field]
                self.request[field] = value
                self.refused()
                self.request[field] = prior

    def test_same_basename_in_another_origin_is_not_accepted(self):
        self.git('remote', 'set-url', 'origin', 'https://github.com/other/repo.git')
        self.refused()

    def test_missing_origin_is_not_accepted(self):
        self.git('remote', 'remove', 'origin')
        self.refused()

    def test_live_and_strict_leases_are_not_retired(self):
        original = dict(self.value)
        for changes in [{'expiresAt': '2099-01-01T00:00:00Z'},
                        {'phase': 'publication_frozen', 'publicationFrozen': True,
                         'headSha': self.head, 'pullRequest': 1},
                        {'phase': 'dispatching', 'publicationFrozen': True,
                         'headSha': self.head, 'pullRequest': 1},
                        {'phase': 'approved', 'publicationFrozen': True,
                         'headSha': self.head, 'pullRequest': 1}]:
            with self.subTest(changes=changes):
                self.value = dict(original, **changes)
                self.write_lease()
                self.bind()
                self.refused(True)

    def test_shape_errors_are_not_normalized(self):
        original = dict(self.value)
        for changes in [{'unexpected': True}, {'fencingToken': False}, {'headSha': 'broken'},
                        {'ownerActor': ''}, {'schema': 'unknown/v1'}, {'repositoryRef': 'other'}]:
            with self.subTest(changes=changes):
                self.value = dict(original, **changes)
                self.write_lease()
                self.bind()
                self.refused()

    def test_closed_request_rejects_extra_or_missing_fields(self):
        original = dict(self.request)
        self.request['unexpected'] = True
        self.refused()
        self.request = dict(original)
        self.request.pop('legacyRepositoryRef')
        self.refused()

    def test_dirty_or_advanced_delivery_is_preserved(self):
        (self.tree / 'unpublished.txt').write_text('keep me')
        self.refused(True)
        (self.tree / 'unpublished.txt').unlink()
        (self.tree / 'source.txt').write_text('unmerged')
        self.git('commit', '-qam', 'unmerged', root=self.tree)
        self.refused(True)

    def test_missing_terminal_receipt_refuses(self):
        self.request['terminalReceiptRef'] = 'receipt:missing'
        self.refused(True)

    def test_symlink_and_hardlink_slots_refuse_without_touching_target(self):
        original = self.lease.read_bytes()
        target = self.root.parent / 'retained.json'
        target.write_bytes(original)
        for hardlink in (False, True):
            with self.subTest(hardlink=hardlink):
                self.lease.unlink()
                if hardlink:
                    os.link(target, self.lease)
                else:
                    self.lease.symlink_to(target)
                self.refused(True)
                self.assertEqual(target.read_bytes(), original)

    def test_real_concurrent_lock_preserves_slot(self):
        import fcntl
        with self.lease.with_suffix('.json.lock').open('w') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.refused(True)

    def test_write_ahead_interruption_replays_without_original_rewrite(self):
        original = self.lease.read_bytes()
        with patch.object(retirement, '_unlink_slot', side_effect=OSError('interrupted')):
            self.refused(True)
        receipts = list((self.root / '.subactor/receipts/legacy-terminal-retirement').glob('*.json'))
        self.assertEqual(len(receipts), 1)
        self.assertEqual(base64.b64decode(json.loads(receipts[0].read_bytes())['original']), original)
        self.assertEqual(self.invoke(True)['status'], 'retired')

    def test_recreated_slot_after_retirement_is_not_removed_on_replay(self):
        original = self.lease.read_bytes()
        result = self.invoke(True)
        journal = json.loads(Path(result['receipt']).read_bytes())
        self.lease.write_bytes(original)
        self.assertEqual(base64.b64decode(journal['original']), original)
        self.refused(True)

    def test_new_fencing_after_interruption_is_not_overwritten(self):
        with patch.object(retirement, '_unlink_slot', side_effect=OSError('interrupted')):
            self.refused(True)
        self.value['fencingToken'] += 1
        self.value['leaseRevision'] += 1
        self.write_lease()
        self.refused(True)

    def test_isolated_cli_plan_and_explicit_owner_apply(self):
        request = self.root.parent / 'request.json'
        request.write_text(json.dumps(self.request))
        command = [sys.executable, '-I', str(ROOT / 'scripts/legacy_terminal_retirement.py'),
                   '--root', str(self.root), '--request', str(request)]
        original = self.lease.read_bytes()
        plan = subprocess.run(command, capture_output=True, text=True, check=True, timeout=20)
        self.assertEqual(json.loads(plan.stdout)['status'], 'planned')
        env = {k: v for k, v in os.environ.items() if not k.startswith('NEW_PROJECT_WRITER_')}
        denied = subprocess.run(command + ['--apply'], env=env, capture_output=True, text=True, timeout=20)
        self.assertEqual(denied.returncode, 2)
        self.assertNotIn(str(self.root), denied.stderr)
        self.assertEqual(self.lease.read_bytes(), original)
        env.update(NEW_PROJECT_WRITER_ACTOR='agent:fixture', NEW_PROJECT_WRITER_SESSION='fixture-session')
        applied = subprocess.run(command + ['--apply'], env=env, capture_output=True, text=True,
                                 check=True, timeout=20)
        self.assertEqual(json.loads(applied.stdout)['status'], 'retired')


if __name__ == '__main__':
    unittest.main()
