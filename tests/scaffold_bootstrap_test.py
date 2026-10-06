#!/usr/bin/env python3
"""Real first-allocation regression; publication is mocked only in fixtures."""
from pathlib import Path
import importlib.util
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
CHANGED = ('project/new-ticket.sh', 'scripts/create_adoption_lock.py', 'scripts/work_start_check.py')


class BootstrapTest(unittest.TestCase):
    fresh = False
    legacy_carriers = False
    expected_ticket = 'ticket-001'

    def command(self, cwd, *args, check=True):
        result = subprocess.run(args, cwd=cwd, capture_output=True, text=True,
                                env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
        if check and result.returncode:
            self.fail(result.stdout + result.stderr)
        return result

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.source = self.base / 'standard'
        self.target = self.base / 'product'
        self.command(self.base, 'git', 'clone', '--quiet', '--no-hardlinks', str(ROOT), str(self.source))
        if not os.environ.get('NP_TEST_BASELINE'):
            for rel in CHANGED:
                shutil.copy2(ROOT / rel, self.source / rel)
        self.command(self.source, 'git', 'config', 'user.name', 'Fixture')
        self.command(self.source, 'git', 'config', 'user.email', 'fixture@example.invalid')
        self.command(self.source, 'git', 'add', *CHANGED)
        self.command(self.source, 'git', 'commit', '--quiet', '--allow-empty', '-m', 'Fixture source')
        revision = self.command(self.source, 'git', 'rev-parse', 'HEAD').stdout.strip()
        self.command(self.base, 'git', 'init', '--quiet', '-b', 'main', str(self.target))
        self.command(self.target, 'git', 'config', 'user.name', 'Fixture')
        self.command(self.target, 'git', 'config', 'user.email', 'fixture@example.invalid')
        (self.target / '.governance').mkdir()
        if not self.fresh:
            (self.target / '.governance/manifest.json').write_text(json.dumps({
                'schema': 'wellmanifest.manifest/v1',
                'standard': {'id': 'profile:baseline', 'version': '0.20.37'}}))
        (self.target / 'README.md').write_text('# Product\n')
        (self.target / '.gitignore').write_text('/.worktrees/\n/.subactor/receipts/\n')
        (self.target / 'foreign.txt').write_text('original\n')
        if self.legacy_carriers:
            carrier = self.target / 'project/ticket-007'
            carrier.mkdir(parents=True)
            (carrier / 'README.md').write_text('# Historical ticket\nStatus: IN_PROGRESS\n')
            (carrier / 'intent.json').write_text('{"ticket":"ticket-007","allowedPaths":["old.py"]}\n')
        self.command(self.target, 'git', 'add', '.')
        self.command(self.target, 'git', 'commit', '--quiet', '-m', 'Legacy scaffold')
        self.head = self.command(self.target, 'git', 'rev-parse', 'HEAD').stdout.strip()
        for rel in ['VERSION', 'CHANGELOG.md', 'TODO.md', 'project/TICKETS.md']:
            p = self.target / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text('0.1.0\n' if rel == 'VERSION' else '# Fixture\n')
        spec = importlib.util.spec_from_file_location('fixture_adopter', self.source / CHANGED[1])
        self.adopter = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.adopter)
        args = ['adopter', '--target-root', str(self.target), '--source-revision', revision,
                '--bootstrap-native-adoption' if self.fresh else '--migrate-wellman-scaffold',
                '--upgrade']
        with patch.object(sys, 'argv', args), patch.object(self.adopter, 'verify_publication_evidence'):
            self.assertEqual(self.adopter.main(), 0)
        self.receipt = self.target / '.subactor/receipts/bootstrap-adoption.json'
        self.assertTrue(self.receipt.is_file(), 'installer must record exact bootstrap bytes')

    def observation(self, checksum=None):
        args = ['python3', '.governance/work_start_check.py', '--root', '.',
                '--workstream', 'governance', '--path', '.governance/**', '--allocation-check']
        if checksum:
            args += ['--bootstrap-adoption-digest', checksum]
        result = self.command(self.target, *args, check=False)
        return result, json.loads(result.stdout)

    def checksum(self):
        # Malformed legacy inputs may refuse before a complete admission report;
        # obtain the exact dirty binding independently through the managed reader.
        result = self.command(self.target, sys.executable, '-c',
            "import sys; from pathlib import Path; sys.path.insert(0, '.governance'); "
            "import work_start_check; print(work_start_check.dirty_observation(Path('.'))[1])")
        return result.stdout.strip()

    def test_first_real_allocator_preserves_foreign_bytes_and_does_not_write_source(self):
        (self.target / 'foreign.txt').write_text('another writer\n')
        checksum = self.checksum()
        result, before = self.observation()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(before['route'], 'RECONCILE')
        result, admitted = self.observation(checksum)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(admitted['route'], 'NEW_TICKET_CANDIDATE')
        self.assertFalse(admitted['grantsAuthority'])
        args = ['bash', './project/new-ticket.sh', '--title', 'Adopt governance', '--agent', 'fixture',
                '--workstream', 'governance', '--path', '.governance/**',
                '--worktree-slug', 'adoption', '--bootstrap-adoption-digest', checksum]
        result = self.command(self.target, *args)
        self.assertIn('Successfully allocated ' + self.expected_ticket, result.stdout)
        wt = self.target / ('.worktrees/' + self.expected_ticket + '--adoption')
        intent = json.loads((wt / 'project' / self.expected_ticket / 'intent.json').read_text())
        self.assertIn('.governance/**', intent['allowedPaths'])
        self.assertEqual(self.command(wt, 'git', 'rev-parse', 'HEAD').stdout.strip(), self.head)
        # The allocator writes metadata only: product and adoption source stay on their old base.
        self.assertEqual((wt / 'foreign.txt').read_text(), 'original\n')
        self.assertEqual((self.target / 'foreign.txt').read_text(), 'another writer\n')
        if self.fresh:
            self.assertFalse((wt / '.governance/manifest.json').exists())
        else:
            self.assertEqual(json.loads((wt / '.governance/manifest.json').read_text())['schema'],
                             'wellmanifest.manifest/v1')
        result, _ = self.observation(checksum)
        self.assertNotEqual(result.returncode, 0, 'second allocation must not reuse bootstrap acknowledgement')

    def test_changed_installed_bytes_are_not_acknowledged(self):
        p = self.target / '.governance/manifest.json'
        p.write_text(p.read_text() + '\n')
        result, _ = self.observation(self.checksum())
        self.assertNotEqual(result.returncode, 0)

    def test_stale_observation_is_rejected(self):
        checksum = self.checksum()
        (self.target / 'foreign.txt').write_text('concurrent change\n')
        result, _ = self.observation(checksum)
        self.assertNotEqual(result.returncode, 0)

    def test_receipt_cannot_claim_foreign_path(self):
        receipt = json.loads(self.receipt.read_text())
        receipt['files']['foreign.txt'] = hashlib.sha256((self.target / 'foreign.txt').read_bytes()).hexdigest()
        self.receipt.write_text(json.dumps(receipt))
        result, _ = self.observation(self.checksum())
        self.assertNotEqual(result.returncode, 0)

    def test_overlapping_foreign_governance_change_still_blocks(self):
        (self.target / '.governance/foreign.json').write_text('{}\n')
        result, report = self.observation(self.checksum())
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(report['blockers'])

    def test_moved_head_is_rejected(self):
        no_hooks = self.base / 'fixture-no-hooks'
        no_hooks.mkdir()
        # Isolated malformed-state fixture; production hooks remain required.
        self.command(self.target, 'git', '-c', f'core.hooksPath={no_hooks}',
                     'commit', '--quiet', '--allow-empty', '-m', 'Another head')
        result, _ = self.observation(self.checksum())
        self.assertNotEqual(result.returncode, 0)

    def test_receipt_cannot_grant_writer_authority(self):
        receipt = json.loads(self.receipt.read_text())
        receipt['grantsWriterAuthority'] = True
        self.receipt.write_text(json.dumps(receipt))
        result, _ = self.observation(self.checksum())
        self.assertNotEqual(result.returncode, 0)

    def test_change_between_bootstrap_proof_and_entry_observation_is_rejected(self):
        checksum = self.checksum()
        spec = importlib.util.spec_from_file_location(
            'bootstrap_race_probe', self.target / '.governance/work_start_check.py')
        module = importlib.util.module_from_spec(spec)
        with patch.object(sys, 'path', [str(self.target / '.governance'), *sys.path]):
            spec.loader.exec_module(module)
        original = module.dirty_observation
        calls = 0

        def observed(root):
            nonlocal calls
            calls += 1
            if calls == 2:
                path = self.target / '.governance/manifest.json'
                path.write_text(path.read_text() + '\n')
            return original(root)

        with patch.object(module, 'dirty_observation', observed):
            with self.assertRaisesRegex(module.ObservationError, 'Bootstrap changed during admission'):
                module.inspect(self.target, 'governance', ['.governance/**'],
                               bootstrap_adoption_digest=checksum)

    def test_receipt_from_other_clone_is_rejected(self):
        receipt = json.loads(self.receipt.read_text())
        receipt['commonGitDir'] = str(self.source / '.git')
        self.receipt.write_text(json.dumps(receipt))
        result, _ = self.observation(self.checksum())
        self.assertNotEqual(result.returncode, 0)


