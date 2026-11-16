"""Actual Git terminal ownership, CAS and interrupted local controller writes."""
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr
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

    def test_declared_no_change_outcome_releases_the_same_lease(self):
        no_change = dict(self.receipt, receiptRef='receipt:test/no-change-123', outcome='no-change')
        activity.record(self.root, no_change)
        self.request['terminalReceiptRef'] = no_change['receiptRef']
        result = self.invoke()
        current = json.loads(self.lease.read_bytes())
        self.assertEqual(result['status'], 'released')
        self.assertEqual((current['phase'], current['leaseRevision'], current['fencingToken']), ('released', 3, 3))
        self.assertEqual(canonical.validate_lease(current), [])

    def test_undeclared_terminal_outcome_is_still_refused(self):
        unknown = dict(self.receipt, receiptRef='receipt:test/superseded-123', outcome='superseded')
        with self.assertRaises(activity.ActivityError):
            activity.record(self.root, unknown)

    def origin_bound_git(self, url='git@github.com:wellmanifest/new-project.git'):
        original = release.git
        def fake(root, *args, **kwargs):
            if args == ('config', '--get', 'remote.origin.url'):
                return url
            return original(root, *args, **kwargs)
        return patch.object(release, 'git', side_effect=fake)

    def test_canonical_repository_identity_is_accepted(self):
        with self.origin_bound_git():
            self.value['repositoryRef'] = 'wellmanifest/new-project'
            self.write_lease()
            self.request['expectedLeaseSha256'] = hashlib.sha256(self.lease.read_bytes()).hexdigest()
            result = self.invoke()
        current = json.loads(self.lease.read_bytes())
        self.assertEqual(result['status'], 'released')
        self.assertEqual((current['phase'], current['leaseRevision'], current['fencingToken']), ('released', 3, 3))

    def test_foreign_repository_identity_still_refuses(self):
        with self.origin_bound_git():
            self.value['repositoryRef'] = 'owner/other-repository'
            self.write_lease()
            self.request['expectedLeaseSha256'] = hashlib.sha256(self.lease.read_bytes()).hexdigest()
            self.refused()

    def test_unqualified_and_foreign_repositories_remain_refused_without_mutation(self):
        for repository, reason in ((self.root.name, 'invalid_canonical_lease'),
                                   ('owner/another-repository', 'repository_identity_mismatch')):
            with self.subTest(repository=repository):
                self.value['repositoryRef'] = repository
                self.write_lease()
                before = self.lease.read_bytes()
                self.request['expectedLeaseSha256'] = hashlib.sha256(before).hexdigest()
                with self.assertRaisesRegex(PermissionError, '^' + reason + '$'):
                    self.invoke(False)
                report = release.settle_verified_leases(self.root, apply=False)
                self.assertFalse(report['grantsAuthority'])
                self.assertEqual(report['settled'], [])
                self.assertEqual(report['skipped'][0]['reason'], reason)
                self.assertEqual(self.lease.read_bytes(), before)

    def test_owner_and_scope_refusals_are_distinct_without_mutation(self):
        before = self.lease.read_bytes()
        self.request['ownerActor'] = 'agent:another-owner'
        with self.assertRaisesRegex(PermissionError, '^current_owner_mismatch$'):
            self.invoke(False)
        self.assertEqual(self.lease.read_bytes(), before)
        self.value['ticketId'] = 'ticket-999'
        self.write_lease()
        before = self.lease.read_bytes()
        with self.assertRaisesRegex(PermissionError, '^lease_scope_mismatch$'):
            self.invoke(False)
        report = release.settle_verified_leases(self.root, apply=False)
        self.assertEqual(report['skipped'][0]['reason'], 'lease_scope_mismatch')
        self.assertEqual(self.lease.read_bytes(), before)

    def test_cli_exposes_only_static_identity_failure_labels(self):
        request = self.root.parent / 'request.json'
        request.write_text(json.dumps(self.request))
        for reason in ('invalid_canonical_lease', 'repository_identity_mismatch', 'current_owner_mismatch', 'lease_scope_mismatch'):
            with self.subTest(reason=reason):
                before = self.lease.read_bytes()
                stderr = io.StringIO()
                with patch.object(release, 'release_owner', side_effect=PermissionError(reason)), redirect_stderr(stderr):
                    code = release.main(['--root', str(self.root), '--request', str(request)])
                self.assertEqual(code, 2)
                self.assertIn('reason=' + reason, stderr.getvalue())
                self.assertEqual(self.lease.read_bytes(), before)

    def test_cli_withholds_unexpected_private_exception_details(self):
        class UnexpectedPermissionError(PermissionError):
            def __str__(self):
                raise AssertionError('Unexpected exception must not be formatted')

        request = self.root.parent / 'request.json'
        request.write_text(json.dumps(self.request))
        before = self.lease.read_bytes()
        for error in (PermissionError('private-fixture-detail'), UnexpectedPermissionError('repository_identity_mismatch')):
            stderr = io.StringIO()
            with patch.object(release, 'release_owner', side_effect=error), redirect_stderr(stderr):
                code = release.main(['--root', str(self.root), '--request', str(request)])
            self.assertEqual(code, 2)
            self.assertIn('GOV-CHANGE-LEASE-002:', stderr.getvalue())
            self.assertNotIn('private-fixture-detail', stderr.getvalue())
            self.assertNotIn('reason=', stderr.getvalue())
            self.assertEqual(self.lease.read_bytes(), before)

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

    def remove_merged_checkout_and_ref(self):
        self.git('worktree', 'remove', str(self.tree))
        self.git('branch', '-d', 'ticket/123-example')

    def test_removed_merged_checkout_and_ref_release_only_current_owner(self):
        self.remove_merged_checkout_and_ref()
        before = self.lease.read_bytes()
        self.assertNotEqual(self.value['headSha'], self.head)
        head = self.git('rev-parse', 'HEAD')
        self.assertEqual(self.invoke(False)['status'], 'planned')
        self.assertEqual(self.lease.read_bytes(), before)
        self.assertEqual(self.invoke()['status'], 'released')
        current = json.loads(self.lease.read_bytes())
        self.assertEqual((current['phase'], current['leaseRevision'], current['fencingToken']), ('released', 3, 3))
        for field in ('ownerActor', 'ownerSession', 'headSha', 'issuedAt', 'expiresAt'):
            self.assertEqual(current[field], self.value[field])
        self.assertEqual(self.invoke()['status'], 'idempotent')
        self.assertFalse(self.tree.exists())
        self.assertEqual(self.git('rev-parse', 'HEAD'), head)
        self.assertEqual(subprocess.run(['git', '-C', str(self.root), 'show-ref', '--verify', '--quiet',
            'refs/heads/ticket/123-example']).returncode, 1)

    def test_removed_ref_nonfrozen_allocation_phases_plan_without_mutation(self):
        self.remove_merged_checkout_and_ref()
        for phase in ('claimed', 'editing', 'validating'):
            with self.subTest(phase=phase):
                self.value['phase'] = phase
                self.write_lease()
                before = self.lease.read_bytes()
                self.request['expectedLeaseSha256'] = hashlib.sha256(before).hexdigest()
                self.assertEqual(self.invoke(False)['status'], 'planned')
                self.assertEqual(self.lease.read_bytes(), before)

    def test_removed_ref_preserves_remaining_checkout_and_symlink(self):
        self.remove_merged_checkout_and_ref()
        self.tree.mkdir()
        retained = self.tree / 'retained.txt'
        retained.write_text('unknown work')
        self.refused()
        self.assertEqual(retained.read_text(), 'unknown work')
        shutil.rmtree(self.tree)
        target = self.root.parent / 'retained-target'
        target.mkdir()
        self.tree.symlink_to(target, target_is_directory=True)
        self.refused()
        self.tree.unlink()
        target.rmdir()
        self.tree.symlink_to(target, target_is_directory=True)
        self.refused()
        self.assertTrue(self.tree.is_symlink())

    def test_removed_ref_preserves_prunable_worktree_registration(self):
        self.git('update-ref', '-d', 'refs/heads/ticket/123-example')
        shutil.rmtree(self.tree)
        before = self.git('worktree', 'list', '--porcelain')
        self.assertIn(str(self.tree), before)
        self.refused()
        self.assertEqual(self.git('worktree', 'list', '--porcelain'), before)

    def test_removed_ref_rejects_allocation_from_unrelated_history(self):
        self.remove_merged_checkout_and_ref()
        tree = self.git('rev-parse', self.head + '^{tree}')
        unrelated = subprocess.check_output(['git', '-C', str(self.root), 'commit-tree', tree],
            input='unrelated root\n', text=True).strip()
        self.value['headSha'] = unrelated
        self.write_lease()
        self.request['expectedLeaseSha256'] = hashlib.sha256(self.lease.read_bytes()).hexdigest()
        self.refused()
        replacement = subprocess.check_output(['git', '-C', str(self.root), 'commit-tree', tree, '-p', unrelated],
            input='replacement ancestry\n', text=True).strip()
        self.git('replace', self.head, replacement)
        self.refused()

    def test_removed_ref_rejects_unverified_terminal_receipt(self):
        self.remove_merged_checkout_and_ref()
        self.git('reset', '--hard', self.value['headSha'])
        self.refused()

    def test_removed_ref_still_requires_owner_and_exact_cas(self):
        self.remove_merged_checkout_and_ref()
        for field, value in [('ownerSession', 'another-session'), ('ownerActor', 'agent:other'),
                             ('expectedRevision', 2), ('expectedFencingToken', 2),
                             ('expectedLeaseSha256', 'f'*64), ('ownerHandoff', False)]:
            with self.subTest(field=field):
                original = self.request[field]
                self.request[field] = value
                self.refused()
                self.request[field] = original

    def test_removed_ref_never_replaces_reviewed_publication_head(self):
        self.remove_merged_checkout_and_ref()
        for phase in ('approved', 'merged', 'closed'):
            with self.subTest(phase=phase):
                self.value.update(phase=phase, publicationFrozen=phase in canonical.FROZEN_PHASES,
                                  pullRequest=1, validatorRunId='fixture-validator')
                self.write_lease()
                self.request['expectedLeaseSha256'] = hashlib.sha256(self.lease.read_bytes()).hexdigest()
                self.refused()

    def test_removed_ref_git_observation_errors_fail_closed(self):
        self.remove_merged_checkout_and_ref()
        original = release.git
        for command in ('worktree', 'for-each-ref', 'merge-base'):
            with self.subTest(command=command):
                def unavailable(root, *args, **kwargs):
                    if command in args:
                        raise PermissionError('git_observation_unavailable')
                    return original(root, *args, **kwargs)
                with patch.object(release, 'git', side_effect=unavailable):
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


