#!/usr/bin/env python3
"""Gate/activity agreement for unambiguous historical metadata, never authority."""
from pathlib import Path
from contextlib import redirect_stderr
import io
from types import SimpleNamespace
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import ticket_activity
import governance_check
import ticket_storage


class TicketStateCompatibilityTest(unittest.TestCase):
    def check(self, text, expected, conflict=False):
        self.assertEqual(governance_check.parse_ticket_state_text(text), expected)
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)
            (path / 'README.md').write_text(text)
            if conflict:
                with self.assertRaises(ticket_activity.ActivityError):
                    ticket_activity.projection_status(path)
            else:
                self.assertEqual(ticket_activity.projection_status(path), expected[0])

    def test_canonical_and_legacy_metadata_agree(self):
        cases = [
            ('- **Status**: IN_PROGRESS\n- **Workflow state**: EDIT\n', ('IN_PROGRESS', 'EDIT')),
            ('Status: IN_PROGRESS / EDIT.\n', ('IN_PROGRESS', 'EDIT')),
            ('Status: IN_PROGRESS / PUBLICATION.\n', ('IN_PROGRESS', 'PUBLICATION')),
            ('Status: BLOCKED\n', ('BLOCKED', None)),
            ('Status: in_progress / validation\n', ('IN_PROGRESS', 'VALIDATION')),
            ('Status: IN_PROGRESS / EDIT.\r\n', ('IN_PROGRESS', 'EDIT')),
            ('- **Status**: IN_PROGRESS\nStatus: IN_PROGRESS / EDIT.\n- **Workflow state**: EDIT\n', ('IN_PROGRESS', 'EDIT')),
        ]
        for text, expected in cases:
            with self.subTest(text=text):
                self.check(text, expected)

    def test_conflicting_and_narrative_headers_do_not_create_status(self):
        conflicts = [
            'Status: IN_PROGRESS\nStatus: DONE\n',
            '- **Status**: IN_PROGRESS\nStatus: DONE\n',
            'Status: IN_PROGRESS / EDIT.\n- **Workflow state**: PUBLICATION\n',
        ]
        for text in conflicts:
            with self.subTest(text=text):
                self.check(text, (None, None), conflict=True)
        cases = [
            'The previous Status: DONE is historical.\n',
            'History\u2028Status: DONE\n',
            'Status: IN_PROGRESS / EDIT. Continue later.\n',
            '```text\nStatus: DONE\n```\n',
            '~~~text\n- **Status**: DONE\n~~~\n',
        ]
        for text in cases:
            with self.subTest(text=text):
                self.check(text, (None, None))

    def test_fenced_examples_do_not_override_real_metadata(self):
        self.check('- **Status**: IN_PROGRESS\n- **Workflow state**: EDIT\n\n```text\nStatus: DONE\n```\n', ('IN_PROGRESS', 'EDIT'))

    def test_sqlite_active_bridge_forwards_legacy_status_without_inventing_authority(self):
        # The bridge reads pinned SQLite documents, not filesystem ticket files.
        # Storage integrity and receipt authority have their own real fixtures.
        arguments = ['ticket_storage.py', 'active', '--root', '/fixture',
                     '--ticket', 'ticket-004', '--active-status', 'IN_PROGRESS']
        with patch.object(sys, 'argv', arguments), \
                patch.dict(sys.modules, {'ticket_activity': ticket_activity}), \
                patch.object(ticket_storage, 'read_file', return_value=b'Status: IN_PROGRESS / EDIT.\n'), \
                patch.object(ticket_activity, 'resolve', return_value=SimpleNamespace(active=True)) as resolved:
            with self.assertRaises(SystemExit) as result:
                ticket_storage.main()
            self.assertEqual(result.exception.code, 0)
            self.assertEqual(resolved.call_args.kwargs['status_override'], 'IN_PROGRESS')
        with patch.object(sys, 'argv', arguments), \
                patch.dict(sys.modules, {'ticket_activity': ticket_activity}), \
                patch.object(ticket_storage, 'read_file', return_value=b'Status: IN_PROGRESS\nStatus: DONE\n'), \
                patch.object(ticket_activity, 'resolve') as resolved, redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as result:
                ticket_storage.main()
            self.assertEqual(result.exception.code, 2)
            resolved.assert_not_called()


if __name__ == '__main__':
    unittest.main()
