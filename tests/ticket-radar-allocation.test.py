"""Ticket creation must assess its declared scope without promoting advice."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import ticket_storage as storage

spec = importlib.util.spec_from_file_location('radar_allocation_fixture', ROOT / 'tests/ticket-allocation-worktree.test.py')
fixture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixture)
sqlite_spec = importlib.util.spec_from_file_location('radar_sqlite_fixture', ROOT / 'tests/sqlite-allocation.test.py')
sqlite_fixture = importlib.util.module_from_spec(sqlite_spec)
sqlite_spec.loader.exec_module(sqlite_fixture)


def bundle(ticket='ticket-001'):
    record = {'schema': 'subactor.ticket-radar/v1', 'ticket_ref': ticket,
              'assessment_mode': 'predicted', 'authority': 'ADVISORY', 'score': 42,
              'complexity': 'M', 'estimate': {'minutes': 45, 'budget_minutes': 30},
              'split': {'recommended': True}, 'diagnostics': ['RADAR-ACCEPTANCE-MISSING']}
    return {'schema': 'subactor.ticket-radar-bundle/v1', 'jsonl': json.dumps(record) + '\n'}


class RadarProjectionTest(unittest.TestCase):
    def setUp(self):
        self.intent = {'ticket': 'ticket-001', 'summary': 'Change src/worker.py',
                       'allowedPaths': ['project/ticket-001/**', 'src/worker.py']}
        self.result = SimpleNamespace(returncode=0, stdout=json.dumps(bundle()))

    def test_projection_uses_declared_scope_and_preserves_intent_and_readme(self):
        before = json.dumps(self.intent)
        with patch.object(storage.subprocess, 'run', return_value=self.result) as run:
            text = storage.radar_readme('# Original\n\n- **Status**: IN_PROGRESS\n', self.intent, ROOT)
        self.assertTrue(text.startswith('# Original\n\n- **Status**: IN_PROGRESS\n'))
        self.assertIn('| Impact score | 42/100 |', text)
        self.assertIn('| Split recommended | yes |', text)
        self.assertIn('advisory only, not execution or merge approval', text)
        self.assertIn('RADAR-ACCEPTANCE-MISSING', text)
        args, kwargs = run.call_args
        self.assertEqual(args[0], ['ticket-radar', '--repository-root', str(ROOT)])
        self.assertEqual(json.loads(kwargs['input'])['ticket']['files'], self.intent['allowedPaths'])
        self.assertNotIn('shell', kwargs)
        self.assertEqual(json.dumps(self.intent), before)

    def test_unavailable_runtime_does_not_echo_private_errors_or_fabricate_score(self):
        for error in (FileNotFoundError('/private/credential'),
                      subprocess.TimeoutExpired('private-command', 10)):
            with self.subTest(error=error), patch.object(storage.subprocess, 'run', side_effect=error):
                text = storage.radar_readme('# Ticket\n', self.intent, ROOT)
                self.assertIn('Assessment unavailable:', text)
                self.assertNotIn('private', text)
                self.assertNotIn('/100', text)

    def test_refresh_replaces_only_the_generated_block(self):
        with patch.object(storage.subprocess, 'run', return_value=self.result):
            first = storage.radar_readme('# User content\n', self.intent, ROOT)
            refreshed = storage.radar_readme(first + '\nKeep this note.\n', self.intent, ROOT)
        self.assertEqual(refreshed.count('## Ticket Radar'), 1)
        self.assertIn('# User content', refreshed)
        self.assertIn('Keep this note.', refreshed)

    def test_wrong_ticket_observed_diff_and_injected_markdown_are_not_accepted(self):
        records = []
        for name, value in [('ticket_ref', 'ticket-999'), ('authority', 'APPROVED'),
                            ('assessment_mode', 'observed-pr'), ('score', True),
                            ('complexity', 'M | forged'), ('diagnostics', ['<script>'])]:
            b = bundle(); r = json.loads(b['jsonl']); r[name] = value
            b['jsonl'] = json.dumps(r); records.append(json.dumps(b))
        records += ['not json', '[]', 'null', 'true', json.dumps({'schema': 'unexpected'})]
        for raw in records:
            with self.subTest(raw=raw), patch.object(storage.subprocess, 'run', return_value=SimpleNamespace(returncode=0, stdout=raw)):
                text = storage.radar_readme('# Ticket\n', self.intent, ROOT)
                self.assertIn('Assessment unavailable:', text)
                self.assertNotIn('/100', text)

    def test_sqlite_writer_receives_the_same_projection_without_extra_files(self):
        args = SimpleNamespace(ticket='ticket-001', title='Change worker', root=ROOT,
            workstream='application', path=['src/worker.py'], kind='SERVICE', priority='P2',
            origin='health', runtime_root='fixture', runtime_sha256='a'*64, allocation_key='fixture')
        with patch.object(storage, 'scoped_paths', return_value=['src/worker.py']), \
             patch.object(storage, 'invoke', return_value={}) as invoke, \
             patch.object(storage.subprocess, 'run', return_value=self.result):
            storage.create(args)
        content = json.loads(invoke.call_args.kwargs['content'])
        self.assertEqual(set(content), {'README.md', 'intent.json'})
        self.assertIn('## Ticket Radar', content['README.md'])
        self.assertIn('42/100', content['README.md'])
        self.assertNotIn('radar', json.loads(content['intent.json']))


class RadarFileAllocationTest(fixture.TicketAllocationWorktreeTest):
    def test_allocator_invokes_radar_after_material_scope_is_known(self):
        executable = Path(self.temp.name) / 'bin' / 'ticket-radar'
        executable.parent.mkdir()
        capture = Path(self.temp.name) / 'captured.json'
        executable.write_text('#!' + sys.executable + '\nimport json,sys\nfrom pathlib import Path\n'
            + f'Path({str(capture)!r}).write_text(sys.stdin.read())\n'
            + f'print({json.dumps(bundle())!r})\n')
        executable.chmod(0o755)
        with patch.dict(os.environ, {'PATH': str(executable.parent) + os.pathsep + os.environ['PATH']}):
            result = self.allocate('--path', 'src/worker.py')
        self.assertEqual(result.returncode, 0, result.stderr)
        readme = self.root / '.worktrees/ticket-001--canonical-ticket/project/ticket-001/README.md'
        self.assertIn('| Estimated effort | 45 min |', readme.read_text())
        self.assertIn('src/worker.py', json.loads(capture.read_text())['ticket']['files'])
        lease = json.loads((self.root / '.subactor/leases/ticket-001--canonical-ticket.json').read_text())
        self.assertEqual(lease['phase'], 'claimed')
        self.assertIn('"executionAuthorized": false', result.stdout)


class RadarSQLiteAllocationTest(unittest.TestCase):
    setUpClass = classmethod(sqlite_fixture.AllocationTests.setUpClass.__func__)
    tearDownClass = classmethod(sqlite_fixture.AllocationTests.tearDownClass.__func__)
    setUp = sqlite_fixture.AllocationTests.setUp
    git = sqlite_fixture.AllocationTests.git
    connection = sqlite_fixture.AllocationTests.connection
    save = sqlite_fixture.AllocationTests.save
    allocate = sqlite_fixture.AllocationTests.allocate

    def test_real_sqlite_allocation_stores_the_assessment_in_its_readme(self):
        executable = Path(self.temp.name) / 'bin' / 'ticket-radar'
        executable.parent.mkdir()
        executable.write_text('#!' + sys.executable + '\n' + f'print({json.dumps(bundle())!r})\n')
        executable.chmod(0o755)
        with patch.dict(os.environ, {'PATH': str(executable.parent) + os.pathsep + os.environ['PATH']}):
            result = self.allocate(None, '--agent', 'codex', '--writer-actor', 'agent:codex',
                                   '--writer-session', 'radar-fixture', '--path', 'project/new-ticket.sh')
        self.assertEqual(result.returncode, 0, result.stderr)
        readme = storage.read_file(self.root, 'ticket-001', 'README.md').decode()
        self.assertIn('| Impact score | 42/100 |', readme)
        self.assertIn('advisory only, not execution or merge approval', readme)
        self.assertFalse((self.root / 'project/ticket-001').exists())


if __name__ == '__main__':
    unittest.main()
