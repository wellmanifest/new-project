#!/usr/bin/env python3
"""Conservative activity observations in disposable Git repositories."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / f'{name}.py')
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


OVERLAP = load('worktree_overlap_check')
ACTIVITY = load('ticket_activity')


class WorkspaceActivityTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.primary = Path(self.temporary.name) / 'repository'
        self.git('init', '--quiet', '--initial-branch=main', str(self.primary))
        self.git('-C', str(self.primary), 'config', 'user.name', 'Disposable fixture')
        self.git('-C', str(self.primary), 'config', 'user.email', 'fixture@example.invalid')
        (self.primary / '.gitignore').write_text('/.worktrees/\n/.subactor/\n')
        (self.primary / 'source.py').write_text('value = 1\n')
        self.git('-C', str(self.primary), 'add', '.')
        self.git('-C', str(self.primary), 'commit', '--quiet', '-m', 'fixture baseline')

    def git(self, *args):
        return subprocess.run(['git', *args], check=True, capture_output=True, text=True,
                              env=OVERLAP.detached_git_env())

    def report(self):
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/worktree_overlap_check.py'),
                                 '--workspace-root', str(self.primary), '--format', 'json'],
                                capture_output=True, text=True, timeout=30)
        return result.returncode, json.loads(result.stdout)

    def assert_incomplete(self, diagnostic='GOV-WORKTREE-OVERLAP-003'):
        code, report = self.report()
        self.assertEqual(code, 1)
        self.assertEqual(report['status'], 'failed')
        self.assertIn(diagnostic, {f['code'] for f in report['findings']})

    def test_broken_registered_checkout_fails_the_cli_audit(self):
        linked = self.primary / '.worktrees/ticket-001--fixture'
        self.git('-C', str(self.primary), 'worktree', 'add', '--relative-paths',
                 '-b', 'ticket/001-fixture', str(linked))
        self.assertEqual(self.report()[0], 0)
        (linked / '.git').write_text('gitdir: missing-metadata\n')
        self.assert_incomplete()

    def test_failed_registered_inventory_is_not_skipped(self):
        with patch.object(OVERLAP, 'registered_worktrees',
                          side_effect=OVERLAP.AuditError('inventory unavailable')):
            with self.assertRaisesRegex(OVERLAP.AuditError, 'inventory unavailable'):
                OVERLAP.discover_checkouts(self.primary, OVERLAP.DEFAULT_IGNORE)

    def test_active_intent_errors_fail_the_cli_audit(self):
        governance = self.primary / '.governance'
        governance.mkdir()
        (governance / 'manifest.json').write_text(json.dumps(
            {'ticket': {'activeStatuses': ['IN_PROGRESS']}}))
        directory = self.primary / 'project/ticket-001'
        directory.mkdir(parents=True)
        (directory / 'README.md').write_text('- **Status**: IN_PROGRESS\n')
        intent = directory / 'intent.json'
        for value in [None, 'not-json', '[]', '{}',
                      json.dumps({'allowedPaths': [None], 'conflictsWith': []}),
                      json.dumps({'allowedPaths': ['source.py'], 'conflictsWith': 'ticket-002'})]:
            with self.subTest(value=value):
                if value is None:
                    intent.unlink(missing_ok=True)
                else:
                    intent.write_text(value)
                self.assert_incomplete('GOV-TICKET-ACTIVITY-001')
        intent.write_text(json.dumps({'allowedPaths': ['source.py'], 'conflictsWith': []}))
        self.assertEqual(self.report()[0], 0)

    def test_file_and_sqlite_intent_shape_are_checked_consistently(self):
        directory = self.primary / 'project/ticket-001'
        for value in [[], {}, {'allowedPaths': [], 'conflictsWith': []}]:
            with self.subTest(value=value):
                virtual = {'ticket-001': {'intent.json': [json.dumps(value).encode()]}}
                with self.assertRaises(OVERLAP.AuditError):
                    OVERLAP.scope_intent(directory, virtual)

    def test_supported_outstanding_branches_keep_ticket_active(self):
        directory = self.primary / 'project/ticket-001'
        directory.mkdir(parents=True)
        (directory / 'README.md').write_text('- **Status**: IN_PROGRESS\n')
        governance = self.primary / '.governance'
        governance.mkdir()
        policy = json.loads((ROOT / 'governance/ticket-activity.json').read_text())
        # Exercise the existing opt-in ancestry fallback; production defaults
        # and trusted terminal receipt requirements are not changed by this fix.
        policy['registry']['missingPolicy'] = 'git-ancestry'
        (governance / 'ticket-activity.json').write_text(json.dumps(policy))
        self.git('-C', str(self.primary), 'add', '.')
        self.git('-C', str(self.primary), 'commit', '--quiet', '-m', 'fixture ticket')
        base = self.git('-C', str(self.primary), 'rev-parse', 'HEAD').stdout.strip()
        names = ['ticket/001-work', 'ticket-001-work', 'ticket_001-work',
                 'feat/ticket-001-work', 'ticket/1-work', 'Ticket/001-work']
        for name in names:
            for remote_only in [False, True]:
                with self.subTest(branch=name, origin_only=remote_only):
                    self.git('-C', str(self.primary), 'checkout', '--quiet', '-b', name, 'main')
                    (self.primary / 'source.py').write_text('value = 2\n')
                    self.git('-C', str(self.primary), 'commit', '--quiet', '-am', 'fixture outstanding')
                    head = self.git('-C', str(self.primary), 'rev-parse', 'HEAD').stdout.strip()
                    self.assertTrue(ACTIVITY._advanced_ticket_branch(self.primary, 'ticket-001', base, base))
                    self.git('-C', str(self.primary), 'checkout', '--quiet', 'main')
                    if remote_only:
                        self.git('-C', str(self.primary), 'update-ref', 'refs/remotes/origin/' + name, head)
                        self.git('-C', str(self.primary), 'branch', '-D', name)
                    resolution = ACTIVITY.resolve(self.primary, directory, {'IN_PROGRESS'})
                    if remote_only:
                        self.git('-C', str(self.primary), 'update-ref', '-d', 'refs/remotes/origin/' + name)
                    else:
                        self.git('-C', str(self.primary), 'branch', '-D', name)
                    self.assertTrue(resolution.active, resolution)
        self.git('-C', str(self.primary), 'checkout', '--quiet', '-b', 'ticket-0012-unrelated', 'main')
        (self.primary / 'source.py').write_text('value = 4\n')
        self.git('-C', str(self.primary), 'commit', '--quiet', '-am', 'fixture unrelated')
        self.git('-C', str(self.primary), 'checkout', '--quiet', 'main')
        self.assertFalse(ACTIVITY.resolve(self.primary, directory, {'IN_PROGRESS'}).active)

    def test_unreadable_branch_inventory_is_not_an_empty_inventory(self):
        missing = Path(self.temporary.name) / 'not-a-repository'
        missing.mkdir()
        with self.assertRaises(ACTIVITY.ActivityError):
            ACTIVITY._unmerged_ticket_branch(missing, 'ticket-001', 'main')

    def test_adjacent_suffixes_do_not_reserve_another_ticket(self):
        directory = self.primary / 'project/ticket-001'
        directory.mkdir(parents=True)
        (directory / 'README.md').write_text('- **Status**: IN_PROGRESS\n')
        governance = self.primary / '.governance'
        governance.mkdir()
        policy = json.loads((ROOT / 'governance/ticket-activity.json').read_text())
        policy['registry']['missingPolicy'] = 'git-ancestry'
        (governance / 'ticket-activity.json').write_text(json.dumps(policy))
        self.git('-C', str(self.primary), 'add', '.')
        self.git('-C', str(self.primary), 'commit', '--quiet', '-m', 'fixture ticket')
        base = self.git('-C', str(self.primary), 'rev-parse', 'HEAD').stdout.strip()
        spec = importlib.util.spec_from_file_location(
            'bundled_ticket_activity_suffix_fixture',
            ROOT / 'packages/wellman/src/wellman/_bundled/ticket_activity.py')
        bundled = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = bundled
        spec.loader.exec_module(bundled)
        names = ['ticket/001a-other', 'ticket-001feature',
                 'ticket_001Z-work', 'feat/ticket-0012-work']
        for index, name in enumerate(names):
            # A neutral local branch supplies a real outstanding commit for
            # the origin-only case without retaining a matching local ref.
            neutral = f'fixture-{index}'
            self.git('-C', str(self.primary), 'checkout', '--quiet', '-b', neutral, 'main')
            (self.primary / 'source.py').write_text(f'value = {index + 2}\n')
            self.git('-C', str(self.primary), 'commit', '--quiet', '-am', 'fixture outstanding')
            head = self.git('-C', str(self.primary), 'rev-parse', 'HEAD').stdout.strip()
            self.git('-C', str(self.primary), 'checkout', '--quiet', 'main')
            for remote_only in [False, True]:
                ref = ('refs/remotes/origin/' if remote_only else 'refs/heads/') + name
                self.git('-C', str(self.primary), 'update-ref', ref, head)
                for observer in [ACTIVITY, bundled]:
                    with self.subTest(branch=name, origin_only=remote_only,
                                      observer=observer.__name__):
                        self.assertFalse(observer._unmerged_ticket_branch(
                            self.primary, 'ticket-001', 'main'))
                        self.assertFalse(observer.resolve(
                            self.primary, directory, {'IN_PROGRESS'}).active)
                        if not remote_only:
                            self.git('-C', str(self.primary), 'checkout', '--quiet', name)
                            try:
                                self.assertFalse(observer._advanced_ticket_branch(
                                    self.primary, 'ticket-001', base, base))
                            finally:
                                self.git('-C', str(self.primary), 'checkout', '--quiet', 'main')
                self.git('-C', str(self.primary), 'update-ref', '-d', ref)
        # The same outstanding commit with a genuine ticket identity must
        # still reserve the ticket for both the local and origin inventories.
        for ref in ['refs/heads/ticket/001-work',
                    'refs/remotes/origin/Ticket/1-work']:
            self.git('-C', str(self.primary), 'update-ref', ref, head)
            for observer in [ACTIVITY, bundled]:
                with self.subTest(matching=ref, observer=observer.__name__):
                    self.assertTrue(observer._unmerged_ticket_branch(
                        self.primary, 'ticket-001', 'main'))
                    self.assertTrue(observer.resolve(
                        self.primary, directory, {'IN_PROGRESS'}).active)
            self.git('-C', str(self.primary), 'update-ref', '-d', ref)


if __name__ == '__main__':
    unittest.main()
