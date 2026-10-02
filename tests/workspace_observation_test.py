#!/usr/bin/env python3
"""Read-only workspace observation regressions using disposable Git repos."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
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
LIFECYCLE = load('workspace_lifecycle_check')
GUARD = load('worktree_guard')


class NetworkIdentityTests(unittest.TestCase):
    def test_default_ports_and_scp_remain_equivalent(self):
        for module in [OVERLAP, LIFECYCLE]:
            for scheme, port in [('https', 443), ('http', 80), ('ssh', 22), ('git', 9418)]:
                with self.subTest(module=module.__name__, scheme=scheme):
                    self.assertEqual(module.normalized_network_remote(f'{scheme}://host:{port}/org/repo.git'),
                                     module.normalized_network_remote(f'{scheme}://host/org/repo.git'))
            self.assertEqual(module.normalized_network_remote('ssh://git@host:22/org/repo.git'),
                             module.normalized_network_remote('git@host:org/repo.git'))

    def test_nondefault_ports_distinguish_repositories(self):
        for module in [OVERLAP, LIFECYCLE]:
            for host in ['host', '[2001:db8::1]']:
                with self.subTest(module=module.__name__, host=host):
                    identities = {module.normalized_network_remote(f'https://{host}{port}/org/repo.git')
                                  for port in ['', ':8443', ':9443']}
                    self.assertEqual(len(identities), 3)

    def test_invalid_ports_produce_audit_errors(self):
        for module in [OVERLAP, LIFECYCLE]:
            for port in ['wrong', '-1', '65536']:
                with self.subTest(module=module.__name__, port=port):
                    with self.assertRaises(module.AuditError):
                        module.normalized_network_remote(f'https://host:{port}/org/repo.git')


class StopWatching(Exception):
    pass


class WorkspaceObservationTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.primary = Path(self.directory.name) / 'repository'
        self.git('init', '--quiet', '--initial-branch=main', str(self.primary))
        self.git('-C', str(self.primary), 'config', 'user.name', 'Disposable fixture')
        self.git('-C', str(self.primary), 'config', 'user.email', 'fixture@example.invalid')
        (self.primary / '.gitignore').write_text('/.worktrees/\n/.subactor/\n')
        (self.primary / 'source.py').write_text('value = 1\n')
        self.git('-C', str(self.primary), 'add', '.')
        self.git('-C', str(self.primary), 'commit', '--quiet', '-m', 'fixture baseline')
        self.linked = self.primary / '.worktrees/ticket-001--fixture'
        self.git('-C', str(self.primary), 'worktree', 'add', '--relative-paths',
                 '-b', 'ticket/001-fixture', str(self.linked))

    def git(self, *args):
        return subprocess.run(['git', *args], check=True, capture_output=True, text=True,
                              env=GUARD.detached_git_env())

    def dirty_both(self):
        (self.primary / 'source.py').write_text('value = 2\n')
        (self.linked / 'source.py').write_text('value = 3\n')

    def checkouts(self):
        return [OVERLAP.inspect_checkout(path, OVERLAP.DEFAULT_IGNORE)
                for path in [self.primary, self.linked]]

    def test_omitted_inventory_is_derived_for_dirty_overlap(self):
        self.dirty_both()
        findings = OVERLAP.overlap_findings(self.checkouts())
        overlap = next(f for f in findings if f.code == 'GOV-WORKTREE-OVERLAP-001')
        self.assertIn('source.py', overlap.evidence['overlappingPaths'])

    def test_incomplete_inventory_fails_conservatively(self):
        self.dirty_both()
        checkouts = self.checkouts()
        inventory = OVERLAP.workspace_inventory(checkouts)
        inventory['entries'].pop()
        with self.assertRaisesRegex(OVERLAP.AuditError, 'inventory omitted'):
            OVERLAP.overlap_findings(checkouts, inventory=inventory)

    def test_malformed_inventory_fails_with_audit_errors(self):
        checkouts = self.checkouts()
        inventory = OVERLAP.workspace_inventory(checkouts)
        for value in [[], {}, {'entries': None}, {'entries': [None]},
                      {'entries': [{'path': None}]},
                      {'entries': inventory['entries'] * 2}]:
            with self.subTest(inventory=value):
                with self.assertRaises(OVERLAP.AuditError):
                    OVERLAP.overlap_findings(checkouts, inventory=value)

    def test_watcher_detects_dirty_overlap_without_topology_change(self):
        report = Path(self.directory.name) / 'report.json'
        before = GUARD.snapshot(self.primary, [])
        sleeps = 0

        def interval(_):
            nonlocal sleeps
            sleeps += 1
            if sleeps == 1:
                self.dirty_both()
                self.assertEqual(GUARD.snapshot(self.primary, []), before)
            else:
                raise StopWatching()

        with patch.object(GUARD, 'time', SimpleNamespace(sleep=interval)), \
                patch.object(GUARD, 'run_once', wraps=GUARD.run_once) as scan, \
                contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaises(StopWatching):
                GUARD.watch(self.primary, {}, 'json', 1, report,
                            ROOT / 'scripts/worktree_overlap_check.py')
        self.assertEqual(scan.call_count, 2)
        result = json.loads(report.read_text())
        self.assertEqual(result['status'], 'failed')
        self.assertIn('GOV-WORKTREE-OVERLAP-001', {f['code'] for f in result['findings']})


if __name__ == '__main__':
    unittest.main()
