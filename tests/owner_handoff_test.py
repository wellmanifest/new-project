"""Adversarial tests of the local controller, with real relative Git worktrees."""
import concurrent.futures
from datetime import datetime, timedelta, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location('owner_handoff', Path(__file__).resolve().parents[1] / 'scripts/owner_handoff.py')
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


@unittest.skipUnless(os.name == 'posix', 'local protected controller requires POSIX descriptors')
class OwnerHandoffTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='owner-handoff-', dir=str(Path('/tmp').resolve()))
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'primary'
        self.root.mkdir()
        self.git('init', '-q', '-b', 'main')
        self.git('config', 'user.name', 'Controller fixture')
        self.git('config', 'user.email', 'controller@example.invalid')
        self.git('remote', 'add', 'origin', 'https://github.com/example/controller-fixture.git')
        self.id = 'ticket-967--fixture'
        self.branch = 'ticket/967-fixture'
        self.ticket = 'ticket-967'
        (self.root / '.governance').mkdir()
        policy = {'$schema': './ticket-allocation.schema.json', 'schema': 'new-project.ticket-allocation/v1', 'mode': 'local-single-clone'}
        (self.root / '.governance/ticket-allocation.json').write_text(json.dumps(policy))
        intent = self.root / 'project' / self.ticket / 'intent.json'
        intent.parent.mkdir(parents=True)
        intent.write_text(json.dumps({'schema': 'new-project.intent/v3', 'ticket': self.ticket,
                                     'workstream': 'governance', 'allowedPaths': ['source.txt']}))
        (self.root / 'source.txt').write_text('original\n')
        self.git('add', '.')
        self.git('commit', '-qm', 'fixture base')
        self.tree = self.root / '.worktrees' / self.id
        try:
            self.git('worktree', 'add', '--relative-paths', '-b', self.branch, str(self.tree))
        except Exception as error:
            self.skipTest('Git with relative worktree support required: ' + str(error))
        stamp = lambda delta: (datetime.now(timezone.utc) + timedelta(seconds=delta)).strftime('%Y-%m-%dT%H:%M:%SZ')
        self.lease = {'schema': 'wellmanifest.change-lease/v1', 'leaseId': 'allocation-fixture',
                      'repositoryRef': 'example/controller-fixture', 'targetBranch': 'main',
                      'ticketId': self.ticket, 'workstream': 'governance', 'scopeHash': 'a' * 64,
                      'planHash': 'b' * 64, 'branchRef': 'refs/heads/' + self.branch,
                      'worktreeId': self.id, 'ownerActor': 'agent:codex', 'ownerSession': 'old-session',
                      'phase': 'claimed', 'leaseRevision': 1, 'fencingToken': 1, 'eventSequence': 1,
                      'issuedAt': stamp(-7200), 'heartbeatAt': stamp(-7200), 'expiresAt': stamp(-3600),
                      'headSha': self.git('rev-parse', 'HEAD').strip(), 'pullRequest': None,
                      'validatorRunId': None, 'publicationFrozen': False, 'previousReceiptRef': None}
        self.slot = self.root / '.subactor/leases' / (self.id + '.json')
        self.slot.parent.mkdir(parents=True)
        self.slot.write_bytes(MODULE._encoded(self.lease))
        self.request = self.make_request()
        self.before = self.slot.read_bytes()

    def git(self, *args, tree=None):
        return MODULE._git(tree or self.root, *args).decode()

    def make_request(self, **changes):
        observed = MODULE.observe(self.root, self.id)
        request = {'schema': MODULE.SCHEMA, 'requestId': 'fixture-handoff', 'worktreeId': self.id,
                   'ownerActor': self.lease['ownerActor'], 'ownerSession': self.lease['ownerSession'],
                   'consent': True, 'expectedRevision': 1, 'expectedFencingToken': 1,
                   'expectedLeaseSha256': hashlib.sha256(self.slot.read_bytes()).hexdigest(),
                   'expectedHeadSha': observed['head'], 'expectedDirtySha256': observed['dirty'],
                   'expectedIntentSha256': observed['intent'], 'expectedScopeHash': observed['scope'],
                   'primaryCheckout': observed['primaryCheckout'], 'repositoryRef': observed['repositoryRef'],
                   'targetOwnerActor': 'agent:codex', 'targetOwnerSession': 'fresh-session', 'ttlSeconds': 600}
        return dict(request, **changes)

    def apply(self, request=None, *, bad=False, verifier=None):
        request = request or self.request
        # The fixture simulates an independent protected issuer. It never
        # treats the FD contents as authenticated merely because they are JSON.
        authorization = {'issuer': 'protected-test-issuer', 'nonce': 'forged' if bad else 'fixture-capability'}
        def authenticate(bound_request, data):
            if data != {'issuer': 'protected-test-issuer', 'nonce': 'fixture-capability'}:
                raise PermissionError('untrusted capability')
            return {'requestDigest': MODULE._digest(MODULE._encoded(bound_request)),
                    'verificationRef': 'receipt:test-protected-invoker'}
        with tempfile.TemporaryFile() as auth:
            auth.write(json.dumps(authorization).encode())
            auth.flush()
            return MODULE.handoff(self.root, request, apply=True, authorization_fd=auth.fileno(),
                                  verifier=verifier or authenticate)

    def assert_untouched(self):
        self.assertEqual(self.slot.read_bytes(), self.before)

    def test_plan_is_readonly_and_never_grants_writer_environment(self):
        result = MODULE.handoff(self.root, self.request)
        self.assertEqual(result['status'], 'planned')
        self.assertFalse(result['grantsAuthority'])
        self.assertNotIn('writerEnvironment', result)
        self.assertFalse((self.root / '.subactor/receipts').exists())
        self.assert_untouched()

    def test_expired_owner_explicit_consent_same_actor_fresh_session(self):
        result = self.apply()
        successor = json.loads(self.slot.read_bytes())
        self.assertEqual((successor['leaseRevision'], successor['fencingToken'], successor['eventSequence']), (2, 2, 2))
        self.assertEqual(successor['ownerActor'], self.lease['ownerActor'])
        self.assertEqual(successor['ownerSession'], 'fresh-session')
        self.assertFalse(MODULE.control.canonical.validate_lease(successor))
        self.assertEqual(MODULE.control.canonical.check_writer(self.tree, 'refs/heads/' + self.branch,
                         'commit', 'agent:codex', 'fresh-session', '2', '2'), [])
        self.assertEqual(result['writerEnvironment']['NEW_PROJECT_FENCING_TOKEN'], '2')
        self.assertEqual((self.tree / 'source.txt').read_text(), 'original\n')

    def test_absent_verifier_and_forged_capability_refused(self):
        with tempfile.TemporaryFile() as auth:
            auth.write(b'{"consent":true}')
            auth.flush()
            with self.assertRaisesRegex(ValueError, 'protected verifier'):
                MODULE.handoff(self.root, self.request, apply=True, authorization_fd=auth.fileno())
        with self.assertRaises(PermissionError):
            self.apply(bad=True)
        with self.assertRaises(ValueError):
            self.apply(verifier=lambda *_: {'requestDigest': '0' * 64, 'verificationRef': 'forged'})
        self.assert_untouched()

    def test_no_consent_unchanged_session_unknown_fields_and_bounds_refused(self):
        for changed in ({'consent': False}, {'targetOwnerSession': 'old-session'}, {'unexpected': True},
                        {'ttlSeconds': True}, {'ttlSeconds': 7201}, {'worktreeId': '../escape'}):
            with self.subTest(changed=changed), self.assertRaises(ValueError):
                self.apply(dict(self.request, **changed))
        self.assert_untouched()

    def test_wrong_old_owner_fencing_scope_and_repository_refused(self):
        for changed in ({'ownerActor': 'other'}, {'ownerSession': 'other'}, {'expectedRevision': 2},
                        {'expectedFencingToken': 2}, {'expectedScopeHash': 'f' * 64},
                        {'repositoryRef': 'other/repository'}, {'primaryCheckout': '/different-primary'}):
            with self.subTest(changed=changed), self.assertRaises(ValueError):
                self.apply(dict(self.request, **changed))
        self.assert_untouched()

    def test_invalid_and_frozen_leases_refused(self):
        for changed in ({'scopeHash': 'invalid'}, {'publicationFrozen': True, 'phase': 'publication_frozen'},
                        {'phase': 'released'}):
            self.slot.write_bytes(MODULE._encoded(dict(self.lease, **changed)))
            request = dict(self.request, expectedLeaseSha256=MODULE._digest(self.slot.read_bytes()))
            with self.subTest(changed=changed), self.assertRaises(ValueError):
                self.apply(request)
            self.assertEqual(json.loads(self.slot.read_bytes()), dict(self.lease, **changed))

    def test_dirty_content_with_same_porcelain_invalidates_snapshot(self):
        (self.tree / 'source.txt').write_text('first dirty\n')
        self.request = self.make_request()
        before_status = self.git('status', '--porcelain', tree=self.tree)
        (self.tree / 'source.txt').write_text('second dirty\n')
        self.assertEqual(before_status, self.git('status', '--porcelain', tree=self.tree))
        with self.assertRaisesRegex(ValueError, 'observation changed'):
            self.apply()
        self.assert_untouched()

    def test_intent_change_and_staged_blob_change_refused(self):
        path = self.tree / 'project' / self.ticket / 'intent.json'
        path.write_text(path.read_text() + '\n')
        with self.assertRaises(ValueError):
            self.apply()
        self.assert_untouched()

    def test_plain_clone_is_not_canonical_registration(self):
        self.git('worktree', 'remove', str(self.tree))
        self.git('clone', '-q', str(self.root), str(self.tree))
        self.git('checkout', '-b', self.branch, tree=self.tree)
        with self.assertRaises(ValueError):
            self.apply()
        self.assert_untouched()

    def test_symlink_lease_parent_leaf_and_lock_refused(self):
        for kind in ('leaf', 'lock', 'parent'):
            with self.subTest(kind=kind):
                if kind == 'leaf':
                    saved = self.slot.with_suffix('.original')
                    self.slot.rename(saved)
                    self.slot.symlink_to(saved.name)
                elif kind == 'lock':
                    lock = Path(str(self.slot) + '.lock')
                    lock.unlink(missing_ok=True)
                    lock.symlink_to(self.slot.name)
                else:
                    original = self.slot.parent
                    moved = original.with_name('original-leases')
                    original.rename(moved)
                    original.symlink_to(moved.name)
                try:
                    with self.assertRaises((OSError, ValueError)):
                        self.apply()
                finally:
                    if kind == 'leaf':
                        self.slot.unlink(); saved.rename(self.slot)
                    elif kind == 'lock':
                        lock.unlink()
                    else:
                        original.unlink(); moved.rename(original)
        self.assert_untouched()

    def test_root_symlink_refused(self):
        alias = self.root.with_name('alias')
        alias.symlink_to(self.root, target_is_directory=True)
        with self.assertRaises((OSError, ValueError)):
            MODULE.handoff(alias, self.request)
        self.assert_untouched()

    def test_snapshot_race_after_durable_journal_refused(self):
        original = MODULE.control.atomic_at
        journal_name = MODULE._digest(MODULE._encoded(self.request)) + '.json'
        def race(fd, name, raw, **kwargs):
            original(fd, name, raw, **kwargs)
            if name == journal_name:
                (self.tree / 'source.txt').write_text('raced after journal\n')
        with patch.object(MODULE.control, 'atomic_at', side_effect=race):
            with self.assertRaises(ValueError):
                self.apply()
        self.assert_untouched()

    def test_two_competing_handoffs_only_one_wins(self):
        def attempt(request):
            try:
                return self.apply(request)['status']
            except (OSError, ValueError):
                return 'refused'
        other = dict(self.request, requestId='competing', targetOwnerSession='another-session')
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(attempt, (self.request, other)))
        self.assertEqual(results.count('handoff'), 1, results)
        self.assertEqual(results.count('refused'), 1, results)
        self.assertEqual(json.loads(self.slot.read_bytes())['fencingToken'], 2)

    def test_exact_replay_reauthenticates_and_never_extends_lifetime(self):
        result = self.apply()
        successor = self.slot.read_bytes()
        self.assertEqual(self.apply()['status'], 'idempotent')
        self.assertEqual(self.slot.read_bytes(), successor)
        self.assertEqual(result['writerEnvironment']['NEW_PROJECT_FENCING_TOKEN'], '2')
        with self.assertRaises(PermissionError):
            self.apply(bad=True)
        self.assertEqual(self.slot.read_bytes(), successor)

    def test_replay_after_fence_advance_or_workspace_change_refused(self):
        self.apply()
        successor = json.loads(self.slot.read_bytes())
        advanced = dict(successor, leaseRevision=3, fencingToken=3, eventSequence=3)
        self.slot.write_bytes(MODULE._encoded(advanced))
        with self.assertRaisesRegex(ValueError, 'CAS lost'):
            self.apply()
        self.slot.write_bytes(MODULE._encoded(successor))
        (self.tree / 'source.txt').write_text('new owner work\n')
        with self.assertRaises(ValueError):
            self.apply()

    def test_allocation_base_and_birth_plan_are_preserved_after_accepted_commit(self):
        (self.tree / 'source.txt').write_text('accepted owner work\n')
        self.git('add', 'source.txt', tree=self.tree)
        self.git('commit', '-qm', 'accepted owner work', tree=self.tree)
        self.request = self.make_request()
        self.assertNotEqual(self.request['expectedHeadSha'], self.lease['headSha'])
        self.apply()
        successor = json.loads(self.slot.read_bytes())
        self.assertEqual(successor['planHash'], self.lease['planHash'])
        self.assertEqual(successor['scopeHash'], self.lease['scopeHash'])
        self.assertEqual(successor['headSha'], self.request['expectedHeadSha'])

    def test_project_lifetime_policy_is_enforced(self):
        (self.root / '.governance/manifest.json').write_text(json.dumps({'delivery':{'maxActiveMinutes':1}}))
        with self.assertRaisesRegex(ValueError, 'lifetime'):
            self.apply()
        self.assert_untouched()

    def test_replay_expired_successor_does_not_renew(self):
        self.apply()
        successor = self.slot.read_bytes()
        class FutureClock:
            @staticmethod
            def now(tz):
                return datetime.now(tz) + timedelta(hours=3)
            fromisoformat = staticmethod(datetime.fromisoformat)
        with patch.object(MODULE, 'datetime', FutureClock):
            with self.assertRaisesRegex(ValueError, 'expired'):
                self.apply()
        self.assertEqual(self.slot.read_bytes(), successor)

    def test_tampered_journal_cannot_change_successor_or_writer_environment(self):
        self.apply()
        journal_path = next((self.root / '.subactor/receipts/owner-handoff').glob('*.json'))
        journal = json.loads(journal_path.read_bytes())
        journal['result']['writerEnvironment']['NEW_PROJECT_WRITER_ACTOR'] = 'forged'
        journal_path.write_bytes(MODULE._encoded(journal))
        with self.assertRaisesRegex(ValueError, 'journal result'):
            self.apply()

    def test_authorization_rechecked_before_replace(self):
        calls = []
        def revoked(request, authorization):
            calls.append(True)
            if len(calls) > 1:
                raise PermissionError('authorization revoked')
            return {'requestDigest':MODULE._digest(MODULE._encoded(request)),
                    'verificationRef':'receipt:test-revocation'}
        with self.assertRaisesRegex(PermissionError, 'revoked'):
            self.apply(verifier=revoked)
        self.assert_untouched()

    def test_staged_blob_changes_with_unchanged_worktree_are_observed(self):
        path = self.tree / 'source.txt'
        path.write_text('staged-first\n')
        self.git('add', 'source.txt', tree=self.tree)
        path.write_text('working-tree\n')
        self.request = self.make_request()
        old_status = self.git('status', '--porcelain', tree=self.tree)
        path.write_text('staged-second\n')
        self.git('add', 'source.txt', tree=self.tree)
        path.write_text('working-tree\n')
        self.assertEqual(old_status, self.git('status', '--porcelain', tree=self.tree))
        with self.assertRaises(ValueError):
            self.apply()
        self.assert_untouched()


if __name__ == '__main__':
    unittest.main()
