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


@unittest.skipUnless(os.name == 'posix', 'local protected controller requires POSIX descriptors')
class ReleasedResumeTest(unittest.TestCase):
    git = OwnerHandoffTest.git
    make_request = OwnerHandoffTest.make_request
    assert_untouched = OwnerHandoffTest.assert_untouched

    def setUp(self):
        OwnerHandoffTest.setUp(self)
        self.lease.update(phase='released', leaseRevision=2, fencingToken=2, eventSequence=2,
                          scopeHash=MODULE._digest(b'["source.txt"]'))
        self.slot.write_bytes(MODULE._encoded(self.lease))
        self.before = self.slot.read_bytes()
        self.carrier = self.tree / 'project' / self.ticket / 'README.md'
        self.carrier.write_text('- **Status**: BLOCKED\n- **Workflow state**: HANDOFF\n')
        policy = Path(__file__).resolve().parents[1] / 'governance/ticket-activity.json'
        (self.root / '.governance/ticket-activity.json').write_bytes(policy.read_bytes())
        self.registry = self.root / '.git/new-project/terminal-receipts.json'
        self.registry.parent.mkdir()
        self.registry.write_text(json.dumps({'schema':'new-project.terminal-receipt-registry/v1',
                                             'repositoryRef':'https://github.com/example/controller-fixture',
                                             'receipts':[]}))
        self.request = self.resume_request()

    def resume_request(self):
        observed = MODULE.observe(self.root, self.id, released=True)
        request = dict(self.request, schema=MODULE.RESUME_SCHEMA,
                       expectedRevision=self.lease['leaseRevision'], expectedFencingToken=self.lease['fencingToken'],
                       expectedLeaseSha256=MODULE._digest(self.slot.read_bytes()),
                       expectedHeadSha=observed['head'], expectedDirtySha256=observed['dirty'],
                       expectedIntentSha256=observed['intent'], repositoryRef=observed['repositoryRef'],
                       expectedScopeHash=observed['scope'], expectedTerminalStateSha256=observed['terminal'],
                       releaseEvidenceRef='receipt:protected-controller/writer-release')
        return request

    def proof(self, request):
        return {'requestDigest':MODULE._digest(MODULE._encoded(request)),
                'verificationRef':'receipt:protected-fixture/accepted-release',
                'releasedOwner':{'leaseId':self.lease['leaseId'], 'leaseSha256':request['expectedLeaseSha256'],
                                  'revision':self.lease['leaseRevision'], 'fencingToken':self.lease['fencingToken'],
                                  'repositoryRef':self.lease['repositoryRef'],
                                  'canonicalRepositoryRef':request['repositoryRef'],
                                  'releaseEvidenceRef':request['releaseEvidenceRef'],
                                  'writerState':'explicitly-released'}}

    def apply(self, request=None, *, verifier=None, forged=False):
        request = request or self.request
        def authenticate(bound, authorization):
            if authorization != {'capability':'independently-issued-fixture'}:
                raise PermissionError('untrusted release capability')
            return self.proof(bound)
        with tempfile.TemporaryFile() as authorization:
            authorization.write(json.dumps({'capability':'forged' if forged else 'independently-issued-fixture'}).encode())
            authorization.flush()
            return MODULE.resume_released(self.root, request, apply=True,
                                          authorization_fd=authorization.fileno(), verifier=verifier or authenticate)

    def test_released_plan_requires_no_authority_and_changes_nothing(self):
        result = MODULE.resume_released(self.root, self.request)
        self.assertEqual(result['status'], 'planned')
        self.assertFalse(result['grantsAuthority'])
        self.assertNotIn('writerEnvironment', result)
        self.assertFalse((self.root / '.subactor/receipts').exists())
        self.assert_untouched()

    def test_resume_preserves_dirty_work_scope_birth_plan_and_fresh_fencing(self):
        (self.tree / 'source.txt').write_text('accepted unfinished implementation\n')
        self.git('add', 'source.txt', tree=self.tree)
        (self.tree / 'new.txt').write_text('untracked unfinished evidence\n')
        self.request = self.resume_request()
        before_status = self.git('status', '--porcelain', tree=self.tree)
        result = self.apply()
        successor = json.loads(self.slot.read_bytes())
        self.assertTrue(result['grantsAuthority'])
        self.assertEqual((successor['phase'], successor['leaseRevision'], successor['fencingToken']), ('claimed',3,3))
        self.assertEqual(successor['ownerSession'], 'fresh-session')
        for field in ('ticketId','worktreeId','branchRef','scopeHash','planHash'):
            self.assertEqual(successor[field], self.lease[field])
        self.assertEqual(self.git('status','--porcelain',tree=self.tree), before_status)
        self.assertEqual((self.tree/'source.txt').read_text(), 'accepted unfinished implementation\n')
        self.assertEqual((self.tree/'new.txt').read_text(), 'untracked unfinished evidence\n')
        self.assertEqual(self.apply()['status'], 'idempotent')
        self.assertEqual(json.loads(self.slot.read_bytes()), successor)

    def test_explicit_legacy_mapping_canonicalizes_only_the_same_origin(self):
        self.lease['repositoryRef'] = 'controller-fixture'
        self.slot.write_bytes(MODULE._encoded(self.lease))
        self.request = self.resume_request()
        self.assertEqual(self.request['repositoryRef'], 'example/controller-fixture')
        self.apply()
        self.assertEqual(json.loads(self.slot.read_bytes())['repositoryRef'], 'example/controller-fixture')
        journal = json.loads(next((self.root/'.subactor/receipts/released-owner-resume').glob('*.json')).read_text())
        self.assertEqual(json.loads(MODULE.base64.b64decode(journal['original']))['repositoryRef'], 'controller-fixture')
        self.assertFalse((self.root/'.subactor/receipts/owner-handoff').exists())

    def test_ordinary_handoff_and_resume_api_are_schema_isolated(self):
        with self.assertRaisesRegex(ValueError, 'ordinary handoff schema'):
            MODULE.handoff(self.root, self.request)
        ordinary = {k:v for k,v in self.request.items() if k in MODULE.FIELDS}
        ordinary['schema'] = MODULE.SCHEMA
        with self.assertRaisesRegex(ValueError, 'released resume schema'):
            MODULE.resume_released(self.root, ordinary)
        with self.assertRaisesRegex(ValueError, 'frozen ownership'):
            MODULE.handoff(self.root, ordinary)
        self.assert_untouched()

    def test_release_labels_or_request_fields_do_not_authenticate(self):
        with self.assertRaisesRegex(ValueError, 'protected verifier'):
            MODULE.resume_released(self.root, self.request, apply=True)
        with self.assertRaisesRegex(PermissionError, 'untrusted'):
            self.apply(forged=True)
        for change in ({'writerState':'pid-not-found'}, {'leaseSha256':'f'*64}, {'leaseId':'other'},
                       {'revision':1}, {'fencingToken':1}, {'repositoryRef':'other'},
                       {'canonicalRepositoryRef':'foreign/controller-fixture'}, {'releaseEvidenceRef':'receipt:other'}):
            def invalid(request, authorization):
                evidence = self.proof(request); evidence['releasedOwner'].update(change); return evidence
            with self.subTest(change=change), self.assertRaisesRegex(ValueError,'released-owner proof'):
                self.apply(verifier=invalid)
        self.assert_untouched()

    def test_reject_live_unknown_frozen_or_terminal_phases(self):
        for changes in ({'phase':'claimed'}, {'phase':'editing'}, {'phase':'validating'},
                        {'phase':'closed'}, {'phase':'expired'}, {'publicationFrozen':True}):
            self.slot.write_bytes(MODULE._encoded(dict(self.lease, **changes)))
            request = dict(self.request, expectedLeaseSha256=MODULE._digest(self.slot.read_bytes()))
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                self.apply(request)
        self.slot.write_bytes(self.before)
        self.assert_untouched()

    def test_legacy_mapping_refuses_other_names_and_canonical_namespaces(self):
        for value in ('other', 'foreign/controller-fixture', 'local/unknown'):
            self.slot.write_bytes(MODULE._encoded(dict(self.lease, repositoryRef=value)))
            with self.subTest(value=value), self.assertRaises(ValueError):
                MODULE.observe(self.root,self.id,released=True)
        self.slot.write_bytes(self.before)
        self.lease['repositoryRef']='controller-fixture'
        self.slot.write_bytes(MODULE._encoded(self.lease));self.request=self.resume_request()
        self.git('remote','set-url','origin','https://github.com/foreign/other.git')
        with self.assertRaises(ValueError):self.apply()

    def test_scope_change_cannot_be_laundered_by_fresh_intent_observation(self):
        intent = self.tree/'project'/self.ticket/'intent.json';value=json.loads(intent.read_text())
        value['allowedPaths'].append('new-scope/**');intent.write_text(json.dumps(value))
        with self.assertRaisesRegex(ValueError,'scope changed'):
            MODULE.observe(self.root,self.id,released=True)
        self.assert_untouched()

    def test_missing_malformed_or_foreign_terminal_registry_is_refused(self):
        original=self.registry.read_bytes()
        for value in (None, b'{}', b'{bad-json', MODULE._encoded({'schema':'new-project.terminal-receipt-registry/v1','repositoryRef':'foreign','receipts':[]})):
            if value is None:self.registry.unlink()
            else:self.registry.write_bytes(value)
            with self.subTest(value=value), self.assertRaises((ValueError,OSError,MODULE.control.activity.ActivityError)):
                self.apply()
        self.registry.write_bytes(original);self.assert_untouched()

    def test_completed_carrier_or_managed_terminal_receipt_cannot_reopen(self):
        original=self.carrier.read_bytes()
        self.carrier.write_text('- **Status**: DONE\n- **Workflow state**: CLOSED\n')
        with self.assertRaisesRegex(ValueError,'unfinished blocked handoff'):self.apply()
        self.carrier.write_bytes(original)
        data=json.loads(self.registry.read_text());data['receipts']=[{'receiptRef':'receipt:fixture/merged','ticket':self.ticket,'outcome':'merged','headSha':self.lease['headSha'],'terminalSha':self.lease['headSha'],'targetBranch':'main','occurredAt':'2026-11-18T00:00:00Z'}];self.registry.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError,'terminal delivery'):self.apply()
        self.assert_untouched()

    def test_terminal_observation_and_carrier_are_rechecked_after_journal(self):
        original = MODULE.control.atomic_at
        def journal_then_change(*args,**kwargs):
            result=original(*args,**kwargs)
            if args[1].endswith('.json') and 'exclusive' in kwargs:
                value=json.loads(self.registry.read_text());value['receipts'].append({'receiptRef':'receipt:other/merged','ticket':'ticket-111','outcome':'merged','headSha':self.lease['headSha'],'terminalSha':self.lease['headSha'],'targetBranch':'main','occurredAt':'2026-11-18T00:00:00Z'});self.registry.write_text(json.dumps(value))
            return result
        with patch.object(MODULE.control,'atomic_at',journal_then_change):
            with self.assertRaisesRegex(ValueError,'terminal observation changed'):self.apply()
        self.assert_untouched()

    def test_competing_successors_exact_replay_and_revocation(self):
        def attempt(session):
            try:return self.apply(dict(self.request,targetOwnerSession=session))['status']
            except (ValueError,OSError):return 'refused'
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            results=list(pool.map(attempt,['successor-one','successor-two']))
        self.assertEqual(results.count('handoff'),1);self.assertEqual(results.count('refused'),1)
        successor=self.slot.read_bytes()
        def revoked(request,authorization):raise PermissionError('protected release revoked')
        with self.assertRaisesRegex(PermissionError,'revoked'):self.apply(verifier=revoked)
        self.assertEqual(self.slot.read_bytes(),successor)

    def test_changed_dirty_or_index_state_fencing_and_expired_replay_refused(self):
        (self.tree/'source.txt').write_text('dirty-one\n');self.request=self.resume_request()
        (self.tree/'source.txt').write_text('dirty-two\n')
        with self.assertRaisesRegex(ValueError,'observation changed'):self.apply()
        self.assert_untouched();(self.tree/'source.txt').write_text('dirty-one\n');self.apply()
        successor=self.slot.read_bytes()
        class FutureClock:
            @staticmethod
            def now(tz):return datetime.now(tz)+timedelta(hours=3)
            fromisoformat=staticmethod(datetime.fromisoformat)
        with patch.object(MODULE,'datetime',FutureClock):
            with self.assertRaisesRegex(ValueError,'expired'):self.apply()
        self.assertEqual(self.slot.read_bytes(),successor)
        advanced=dict(json.loads(successor),leaseRevision=4,fencingToken=4,eventSequence=4);self.slot.write_bytes(MODULE._encoded(advanced))
        with self.assertRaisesRegex(ValueError,'CAS lost'):self.apply()

    def test_symlink_policy_registry_and_lease_refused(self):
        for path in (self.registry,self.root/'.governance/ticket-activity.json',self.slot):
            raw=path.read_bytes();target=path.with_suffix('.original');path.rename(target);path.symlink_to(target)
            with self.subTest(path=path),self.assertRaises((ValueError,OSError,MODULE.control.activity.ActivityError)):
                self.apply()
            path.unlink();target.rename(path)
        self.assert_untouched()

    def test_missing_release_proof_and_project_lifetime_are_refused(self):
        def ordinary_proof(request, authorization):
            return {'requestDigest':MODULE._digest(MODULE._encoded(request)),
                    'verificationRef':'receipt:ordinary-without-release-proof'}
        with self.assertRaisesRegex(ValueError,'released-owner proof'):
            self.apply(verifier=ordinary_proof)
        (self.root/'.governance/manifest.json').write_text(json.dumps({'delivery':{'maxActiveMinutes':1}}))
        with self.assertRaisesRegex(ValueError,'lifetime'):self.apply()
        self.assert_untouched()

    def test_legacy_projection_does_not_repair_other_invalid_lease_fields(self):
        self.slot.write_bytes(MODULE._encoded(dict(self.lease,repositoryRef='controller-fixture',eventSequence=0)))
        with self.assertRaisesRegex(ValueError,'invalid canonical lease'):
            MODULE.observe(self.root,self.id,released=True)
        self.assertEqual(json.loads(self.slot.read_bytes())['eventSequence'],0)

    def test_authentication_revocation_and_state_race_after_final_authentication(self):
        calls=[]
        def revoked(request,authorization):
            calls.append(True)
            if len(calls)>1:raise PermissionError('release revoked before effect')
            return self.proof(request)
        with self.assertRaisesRegex(PermissionError,'revoked'):self.apply(verifier=revoked)
        self.assert_untouched()
        # A fresh journal namespace avoids replaying the refused transaction
        # with different verifier evidence; the rejected journal is preserved.
        request=dict(self.request,requestId='post-auth-state-race')
        calls=[]
        def concurrent_carrier_change(bound,authorization):
            calls.append(True)
            if len(calls)>1:(self.tree/'source.txt').write_text('changed during final observation\n')
            return self.proof(bound)
        with self.assertRaisesRegex(ValueError,'observation changed'):
            self.apply(request,verifier=concurrent_carrier_change)
        self.assert_untouched()


if __name__ == '__main__':
    unittest.main()