class FreshBootstrapTest(BootstrapTest):
    fresh = True

    def test_fresh_receipt_records_absent_original_governance(self):
        receipt = json.loads(self.receipt.read_text())
        self.assertEqual(receipt['bootstrapKind'], 'fresh')
        self.assertFalse(receipt['grantsWriterAuthority'])
        self.assertFalse(receipt['grantsPublicationAuthority'])
        result, _ = self.observation(self.checksum())
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_unknown_bootstrap_kind_is_rejected(self):
        receipt = json.loads(self.receipt.read_text())
        receipt['bootstrapKind'] = 'unrestricted'
        self.receipt.write_text(json.dumps(receipt))
        result, _ = self.observation(self.checksum())
        self.assertNotEqual(result.returncode, 0)


class FreshLegacyBootstrapTest(FreshBootstrapTest):
    legacy_carriers = True
    expected_ticket = 'ticket-008'

    def test_historical_carriers_are_preserved_without_activity_claim(self):
        before = {p.name: p.read_bytes() for p in (self.target / 'project/ticket-007').iterdir()}
        self.test_first_real_allocator_preserves_foreign_bytes_and_does_not_write_source()
        after = {p.name: p.read_bytes() for p in (self.target / 'project/ticket-007').iterdir()}
        self.assertEqual(before, after)
        self.assertIn(b'IN_PROGRESS', after['README.md'])

    def test_modified_historical_carrier_is_refused(self):
        (self.target / 'project/ticket-007/README.md').write_text('unfinished changes\n')
        result, _ = self.observation(self.checksum())
        self.assertNotEqual(result.returncode, 0)

    def test_missing_historical_carrier_is_refused(self):
        (self.target / 'project/ticket-007/intent.json').unlink()
        result, _ = self.observation(self.checksum())
        self.assertNotEqual(result.returncode, 0)

    def test_untracked_carrier_is_refused(self):
        (self.target / 'project/ticket-007/extra.md').write_text('unknown owner\n')
        result, _ = self.observation(self.checksum())
        self.assertNotEqual(result.returncode, 0)

    def test_symlinked_carrier_is_refused(self):
        p = self.target / 'project/ticket-007/README.md'
        p.unlink()
        p.symlink_to(self.target / 'foreign.txt')
        result, _ = self.observation(self.checksum())
        self.assertNotEqual(result.returncode, 0)

    def test_live_ticket_branch_is_refused(self):
        self.command(self.target, 'git', 'branch', 'ticket/008-other-writer')
        result, _ = self.observation(self.checksum())
        self.assertNotEqual(result.returncode, 0)

    def test_prior_allocation_reservation_is_refused(self):
        (self.target / '.git/new-project-ticket-high-water').write_text('8\n')
        result, _ = self.observation(self.checksum())
        self.assertNotEqual(result.returncode, 0)


if __name__ == '__main__':
    unittest.main()
