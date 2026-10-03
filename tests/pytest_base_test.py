#!/usr/bin/env python3
"""Actual Git-base and pytest lifecycle regressions in disposable repositories."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


BRIDGE = load('pytest_base_bridge_fixture', 'template/files/wellmanifest_governance.py')
OVERLAP = load('pytest_base_git_environment', 'scripts/worktree_overlap_check.py')


class PytestBaseTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name) / 'repository'
        environment = OVERLAP.detached_git_env()
        for name in ['WELLMANIFEST_BASE_SHA', 'GITHUB_EVENT_PATH', 'GITHUB_BASE_REF',
                     'WELLMANIFEST_GOVERNANCE_ACTIVE']:
            environment.pop(name, None)
        self.environment = patch.dict(os.environ, environment, clear=True)
        self.environment.start()
        self.addCleanup(self.environment.stop)
        self.git('init', '--quiet', '--initial-branch=main', str(self.root))
        self.git('-C', str(self.root), 'config', 'user.name', 'Disposable fixture')
        self.git('-C', str(self.root), 'config', 'user.email', 'fixture@example.invalid')
        (self.root / 'changed.py').write_text('value = 1\n')
        self.git('-C', str(self.root), 'add', '.')
        self.git('-C', str(self.root), 'commit', '--quiet', '-m', 'fixture base')
        self.base = self.git('-C', str(self.root), 'rev-parse', 'HEAD').stdout.strip()
        (self.root / 'changed.py').write_text('value = 2\n')
        self.git('-C', str(self.root), 'commit', '--quiet', '-am', 'fixture head')
        self.head = self.git('-C', str(self.root), 'rev-parse', 'HEAD').stdout.strip()

    def git(self, *args):
        return subprocess.run(['git', *args], check=True, capture_output=True, text=True)

    def test_missing_base_does_not_hide_committed_changes(self):
        with self.assertRaisesRegex(BRIDGE.GovernanceGateError, 'GOV-PACKAGING-003'):
            BRIDGE._resolve_base(self.root)

    def test_explicit_base_preserves_committed_changes(self):
        os.environ['WELLMANIFEST_BASE_SHA'] = self.base
        resolved = BRIDGE._resolve_base(self.root)
        self.assertEqual(resolved, self.base)
        self.assertEqual(BRIDGE._changed_paths(self.root, resolved), ['changed.py'])

    def test_event_base_preserves_committed_changes(self):
        event = self.root.parent / 'event.json'
        event.write_text(json.dumps({'pull_request': {'base': {'sha': self.base}}}))
        os.environ['GITHUB_EVENT_PATH'] = str(event)
        resolved = BRIDGE._resolve_base(self.root)
        self.assertEqual(resolved, self.base)
        self.assertEqual(BRIDGE._changed_paths(self.root, resolved), ['changed.py'])

    def test_verified_upstream_preserves_committed_changes(self):
        self.git('-C', str(self.root), 'update-ref', 'refs/remotes/origin/main', self.base)
        resolved = BRIDGE._resolve_base(self.root)
        self.assertEqual(resolved, self.base)
        self.assertEqual(BRIDGE._changed_paths(self.root, resolved), ['changed.py'])

    def test_verified_equal_head_upstream_remains_valid(self):
        self.git('-C', str(self.root), 'update-ref', 'refs/remotes/origin/main', self.head)
        resolved = BRIDGE._resolve_base(self.root)
        self.assertEqual(resolved, self.head)
        self.assertEqual(BRIDGE._changed_paths(self.root, resolved), [])

    def test_selected_github_base_ref_preserves_committed_changes(self):
        self.git('-C', str(self.root), 'update-ref', 'refs/remotes/origin/main', self.head)
        self.git('-C', str(self.root), 'update-ref', 'refs/remotes/origin/release', self.base)
        os.environ['GITHUB_BASE_REF'] = 'release'
        resolved = BRIDGE._resolve_base(self.root)
        self.assertEqual(resolved, self.base)
        self.assertEqual(BRIDGE._changed_paths(self.root, resolved), ['changed.py'])

    def test_missing_base_stops_actual_pytest_lifecycle_before_gate(self):
        project = self.root / 'project'
        project.mkdir()
        gate = project / 'governance-check.sh'
        gate.write_text('#!/usr/bin/env bash\nprintf "invoked\\n" > gate-invoked\n')
        gate.chmod(0o755)
        (project / 'governance-check.bat').write_text('@echo off\necho invoked>gate-invoked\n')
        session = SimpleNamespace(config=SimpleNamespace(rootpath=self.root))
        with self.assertRaisesRegex(BRIDGE.GovernanceGateError, 'GOV-PACKAGING-003'):
            BRIDGE.pytest_sessionstart(session)
        self.assertFalse((self.root / 'gate-invoked').exists())

    def test_collect_only_needs_no_base_or_gate(self):
        session = SimpleNamespace(config=SimpleNamespace(
            rootpath=self.root, option=SimpleNamespace(collectonly=True)))
        BRIDGE.pytest_sessionstart(session)


if __name__ == '__main__':
    unittest.main()
