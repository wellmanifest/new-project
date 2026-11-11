"""Real Git histories exercise batch invalidation and invocation isolation."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import ticket_activity as activity
import worktree_overlap_check as overlap

SOURCE = Path(__file__).resolve().parents[1]


class BatchTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'repo'
        self.root.mkdir()
        self.git('init', '-q', '--initial-branch=main')
        self.git('config', 'user.name', 'activity-test')
        self.git('config', 'user.email', 'activity@example.invalid')
        self.git('remote', 'add', 'origin', 'https://example.invalid/shared.git')
        (self.root / 'governance').mkdir()
        shutil.copyfile(SOURCE / 'governance/ticket-activity.json', self.root / 'governance/ticket-activity.json')
        self.tickets = []
        for number in range(1, 41):
            directory = self.root / 'project' / f'ticket-{number:03}'
            directory.mkdir(parents=True)
            (directory / 'README.md').write_text('- **Status**: IN_PROGRESS\n')
            (directory / 'intent.json').write_text(json.dumps({'allowedPaths': [f'src/{number}.py']}))
            self.tickets.append(directory)
        self.git('add', '.')
        self.git('commit', '-qm', 'tickets')
        self.head = self.git('rev-parse', 'HEAD')
        (self.root / 'delivery').write_text('delivered')
        self.git('add', '.')
        self.git('commit', '-qm', 'integrate')
        self.terminal = self.git('rev-parse', 'HEAD')
        self.registry = activity.registry_path(self.root)
        self.registry.parent.mkdir(parents=True)
        self.registry.write_text(json.dumps({
            'schema': 'new-project.terminal-receipt-registry/v1',
            'repositoryRef': activity.repository_ref(self.root),
            'receipts': [dict(receiptRef=f'receipt:test/{t.name}', ticket=t.name,
                             outcome='merged', headSha=self.head, terminalSha=self.terminal,
                             targetBranch='main', occurredAt='2026-09-14T08:00:00Z') for t in self.tickets]}))

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.root), *args], text=True, stderr=subprocess.DEVNULL).strip()

    def resolve(self, index=0):
        return activity.resolve(self.root, self.tickets[index], {'IN_PROGRESS'})

    def test_batch_parity_and_subprocess_bound(self):
        with patch.object(activity.subprocess, 'run', wraps=subprocess.run) as calls:
            ordinary = [self.resolve(i) for i in range(len(self.tickets))]
            baseline = calls.call_count
        with patch.object(activity.subprocess, 'run', wraps=subprocess.run) as calls:
            with activity.ActivityReadBatch(self.root):
                batched = [self.resolve(i) for i in range(len(self.tickets))]
            optimized = calls.call_count
        self.assertEqual(ordinary, batched)
        self.assertTrue(all(not r.active for r in batched))
        self.assertLess(optimized, baseline // 2, (baseline, optimized))
        print(f'activity subprocesses: standalone={baseline}, batch={optimized}, tickets={len(self.tickets)}')

    def assert_invalidated(self, mutate):
        with self.assertRaisesRegex(activity.ActivityError, 'changed'):
            with activity.ActivityReadBatch(self.root):
                self.assertFalse(self.resolve().active)
                mutate()
        self.assertIsNone(activity._READ_BATCH.get())

    def test_target_ref_changed(self):
        self.assert_invalidated(lambda: self.git('update-ref', 'refs/heads/main', self.head))
        self.assertTrue(self.resolve().active)

    def test_remote_target_appears(self):
        self.assert_invalidated(lambda: self.git('update-ref', 'refs/remotes/origin/main', self.head))

    def test_registry_changed(self):
        self.assert_invalidated(lambda: self.registry.write_text('{}'))
        with self.assertRaises(activity.ActivityError):
            self.resolve()

    def test_registry_created_after_absence(self):
        saved = self.registry.read_text()
        self.registry.unlink()
        with self.assertRaisesRegex(activity.ActivityError, 'changed'):
            with activity.ActivityReadBatch(self.root):
                self.assertTrue(self.resolve().active)
                self.registry.write_text(saved)

    def test_policy_changed(self):
        self.assert_invalidated(lambda: (self.root / 'governance/ticket-activity.json').write_text('{}'))

    def test_override_appears(self):
        self.assert_invalidated(lambda: (self.root / 'governance/ticket-activity.override.json').write_text('{}'))

    def test_projection_changed(self):
        self.assert_invalidated(lambda: (self.tickets[0] / 'README.md').write_text('- **Status**: BLOCKED\n'))

    def test_missing_projection_created(self):
        readme = self.tickets[0] / 'README.md'
        readme.unlink()
        self.assert_invalidated(lambda: readme.write_text('- **Status**: IN_PROGRESS\n'))

    def test_ticket_inventory_changed(self):
        self.assert_invalidated(lambda: (self.root / 'project/ticket-041').mkdir())

    def test_checkout_changed(self):
        self.assert_invalidated(lambda: self.git('switch', '-qc', 'another-branch'))

    def test_registry_repository_binding_still_enforced(self):
        self.assert_invalidated(lambda: self.git('remote', 'set-url', 'origin', 'https://example.invalid/other.git'))
        with self.assertRaises(activity.ActivityError):
            self.resolve()

    def test_next_invocation_observes_reactivated_ticket(self):
        batch = activity.ActivityReadBatch(self.root)
        with batch:
            self.assertFalse(self.resolve().active)
        self.assertEqual(batch.queries, {})
        self.assertEqual(batch.files, {})
        self.assertEqual(batch.ancestors, {})
        self.assertEqual(batch.derived, {})
        self.git('switch', '-qc', 'ticket/001-followup')
        (self.root / 'followup').write_text('new work')
        self.git('add', '.')
        self.git('commit', '-qm', 'reopen')
        with batch:
            self.assertTrue(self.resolve().active)

    def test_same_remote_independent_clone_has_no_shared_receipts(self):
        clone = Path(self.temp.name) / 'clone'
        self.git('clone', '-q', str(self.root), str(clone))
        subprocess.check_call(['git', '-C', str(clone), 'remote', 'set-url', 'origin', 'https://example.invalid/shared.git'])
        with activity.ActivityReadBatch(self.root):
            self.assertFalse(self.resolve().active)
            with self.assertRaisesRegex(activity.ActivityError, 'cross checkouts'):
                activity.resolve(clone, clone / 'project/ticket-001', {'IN_PROGRESS'})
            with activity.ActivityReadBatch(clone):
                self.assertTrue(activity.resolve(clone, clone / 'project/ticket-001', {'IN_PROGRESS'}).active)
            self.assertFalse(self.resolve().active)

    def test_ancestry_policy_rechecks_branch_object_ids(self):
        self.registry.unlink()
        policy = self.root / 'governance/ticket-activity.json'
        value = json.loads(policy.read_text())
        value['registry']['missingPolicy'] = 'git-ancestry'
        policy.write_text(json.dumps(value))
        self.git('branch', 'ticket/001-followup', self.head)
        self.assert_invalidated(lambda: self.git('update-ref', 'refs/heads/ticket/001-followup', self.terminal))

    def test_git_ancestry_batch_avoids_per_ticket_cat_file_and_ancestor_subprocesses(self):
        self.registry.unlink()
        policy = self.root / 'governance/ticket-activity.json'
        value = json.loads(policy.read_text())
        value['registry']['missingPolicy'] = 'git-ancestry'
        policy.write_text(json.dumps(value))
        self.git('branch', 'ticket/002-active', self.terminal)
        (self.root / 'extra').write_text('unmerged')
        self.git('switch', '-q', 'ticket/002-active')
        self.git('add', 'extra')
        self.git('commit', '-qm', 'unmerged ticket branch')
        self.git('switch', '-q', 'main')

        with patch.object(activity.subprocess, 'run', wraps=subprocess.run) as calls:
            ordinary = [self.resolve(i) for i in range(len(self.tickets))]
            baseline = calls.call_count
        with patch.object(activity.subprocess, 'run', wraps=subprocess.run) as calls:
            with activity.ActivityReadBatch(self.root):
                batched = [self.resolve(i) for i in range(len(self.tickets))]
            optimized = calls.call_count

        self.assertEqual(ordinary, batched)
        self.assertEqual([r.ticket for r in batched if r.active], ['ticket-002'])
        self.assertLessEqual(optimized, 20, (baseline, optimized))
        self.assertLess(optimized * 4, baseline, (baseline, optimized))

    def test_scoped_overlap_discovery_skips_unrelated_identity_ticket_scopes(self):
        workspace = Path(self.temp.name) / 'workspace'
        workspace.mkdir()
        target_repo = workspace / 'target'
        sibling_repo = workspace / 'sibling'
        shutil.copytree(self.root, target_repo)
        shutil.copytree(self.root, sibling_repo)
        subprocess.check_call(['git', '-C', str(target_repo), 'remote', 'set-url', 'origin', 'https://example.invalid/target.git'])
        subprocess.check_call(['git', '-C', str(sibling_repo), 'remote', 'set-url', 'origin', 'https://example.invalid/sibling.git'])
        (target_repo / 'dirty.txt').write_text('target edit\n')
        (sibling_repo / 'dirty.txt').write_text('sibling edit\n')

        only_identity = overlap.repository_identity(target_repo)
        with patch.object(overlap, 'ticket_scopes', wraps=overlap.ticket_scopes) as scope_calls:
            checkouts = overlap.discover_checkouts(workspace, overlap.DEFAULT_IGNORE, only_identity)
        self.assertEqual(len(checkouts), 2)
        self.assertEqual([call.args[0] for call in scope_calls.call_args_list], [target_repo.resolve()])

    def test_failed_batch_cannot_produce_clean_overlap_report(self):
        original = overlap.resolve_ticket_activity
        changed = False
        def mutate(*args, **kwargs):
            nonlocal changed
            result = original(*args, **kwargs)
            if not changed:
                self.registry.write_text('{}')
                changed = True
            return result
        with patch.object(overlap, 'active_statuses', return_value={'IN_PROGRESS'}), patch.object(overlap, 'resolve_ticket_activity', side_effect=mutate):
            _, errors = overlap.ticket_scopes(self.root)
        self.assertTrue(any('changed' in e for e in errors), errors)

    def test_transient_git_invalidation_retries_once_and_persistent_git_churn_fails_closed(self):
        original = overlap.resolve_ticket_activity
        flips = 0

        def transient_git_flip(*args, **kwargs):
            nonlocal flips
            result = original(*args, **kwargs)
            if flips == 0:
                self.git('update-ref', 'refs/remotes/origin/main', self.head)
                flips += 1
            return result

        with patch.object(overlap, 'active_statuses', return_value={'IN_PROGRESS'}), patch.object(
            overlap, 'resolve_ticket_activity', side_effect=transient_git_flip
        ):
            scopes, errors = overlap.ticket_scopes(self.root)
        self.assertEqual(errors, ())
        self.assertEqual(len(scopes), len(self.tickets))

        step = 0

        def persistent_git_flip(*args, **kwargs):
            nonlocal step
            result = original(*args, **kwargs)
            if args[1] == self.tickets[0]:
                target_sha = self.terminal if step % 2 == 0 else self.head
                self.git('update-ref', 'refs/remotes/origin/main', target_sha)
                step += 1
            return result

        with patch.object(overlap, 'active_statuses', return_value={'IN_PROGRESS'}), patch.object(
            overlap, 'resolve_ticket_activity', side_effect=persistent_git_flip
        ):
            _, persistent_errors = overlap.ticket_scopes(self.root)
        self.assertTrue(any('Git state changed during activity inspection; retry' in e for e in persistent_errors))

    def test_sibling_worktree_commit_does_not_invalidate_inspected_checkout_batch(self):
        sibling_a = Path(self.temp.name) / 'wt-099'
        sibling_b = Path(self.temp.name) / 'wt-100'
        self.git('worktree', 'add', '-q', '-b', 'ticket/099-sibling', str(sibling_a), 'main')

        # 1. Terminal-receipt mode: sibling commit + new sibling worktree mid-batch succeed.
        with activity.ActivityReadBatch(self.root):
            self.assertFalse(self.resolve(0).active)
            (sibling_a / 'sibling.txt').write_text('disjoint work\n')
            subprocess.check_call(['git', '-C', str(sibling_a), 'add', 'sibling.txt'])
            subprocess.check_call(['git', '-C', str(sibling_a), 'commit', '-qm', 'sibling commit 1'])
            self.git('worktree', 'add', '-q', '-b', 'ticket/100-sibling', str(sibling_b), 'main')

        # 2. git-ancestry mode: unconsulted sibling ticket commit mid-batch succeeds.
        self.registry.unlink()
        policy = self.root / 'governance/ticket-activity.json'
        value = json.loads(policy.read_text())
        value['registry']['missingPolicy'] = 'git-ancestry'
        policy.write_text(json.dumps(value))

        with activity.ActivityReadBatch(self.root):
            self.assertFalse(self.resolve(0).active)
            (sibling_b / 'sibling2.txt').write_text('more disjoint work\n')
            subprocess.check_call(['git', '-C', str(sibling_b), 'add', 'sibling2.txt'])
            subprocess.check_call(['git', '-C', str(sibling_b), 'commit', '-qm', 'sibling commit 2'])

        # 3. Mutating the inspected worktree's own registration (e.g. locking it) still invalidates.
        with self.assertRaisesRegex(activity.ActivityError, 'changed'):
            with activity.ActivityReadBatch(sibling_a):
                self.assertTrue(activity.resolve(sibling_a, sibling_a / 'project/ticket-001', {'IN_PROGRESS'}).active)
                self.git('worktree', 'lock', str(sibling_a))


if __name__ == '__main__':
    unittest.main()