@unittest.skipUnless(os.name == 'posix', 'POSIX local controller adapter; unsupported hosts tested separately')
class ControllerVerifiedSettlement(unittest.TestCase):
    setUp = TerminalOwnerRelease.setUp
    git = TerminalOwnerRelease.git
    write_lease = TerminalOwnerRelease.write_lease
    remove_merged_checkout_and_ref = TerminalOwnerRelease.remove_merged_checkout_and_ref

    def copy_controller_scripts(self):
        for name in ('terminal_lease_release.py', 'change_lease_check.py', 'ticket_activity.py'):
            (self.root / '.governance' / name).write_bytes((ROOT / 'scripts' / name).read_bytes())
        (self.root / '.governance/change-lease.schema.json').write_bytes(
            (ROOT / 'subprojects/change-lease/change-lease.schema.json').read_bytes())

    def test_settle_verified_plan_then_apply_and_idempotent_without_owner_session(self):
        before = self.lease.read_bytes()
        planned = release.settle_verified_leases(self.root, apply=False)
        self.assertEqual(planned['mode'], 'plan')
        self.assertEqual(planned['grantsAuthority'], False)
        self.assertEqual(len(planned['settled']), 1)
        self.assertEqual(planned['settled'][0]['status'], 'planned')
        self.assertEqual(planned['settled'][0]['settledBy'], release.SETTLED_BY)
        self.assertEqual(planned['settled'][0]['terminalReceiptRef'], self.receipt['receiptRef'])
        self.assertEqual(self.lease.read_bytes(), before)

        self.copy_controller_scripts()
        clean_env = {k: v for k, v in os.environ.items() if not k.startswith('NEW_PROJECT_WRITER_')}
        cmd = [sys.executable, '-I', str(self.root / '.governance/terminal_lease_release.py'),
               '--root', str(self.root), '--settle-verified']
        cli_plan = subprocess.run(cmd, env=clean_env, capture_output=True, text=True, check=True, timeout=20)
        self.assertEqual(json.loads(cli_plan.stdout)['settled'][0]['status'], 'planned')
        self.assertEqual(self.lease.read_bytes(), before)

        cli_apply = subprocess.run(cmd + ['--apply'], env=clean_env, capture_output=True, text=True, check=True, timeout=20)
        report = json.loads(cli_apply.stdout)
        self.assertEqual(len(report['settled']), 1)
        item = report['settled'][0]
        self.assertEqual(item['status'], 'released')
        self.assertEqual(item['settledBy'], 'controller:verified-terminal-receipt')
        self.assertEqual(item['terminalReceiptRef'], self.receipt['receiptRef'])

        current = json.loads(self.lease.read_bytes())
        self.assertEqual((current['phase'], current['leaseRevision'], current['fencingToken']), ('released', 3, 3))
        self.assertEqual(canonical.validate_lease(current), [])

        receipt_doc = json.loads(Path(item['receipt']).read_text())
        self.assertEqual(receipt_doc['schema'], release.SETTLEMENT_SCHEMA)
        self.assertEqual(receipt_doc['settledBy'], 'controller:verified-terminal-receipt')
        self.assertEqual(receipt_doc['terminalReceiptRef'], self.receipt['receiptRef'])
        self.assertEqual(receipt_doc['settlement']['settledBy'], 'controller:verified-terminal-receipt')
        self.assertTrue(all(t['outcome'] == 'accepted' for t in receipt_doc['transitions']))

        repeat = subprocess.run(cmd + ['--ticket', 'ticket-123', '--apply'],
                                env=clean_env, capture_output=True, text=True, check=True, timeout=20)
        repeat_report = json.loads(repeat.stdout)
        self.assertEqual(repeat_report['settled'], [])
        self.assertEqual(repeat_report['skipped'][0]['reason'], 'already_released')
        self.assertEqual(json.loads(self.lease.read_bytes())['leaseRevision'], 3)

    def test_settle_verified_supports_all_settleable_phases_and_removed_checkout(self):
        for phase in ('claimed', 'editing', 'validating', 'approved', 'merged', 'closed'):
            with self.subTest(phase=phase):
                self.value.update(
                    phase=phase,
                    publicationFrozen=(phase in canonical.FROZEN_PHASES),
                    headSha=self.head if phase in {'approved', 'merged', 'closed'} else self.value['headSha'],
                    pullRequest=1 if phase in {'approved', 'merged', 'closed'} else None,
                    validatorRunId='fixture-validator' if phase in {'approved', 'merged', 'closed'} else None,
                    leaseRevision=1,
                    fencingToken=1,
                    eventSequence=1,
                    previousReceiptRef=None,
                )
                self.write_lease()
                report = release.settle_verified_leases(self.root, ticket='ticket-123', apply=True)
                self.assertEqual(len(report['settled']), 1)
                self.assertEqual(json.loads(self.lease.read_bytes())['phase'], 'released')

        self.remove_merged_checkout_and_ref()
        self.value.update(
            phase='claimed',
            publicationFrozen=False,
            headSha=self.git('rev-parse', 'HEAD~1'),
            pullRequest=None,
            validatorRunId=None,
            leaseRevision=1,
            fencingToken=1,
            eventSequence=1,
            previousReceiptRef=None,
        )
        self.write_lease()
        report = release.settle_verified_leases(self.root, ticket='ticket-123', apply=True)
        self.assertEqual(report['settled'][0]['status'], 'released')
        self.assertEqual(json.loads(self.lease.read_bytes())['phase'], 'released')

    def test_settle_verified_skips_unmerged_dirty_frozen_and_ambiguous_leases(self):
        unmerged = dict(self.value, leaseId='allocation-124', ticketId='ticket-124',
                        branchRef='refs/heads/ticket/124-unmerged', worktreeId='ticket-124--unmerged')
        (self.lease.parent / 'ticket-124--unmerged.json').write_text(json.dumps(unmerged))

        frozen = dict(self.value, leaseId='allocation-125', ticketId='ticket-125',
                      branchRef='refs/heads/ticket/125-frozen', worktreeId='ticket-125--frozen',
                      phase='publication_frozen', publicationFrozen=True, headSha=self.head, pullRequest=2)
        (self.lease.parent / 'ticket-125--frozen.json').write_text(json.dumps(frozen))
        activity.record(self.root, dict(self.receipt, receiptRef='receipt:test/merged-125', ticket='ticket-125'))

        tree_dirty = self.root / '.worktrees/ticket-126--dirty'
        self.git('worktree', 'add', '-qb', 'ticket/126-dirty', str(tree_dirty), self.head)
        (tree_dirty / 'unpublished.txt').write_text('dirty')
        dirty_lease = dict(self.value, leaseId='allocation-126', ticketId='ticket-126',
                           branchRef='refs/heads/ticket/126-dirty', worktreeId='ticket-126--dirty')
        (self.lease.parent / 'ticket-126--dirty.json').write_text(json.dumps(dirty_lease))
        activity.record(self.root, dict(self.receipt, receiptRef='receipt:test/merged-126', ticket='ticket-126'))

        alt_branch = 'ticket/127-ambiguous'
        tree_alt = self.root / '.worktrees/ticket-127--ambiguous'
        base_sha = self.value['headSha']
        self.git('worktree', 'add', '-qb', alt_branch, str(tree_alt), base_sha)
        (tree_alt / 'alt1.txt').write_text('one')
        self.git('add', '.', root=tree_alt)
        self.git('commit', '-qm', 'alt1', root=tree_alt)
        head1 = self.git('rev-parse', 'HEAD', root=tree_alt)
        self.git('merge', '--no-ff', '-qm', 'merge alt1', alt_branch)
        term1 = self.git('rev-parse', 'HEAD')
        (tree_alt / 'alt2.txt').write_text('two')
        self.git('add', '.', root=tree_alt)
        self.git('commit', '-qm', 'alt2', root=tree_alt)
        head2 = self.git('rev-parse', 'HEAD', root=tree_alt)
        self.git('merge', '--no-ff', '-qm', 'merge alt2', alt_branch)
        term2 = self.git('rev-parse', 'HEAD')
        self.git('worktree', 'remove', str(tree_alt))
        self.git('branch', '-d', alt_branch)
        ambiguous_lease = dict(self.value, leaseId='allocation-127', ticketId='ticket-127',
                               branchRef='refs/heads/ticket/127-ambiguous', worktreeId='ticket-127--ambiguous')
        (self.lease.parent / 'ticket-127--ambiguous.json').write_text(json.dumps(ambiguous_lease))
        activity.record(self.root, {'receiptRef': 'receipt:test/amb-1', 'ticket': 'ticket-127', 'outcome': 'merged',
                                    'headSha': head1, 'terminalSha': term1, 'targetBranch': 'main', 'occurredAt': '2026-10-28T01:00:00Z'})
        activity.record(self.root, {'receiptRef': 'receipt:test/amb-2', 'ticket': 'ticket-127', 'outcome': 'merged',
                                    'headSha': head2, 'terminalSha': term2, 'targetBranch': 'main', 'occurredAt': '2026-10-28T01:05:00Z'})

        report = release.settle_verified_leases(self.root, apply=True)
        self.assertEqual([item['ticketId'] for item in report['settled']], ['ticket-123'])
        reasons = {item['ticketId']: item['reason'] for item in report['skipped']}
        self.assertEqual(reasons['ticket-124'], 'matching_merged_receipt_required')
        self.assertEqual(reasons['ticket-125'], 'phase_requires_existing_controller_reconciliation')
        self.assertEqual(reasons['ticket-126'], 'worktree_has_unpublished_work')
        self.assertEqual(reasons['ticket-127'], 'ambiguous_terminal_receipts')

        with self.assertRaises(PermissionError):
            release.settle_verified_leases(self.root, ticket='ticket-124', apply=True)
        with self.assertRaises(PermissionError):
            release.settle_verified_leases(self.root, ticket='ticket-999', apply=False)

    def test_settle_verified_cas_lock_and_write_ahead_recovery(self):
        import fcntl
        lock = self.lease.with_name(self.lease.name + '.lock')
        with lock.open('w') as held:
            fcntl.flock(held, fcntl.LOCK_EX | fcntl.LOCK_NB)
            with self.assertRaises(OSError):
                release.settle_verified_leases(self.root, ticket='ticket-123', apply=True)
        self.assertEqual(json.loads(self.lease.read_bytes())['phase'], 'claimed')

        before = self.lease.read_bytes()
        with patch.object(release, '_replace_lease', side_effect=OSError('injected interruption')):
            with self.assertRaises(PermissionError):
                release.settle_verified_leases(self.root, ticket='ticket-123', apply=True)
        self.assertEqual(self.lease.read_bytes(), before)

        recovered = release.settle_verified_leases(self.root, ticket='ticket-123', apply=True)
        self.assertEqual(recovered['settled'][0]['status'], 'released')
        self.assertEqual(json.loads(self.lease.read_bytes())['leaseRevision'], 3)


class PlatformBoundary(unittest.TestCase):
    def test_unsupported_controller_refuses_before_filesystem_effect(self):
        request = {'schema': release.REQUEST_SCHEMA, 'requestId': 'unsupported', 'worktreeId': 'ticket-123--example',
            'ownerActor': 'agent:fixture', 'ownerSession': 'session', 'ownerHandoff': True,
            'expectedRevision': 1, 'expectedFencingToken': 1, 'expectedLeaseSha256': 'a'*64,
            'terminalReceiptRef': 'receipt:test/terminal'}
        with patch.object(release.os, 'name', 'unsupported'):
            with self.assertRaisesRegex(PermissionError, 'posix_controller_required'):
                release.release_owner('unavailable', request, apply=True)
            with self.assertRaisesRegex(PermissionError, 'posix_controller_required'):
                release.settle_verified_leases('unavailable', apply=True)


if __name__ == '__main__':
    unittest.main()
