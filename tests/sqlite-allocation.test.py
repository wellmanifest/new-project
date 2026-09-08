#!/usr/bin/env python3
"""Interop with the reviewed Registry writer, actual allocation and Git hooks."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
SOURCE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SOURCE / 'scripts'))
import ticket_input
import ticket_storage
import work_continuity
import worktree_overlap_check

spec = importlib.util.spec_from_file_location('input_fixture', SOURCE / 'tests/ticket-input.test.py')
fixture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixture)
REVISION = '408e90bb0a0554499fa4560cff9e2e0e83c2cd8d'
HASHES = {
    'storage-common.mjs': 'd27b0ef0e2423da206a5198932302cce149bde298a3531b920a32c5393a3c8a7',
    'ticket-store-cli.mjs': 'cd9a6aa665958689e975537e04eb4e274f0c760cec173330e54eb353eeca93f9',
    'ticket-store.mjs': '5d14b64b7abd40a5a38ee9cce8ad1eb5572ee37b5c512e792344cc2d714f81cd',
}
PIN = hashlib.sha256(json.dumps(HASHES, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


class AllocationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = os.environ.get('TEST_REGISTRY_TICKET_RUNTIME')
        if not source:
            raise unittest.SkipTest('Real Registry interop requires explicit TEST_REGISTRY_TICKET_RUNTIME; private source is never fetched implicitly')
        fixture.TicketInputTests.setUpClass.__func__(cls)
        cls.runtime = cls.seed.parent / (cls.seed.name + '-registry')
        cls.runtime.mkdir()
        for name, pin in HASHES.items():
            data = (Path(source) / name).read_bytes()
            if hashlib.sha256(data).hexdigest() != pin:
                raise AssertionError('Independent Registry source pin mismatch: ' + name)
            (cls.runtime / name).write_bytes(data)
        shutil.copy2(SOURCE / 'scripts/ticket_storage.py', cls.seed / 'scripts/ticket_storage.py')

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.runtime)
        cls.seed_temp.cleanup()

    git = fixture.TicketInputTests.git
    run_gate = fixture.TicketInputTests.run_gate

    def setUp(self):
        # Reuse the full standard fixture and valid bounded delivery intent, but
        # replace its synthetic database with the actual published writer.
        fixture.TicketInputTests.setUp(self)
        self.database.unlink()
        self.git('config', 'core.hooksPath', '.git/no-hooks')
        self.git('checkout', '-q', 'main')
        self.git('branch', '-D', 'ticket/001-database')
        self.git('config', 'new-project.ticketStorage', 'sqlite')
        self.git('config', 'new-project.ticketStoreRoot', str(self.runtime))
        self.git('config', 'new-project.ticketStoreSha256', PIN)

    connection = fixture.TicketInputTests.connection
    save = fixture.TicketInputTests.save

    def allocate(self, root=None, *args):
        root = root or self.root
        return subprocess.run(['bash', str(root / 'project/new-ticket.sh'), '--workstream', 'governance',
            '--title', 'Actual SQLite allocation', *args], cwd=root, text=True, capture_output=True)

    def update(self, filename, data, revision):
        return ticket_storage.invoke(self.runtime, PIN, 'update', '--repository', str(self.root),
            '--ticket', 'ticket-001', '--file', filename, '--expected-revision', str(revision), content=data)

    def create_ready_ticket(self):
        result = self.allocate()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.update('intent.json', json.dumps(self.intent), 1)
        self.git('checkout', '-qb', 'ticket/001-database')
        self.git('config', 'core.hooksPath', '.githooks')

    def test_allocate_commit_and_full_gate_without_ticket_carriers(self):
        before = self.git('status', '--porcelain')
        index = (self.root / '.git/index').read_bytes()
        self.create_ready_ticket()
        self.assertEqual(self.git('status', '--porcelain'), before)
        self.assertEqual((self.root / '.git/index').read_bytes(), index)
        self.assertFalse((self.root / 'project/ticket-001').exists())
        (self.root / 'src').mkdir(exist_ok=True)
        (self.root / 'src/feature.txt').write_text('Material implementation\n')
        self.git('add', 'src/feature.txt')
        self.git('commit', '-qm', 'Implement source with SQLite intent')
        self.head = self.git('rev-parse', 'HEAD').strip()
        code, report = self.run_gate()
        self.assertEqual(code, 0, report)
        self.assertEqual(self.git('diff', '--name-only', self.base, self.head).strip(), 'src/feature.txt')
        self.assertEqual(self.git('status', '--porcelain'), '')
        self.assertEqual(self.run_gate('--actor', 'ci')[0], 1)
        scopes, errors = worktree_overlap_check.ticket_scopes(self.root)
        self.assertEqual(errors, ())
        self.assertEqual(scopes[0].allowed_paths, ('src/**',))
        intent, _, _, target = work_continuity.intent_state(self.root, 'ticket-001')
        self.assertEqual(intent['allowedPaths'], ['src/**'])
        self.assertEqual(target, 'main')

    def test_inactive_database_ticket_rejects_source_commit(self):
        self.create_ready_ticket()
        (self.root / 'src').mkdir(exist_ok=True)
        (self.root / 'src/feature.txt').write_text('Material implementation\n')
        self.git('add', 'src/feature.txt')
        for revision, state in enumerate(('BLOCKED', 'DONE'), start=2):
            self.update('README.md', f'# Ticket\n\n- **Status**: {state}\n', revision)
            result = subprocess.run(['git', 'commit', '-qm', 'must reject'], cwd=self.root, text=True, capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('GOV-AGENT-HOST-003', result.stderr)
        # A staged legacy README cannot replace the selected database state,
        # including the former governance-only transition exception.
        legacy = self.root / 'project/ticket-001/README.md'
        legacy.parent.mkdir(parents=True)
        legacy.write_text('# Forged fallback\n\n- **Status**: IN_PROGRESS\n')
        self.git('reset', '-q', 'HEAD', 'src/feature.txt')
        self.git('add', 'project/ticket-001/README.md')
        self.update('README.md', '# Ticket\n\n- **Status**: BLOCKED\n', 4)
        for hook in ('.githooks/pre-commit', 'template/files/pre-commit.template.sh'):
            result = subprocess.run(['bash', str(self.root / hook)], cwd=self.root, text=True, capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('GOV-AGENT-HOST-003', result.stderr)
        self.assertEqual(self.git('rev-parse', 'HEAD').strip(), self.base)

    def test_runtime_tampering_and_missing_pin_fail_before_reservation(self):
        copied = Path(self.temp.name) / 'tampered'
        shutil.copytree(self.runtime, copied)
        with (copied / 'storage-common.mjs').open('a') as stream:
            stream.write('\n// changed dependency\n')
        self.git('config', 'new-project.ticketStoreRoot', str(copied))
        self.assertNotEqual(self.allocate().returncode, 0)
        self.assertFalse(self.database.exists())
        self.assertFalse((self.root / '.git/new-project-ticket-high-water').exists())
        self.git('config', '--unset', 'new-project.ticketStoreSha256')
        self.assertNotEqual(self.allocate().returncode, 0)
        self.assertFalse(self.database.exists())

    def test_linked_worktree_and_legacy_allocator_share_reserved_ids(self):
        self.create_ready_ticket()
        self.assertEqual(self.allocate().returncode, 3, 'active branch must reuse its ticket')
        linked = Path(self.temp.name) / 'linked'
        self.git('worktree', 'add', '--relative-paths', '-qb', 'preparation', str(linked), self.base)
        # New helper is staged in the fixture seed, so the linked tree gets the
        # same managed release, while Git configuration and DB stay clone-wide.
        result = self.allocate(linked)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(ticket_input.configured_records(linked)), 2)
        self.assertFalse((linked / 'project.sqlite').exists())
        self.assertFalse((linked / 'project/ticket-002').exists())
        # Even if the compatibility cache is lost, a file-mode allocator sees
        # IDs reserved only in SQLite and cannot reuse one.
        (self.root / '.git/new-project-ticket-high-water').unlink()
        result = self.allocate(linked, '--storage', 'files')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((linked / 'project/ticket-003/intent.json').exists())


class RuntimeBoundaryTests(unittest.TestCase):
    def test_independent_pin_is_required_before_execution(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ticket_storage.RUNTIME_FILES:
                (root / name).write_text('throw new Error("must never execute");\n')
            pin = ticket_storage.runtime_digest(root)
            ticket_storage.verify_runtime(root, pin)
            for missing in (None, '', '0' * 64):
                with self.assertRaises(ValueError):
                    ticket_storage.invoke(root, missing, 'init')
            (root / 'storage-common.mjs').write_text('changed dependency')
            with self.assertRaises(ValueError):
                ticket_storage.invoke(root, pin, 'init')

    def test_unknown_local_mode_is_not_a_legacy_fallback(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(['git', 'init', '-q', str(root)], check=True)
            subprocess.run(['git', '-C', str(root), 'config', 'new-project.ticketStorage', 'unknown'], check=True)
            with self.assertRaises(ticket_input.TicketInputError):
                ticket_input.configured_records(root)


if __name__ == '__main__':
    unittest.main()
