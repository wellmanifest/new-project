#!/usr/bin/env python3
"""Classification validation must precede every allocator identity effect."""
import importlib.util
import json
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    'classification_allocator_fixture', ROOT / 'tests/ticket-allocation-worktree.test.py')
fixture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixture)


class ClassificationAllocationTest(unittest.TestCase):
    def allocator(self):
        case = fixture.TicketAllocationWorktreeTest(
            'test_file_ticket_is_created_only_in_canonical_linked_worktree')
        case.setUp()
        self.addCleanup(case.doCleanups)
        return case

    def state(self, case):
        root = case.root
        paths = [root / '.git/new-project-ticket-high-water']
        for directory in ['project', '.subactor/leases', '.git/worktrees']:
            paths.extend(sorted((root / directory).rglob('*')))
        return {
            'refs': case.git('for-each-ref', '--format=%(refname) %(objectname)').stdout,
            'worktrees': case.git('worktree', 'list', '--porcelain').stdout,
            'status': case.git('status', '--porcelain').stdout,
            'files': {str(p.relative_to(root)): p.read_bytes()
                      for p in paths if p.is_file()},
        }

    def test_invalid_classifications_leave_allocator_identity_state_unchanged(self):
        for dimension, valid in [('kind', 'SERVICE'), ('priority', 'P2'), ('origin', 'health')]:
            for value in ['INVALID', valid + '\nINVALID', '\n' + valid,
                          valid + '\n', valid + '\r', valid + '\t', valid + '\x01']:
                with self.subTest(dimension=dimension, value=value):
                    case = self.allocator()
                    before = self.state(case)
                    result = case.allocate('--' + dimension, value)
                    self.assertNotEqual(result.returncode, 0, result.stdout)
                    self.assertIn('GOV-CLASS-001', result.stderr)
                    self.assertEqual(self.state(case), before)

    def test_every_declared_scalar_is_accepted_by_the_actual_validator(self):
        source = (ROOT / 'project/new-ticket.sh').read_text()
        start = source.index('classification_dsl() {')
        end = source.index('\nrequire_classification_value kind', start)
        helper = source[start:end]
        contract = json.loads((ROOT / 'governance/work-classification.dsl.json').read_text())
        for dimension, values in contract['dimensions'].items():
            for value in values:
                with self.subTest(dimension=dimension, value=value):
                    result = subprocess.run(
                        ['bash', '-c', helper + '\nrequire_classification_value "$1" "$2"',
                         'classification-validator', dimension, value],
                        cwd=ROOT, capture_output=True, text=True)
                    self.assertEqual(result.returncode, 0, result.stderr)

    def test_template_and_fallback_preserve_unicode_title_and_valid_classification(self):
        title = 'Zażółć "gęślą" \\ ścieżka'
        for template in [True, False]:
            with self.subTest(template=template):
                case = self.allocator()
                if not template:
                    (case.root / 'template/files/intent.template.json').unlink()
                    case.git('add', '.')
                    case.git('commit', '-m', 'Use supported fallback renderer')
                result = case.allocate('--title', title, '--kind', 'BUG',
                                       '--priority', 'P1', '--origin', 'health')
                self.assertEqual(result.returncode, 0, result.stderr)
                record = next(json.loads(line) for line in result.stdout.splitlines()
                              if line.startswith('{'))
                path = Path(record['worktreePath']) / 'project/ticket-001/intent.json'
                intent = json.loads(path.read_text())
                self.assertEqual(intent['summary'], title)
                self.assertEqual(intent['classification'],
                                 {'kind': 'BUG', 'priority': 'P1', 'origin': 'health'})
                self.assertEqual(intent['workstream'], 'application')
                self.assertEqual(intent['ticket'], 'ticket-001')
                self.assertIn('project/ticket-001/**', intent['allowedPaths'])


if __name__ == '__main__':
    unittest.main()
