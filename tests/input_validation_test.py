#!/usr/bin/env python3
"""Regressions for malformed contracts and the installed guard command."""
import copy
import importlib.util
import json
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / f'{name}.py')
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


class InputBoundaryTests(unittest.TestCase):
    def test_valid_catalog_and_duplicate_ownership(self):
        checker = module('standard_pack_check')
        catalog = json.loads((ROOT / 'governance/standard-packs.json').read_text())
        self.assertEqual(checker.catalog_findings(catalog), [])
        catalog['packs'][0]['owns'] *= 2
        self.assertIn('STD-PACK-DUPLICATE-OWNER',
                      {f['code'] for f in checker.catalog_findings(catalog)})

    def test_malformed_catalog_members_return_findings(self):
        checker = module('standard_pack_check')
        original = json.loads((ROOT / 'governance/standard-packs.json').read_text())
        cases = []
        for value in [[], {}, None, 0]:
            cases.append(('owns', [value]))
        for field in ['extends', 'requirements']:
            for value in [None, {}, 'not-an-array']:
                cases.append((field, value))
        for value in [None, 0, 'not-an-object', {'id': [], 'minimumLevel': []}]:
            cases.append(('requirements', [value]))
        for value in [[], {}]:
            cases.append(('extends', [value]))
        for value in [None, [], ['invalid']]:
            cases.append(('aliases', value))
        cases.append(('aliases', {'legacy': []}))
        for field, value in cases:
            with self.subTest(field=field, value=value):
                catalog = copy.deepcopy(original)
                if field == 'owns':
                    catalog['packs'][0][field] = value
                elif field == 'aliases':
                    catalog[field] = value
                else:
                    catalog['profiles']['baseline'][field] = value
                findings = checker.catalog_findings(catalog)
                self.assertTrue(findings)
                self.assertTrue(all(f['diagnostic'] == 'GOV-STANDARD-PACK-001'
                                    for f in findings))

    def test_cli_malformed_catalog_has_structured_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            catalog = json.loads((ROOT / 'governance/standard-packs.json').read_text())
            catalog['packs'][0]['owns'] = [[]]
            (root / 'catalog.json').write_text(json.dumps(catalog))
            (root / 'adoption.json').write_text(json.dumps({'mode': 'audit'}))
            result = subprocess.run(
                [sys.executable, str(ROOT / 'scripts/standard_pack_check.py'),
                 '--root', str(root), '--catalog', 'catalog.json',
                 '--adoption', 'adoption.json', '--format', 'json'],
                capture_output=True, text=True, timeout=15)
            self.assertEqual(result.returncode, 2, result.stderr)
            report = json.loads(result.stdout)
            self.assertFalse(report['ok'])
            self.assertEqual(report['findings'][0]['code'], 'STD-PACK-CATALOG')

    def test_checkpoint_sequence_is_a_positive_integer(self):
        checker = module('work_continuity')
        stamp = '2026-10-02T21:00:00Z'
        index = {'schema': checker.INDEX_SCHEMA,
                 'repositoryRef': 'repository:example/input-boundary',
                 'maxEntries': 128, 'updatedAt': stamp,
                 'entries': [{'ticket': 'ticket-001', 'sessionId': 'test-001',
                              'eventRef': 'receipt:input/event',
                              'checkpointRef': 'receipt:input/checkpoint',
                              'checkpointSequence': 1, 'recordedAt': stamp}]}
        checker.validate_index(index)
        for value in [True, False, 0, -1, '1', 1.5, [], None]:
            with self.subTest(value=value):
                invalid = copy.deepcopy(index)
                invalid['entries'][0]['checkpointSequence'] = value
                with self.assertRaises(checker.ContinuityError):
                    checker.validate_index(invalid)

    def test_package_guard_command_executes_installed_checker(self):
        package = json.loads((ROOT / 'governance/package-manifest.json').read_text())
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for entry in package['files']:
                if entry['strategy'] != 'managed':
                    continue
                target = root / entry['target']
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((ROOT / entry['source']).read_bytes())
            commands = [line.strip().removeprefix('command:').strip()
                        for line in (root / 'worktree-guard.yaml').read_text().splitlines()
                        if line.strip().startswith('command:')]
            self.assertEqual(len(commands), 1)
            argv = shlex.split(commands[0])
            self.assertEqual(argv, ['python3', '.governance/worktree_overlap_check.py',
                                    '--workspace-root', '{workdir}'])
            subprocess.run(['git', 'init', '--quiet', '--initial-branch=main', str(root)],
                           check=True, capture_output=True)
            result = subprocess.run(
                [sys.executable, str(root / argv[1]), '--workspace-root', str(root),
                 '--format', 'json'], capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report['status'], 'passed')
            self.assertEqual(report['summary']['checkouts'], 1)


if __name__ == '__main__':
    unittest.main()
