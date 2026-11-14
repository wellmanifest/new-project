#!/usr/bin/env python3
"""Receipt-only recovery over real Git fixtures; no production grant is mocked."""
from contextlib import redirect_stdout
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

import scaffold_bootstrap_test as fixtures


class RefreshTest(unittest.TestCase):
    fresh = False
    untracked_scaffold = True
    legacy_carriers = False
    expected_ticket = 'ticket-001'
    command = fixtures.BootstrapTest.command
    observation = fixtures.BootstrapTest.observation
    checksum = fixtures.BootstrapTest.checksum

    def setUp(self):
        with redirect_stdout(io.StringIO()):
            fixtures.BootstrapTest.setUp(self)
        sys.path.insert(0, str(self.source / 'scripts'))
        self.addCleanup(lambda: sys.path.remove(str(self.source / 'scripts')))
        self.original = self.receipt.read_bytes()
        self.old_revision = json.loads(self.original)['sourceRevision']
        # A second immutable fixture publication changes real managed bytes and
        # the standard-owned manifest version, leaving target seeds unchanged.
        (self.source / 'VERSION').write_text('0.20.999\n')
        p = self.source / 'governance/manifest.default.json'
        manifest = json.loads(p.read_text())
        manifest['standard']['version'] = '0.20.999'
        p.write_text(json.dumps(manifest, indent=2) + '\n')
        with (self.source / 'scripts/work_start_check.py').open('a') as stream:
            stream.write('\n# Fixture published managed revision.\n')
        self.command(self.source, 'git', 'add', 'VERSION', 'governance/manifest.default.json',
                     'scripts/work_start_check.py')
        self.command(self.source, 'git', 'commit', '--quiet', '-m', 'Fixture second publication')
        self.revision = self.command(self.source, 'git', 'rev-parse', 'HEAD').stdout.strip()
        self.adopt('--upgrade')
        self.assertEqual(self.receipt.read_bytes(), self.original, 'ordinary upgrade stays explicit')

    def adopt(self, *options):
        with patch.object(self.adopter, 'verify_publication_evidence'), redirect_stdout(io.StringIO()):
            return self.adopter.main(['--target-root', str(self.target), '--source-revision',
                                     self.revision, *options])

    def refresh(self, *options):
        return self.adopt('--refresh-bootstrap-receipt', *(options or ('--upgrade',)))

    def snapshot(self):
        return {p.relative_to(self.target).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in self.target.rglob('*') if p.is_file() and not p.is_symlink()
                and '.git' not in p.relative_to(self.target).parts}

    def refuse(self):
        before = self.snapshot()
        with self.assertRaises((SystemExit, ValueError, OSError, subprocess.SubprocessError)):
            self.refresh()
        self.assertEqual(self.snapshot(), before)

    def change_receipt(self, change):
        receipt = json.loads(self.receipt.read_bytes())
        change(receipt)
        self.receipt.write_text(json.dumps(receipt))

    def test_check_is_read_only_and_refresh_changes_only_receipt_then_allocates(self):
        (self.target / 'foreign.txt').write_text('another writer\n')
        before = self.snapshot()
        self.assertEqual(self.refresh('--check'), 1)
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(self.refresh(), 0)
        after = self.snapshot()
        self.assertEqual({name for name in before if before[name] != after[name]},
                         {'.subactor/receipts/bootstrap-adoption.json'})
        receipt = json.loads(self.receipt.read_bytes())
        self.assertEqual(receipt['sourceRevision'], self.revision)
        self.assertFalse(receipt['grantsWriterAuthority'])
        self.assertFalse(receipt['grantsPublicationAuthority'])
        checksum = self.checksum()
        result, report = self.observation(checksum)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(report['route'], 'NEW_TICKET_CANDIDATE')
        self.assertFalse(report['grantsAuthority'])
        result = self.command(self.target, 'bash', './project/new-ticket.sh', '--title',
            'Adopt governance', '--agent', 'fixture', '--workstream', 'governance',
            '--path', '.governance/**', '--worktree-slug', 'receipt-refresh',
            '--bootstrap-adoption-digest', checksum)
        self.assertIn('Successfully allocated ticket-001', result.stdout)
        self.assertEqual((self.target / 'foreign.txt').read_text(), 'another writer\n')
        self.assertEqual(self.command(self.target, 'git', 'rev-parse', 'HEAD').stdout.strip(), self.head)
        allocated_manifest = self.target / '.worktrees/ticket-001--receipt-refresh/.governance/manifest.json'
        if self.fresh or self.untracked_scaffold:
            self.assertFalse(allocated_manifest.exists())
        else:
            self.assertEqual(json.loads(allocated_manifest.read_bytes()), {
                'schema': 'wellmanifest.manifest/v1',
                'standard': {'id': 'profile:baseline', 'version': '0.20.37'}})
        self.refuse()  # A receipt cannot acknowledge a second allocation.

    def test_repeat_is_idempotent(self):
        self.assertEqual(self.refresh(), 0)
        before = self.snapshot()
        self.assertEqual(self.refresh(), 0)
        self.assertEqual(self.refresh('--check'), 0)
        self.assertEqual(self.snapshot(), before)

    def test_wrong_base(self):
        tree = self.command(self.target, 'git', 'rev-parse', 'HEAD^{tree}').stdout.strip()
        moved = self.command(self.target, 'git', 'commit-tree', tree, '-p', self.head,
                             '-m', 'Fixture external HEAD movement').stdout.strip()
        self.command(self.target, 'git', 'update-ref', 'refs/heads/main', moved, self.head)
        self.refuse()

    def test_wrong_clone(self):
        self.change_receipt(lambda r: r.update(commonGitDir='/another/clone/.git'))
        self.refuse()

    def test_existing_reservation(self):
        (self.target / '.git/new-project-ticket-high-water').write_text('1\n')
        self.refuse()

    def test_ambiguous_ticket_ref(self):
        self.command(self.target, 'git', 'branch', 'ticket/001-pending')
        self.refuse()

    def test_extra_worktree(self):
        self.command(self.target, 'git', 'worktree', 'add', '--quiet', '--detach', str(self.base / 'other'))
        self.refuse()

    def test_changed_seed(self):
        (self.target / 'TODO.md').write_text('# Foreign modification\n')
        self.refuse()

    def test_changed_ignore_rules(self):
        with (self.target / '.gitignore').open('a') as stream:
            stream.write('foreign-rule\n')
        self.refuse()

    def test_changed_manifest_extension(self):
        p = self.target / '.governance/manifest.json'
        manifest = json.loads(p.read_bytes())
        manifest['foreignExtension'] = 'not acknowledged by installer'
        p.write_bytes(self.adopter.json_bytes(manifest))
        self.refuse()

    def test_changed_managed_payload(self):
        with (self.target / '.governance/work_start_check.py').open('a') as stream:
            stream.write('\n# Foreign modification.\n')
        self.refuse()

    def test_unpublished_installed_lock(self):
        p = self.target / '.governance/manifest.lock.json'
        lock = json.loads(p.read_bytes())
        lock['standard']['publicationStatus'] = 'unpublished-test'
        p.write_text(json.dumps(lock))
        self.refuse()

    def test_missing_original_managed_closure(self):
        self.change_receipt(lambda r: r['files'].pop('.governance/work_start_check.py'))
        self.refuse()

    def test_forged_original_managed_hash(self):
        self.change_receipt(lambda r: r['files'].update({'.governance/work_start_check.py': 'f' * 64}))
        self.refuse()

    def test_receipt_cannot_admit_foreign_path(self):
        self.change_receipt(lambda r: r['files'].update({'foreign.txt': hashlib.sha256(b'original\n').hexdigest()}))
        self.refuse()

    def test_receipt_cannot_grant_authority(self):
        self.change_receipt(lambda r: r.update(grantsWriterAuthority=True))
        self.refuse()

    def test_duplicate_receipt_key(self):
        raw = self.receipt.read_text()
        self.receipt.write_text('{"sourceRevision":"' + self.old_revision + '",' + raw[1:])
        self.refuse()

    @unittest.skipIf(os.name == 'nt', 'POSIX bootstrap file-operation boundary')
    def test_symlinked_payload(self):
        p = self.target / '.governance/work_start_check.py'
        external = self.base / 'foreign.py'
        external.write_bytes(p.read_bytes())
        p.unlink()
        p.symlink_to(external)
        self.refuse()

    def test_observation_change_before_write(self):
        original = self.adopter.bootstrap_refresh_observation
        count = 0
        def observe(*args):
            nonlocal count
            count += 1
            if count == 2:
                (self.target / 'foreign.txt').write_text('concurrent writer\n')
            return original(*args)
        with patch.object(self.adopter, 'bootstrap_refresh_observation', side_effect=observe):
            with self.assertRaisesRegex(SystemExit, 'state changed'):
                self.refresh()
        self.assertEqual(self.receipt.read_bytes(), self.original)
        self.assertEqual((self.target / 'foreign.txt').read_text(), 'concurrent writer\n')

    def test_failed_atomic_replace_preserves_receipt(self):
        before = self.snapshot()
        with patch.object(self.adopter.os, 'replace', side_effect=OSError('fixture interruption')):
            with self.assertRaises(OSError):
                self.refresh()
        self.assertEqual(self.snapshot(), before)
        self.assertFalse(list(self.receipt.parent.glob('.bootstrap-refresh-*')))

    def test_testing_publication_bypass_is_forbidden(self):
        with self.assertRaises(SystemExit):
            self.adopt('--refresh-bootstrap-receipt', '--upgrade', '--allow-unpublished-for-testing')
        self.assertEqual(self.receipt.read_bytes(), self.original)


if __name__ == '__main__':
    unittest.main()
