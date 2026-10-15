#!/usr/bin/env python3
"""Real Git source pins, fail-closed publication and workflow effect boundaries."""
import copy
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import standard_propagation_request as request
from jsonschema import Draft202012Validator


class PropagationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cache = ROOT / '.subactor/cache'
        cache.mkdir(parents=True, exist_ok=True)
        cls.tmp = tempfile.TemporaryDirectory(dir=cache, prefix='propagation-test-')
        cls.repo = Path(cls.tmp.name)
        (cls.repo / 'governance').mkdir()
        (cls.repo / 'scripts').mkdir()
        (cls.repo / 'VERSION').write_text('0.20.103\n')
        (cls.repo / 'governance/package-manifest.json').write_text('{"files": []}\n')
        (cls.repo / 'scripts/create_adoption_lock.py').write_text('# exact tool bytes\n')
        cls.git('init', '-q')
        cls.git('add', '.')
        cls.git('-c', 'user.name=Test', '-c', 'user.email=test@example.invalid',
                '-c', 'core.hooksPath=/dev/null', 'commit', '-qm', 'fixture')
        cls.revision = cls.git('rev-parse', 'HEAD').strip()

    @classmethod
    def git(cls, *args):
        return subprocess.check_output(['git', *args], cwd=cls.repo, text=True,
                                       env=request.publication.plan_git_environment())

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def setUp(self):
        self.event = {'repository': {'full_name': request.REPOSITORY},
                      'inputs': {'target-version': '0.20.103', 'dry-run': 'true'}}
        self.release = {'tag_name': 'v0.20.103', 'draft': False, 'prerelease': False,
                        'published_at': '2026-10-15T19:00:00Z'}
        real_run = subprocess.run
        def remote(*args, **kwargs):
            command = args[0]
            if command[:3] == ['git', 'ls-remote', '--tags']:
                return subprocess.CompletedProcess(command, 0,
                    'a' * 40 + '\trefs/tags/v0.20.103\n' + self.revision + '\trefs/tags/v0.20.103^{}\n', '')
            return real_run(*args, **kwargs)
        self.remote = patch.object(subprocess, 'run', side_effect=remote)
        self.release_transport = patch.object(request.publication, 'canonical_release', side_effect=lambda _: self.release)
        self.remote.start()
        self.release_transport.start()
        self.addCleanup(self.remote.stop)
        self.addCleanup(self.release_transport.stop)

    def build(self):
        return request.build_request(self.repo, 'workflow_dispatch', self.event)

    def test_real_git_pins_and_closed_schema(self):
        result = self.build()
        self.assertEqual(result['source']['revision'], self.revision)
        self.assertEqual(result['source']['adoptionToolSha256'], hashlib.sha256(b'# exact tool bytes\n').hexdigest())
        schema = json.loads((ROOT / 'governance/standard-propagation-request.schema.json').read_text())
        validator = Draft202012Validator(schema)
        validator.validate(result)
        for mutation in ({'executionAuthorized': True}, {'readOnly': False}, {'targets': ['org/repo']}, {'grant': 'yes'}):
            with self.subTest(mutation=mutation):
                self.assertTrue(list(validator.iter_errors(dict(result, **mutation))))

    def test_source_version_disagreement_refused(self):
        self.event['inputs']['target-version'] = '0.20.104'
        # Transport provides no matching requested tag: there is no HEAD fallback.
        with self.assertRaises(SystemExit):
            self.build()

    def test_final_release_required(self):
        for change in ({'draft': True}, {'prerelease': True}, {'published_at': None},
                       {'published_at': ''}, {'tag_name': 'v0.20.104'}, {'draft': 0}):
            with self.subTest(change=change):
                before = self.release
                self.release = dict(before, **change)
                with self.assertRaises(SystemExit):
                    self.build()
                self.release = before

    def test_missing_or_lightweight_tag_refused(self):
        for output in ('', self.revision + '\trefs/tags/v0.20.103\n'):
            with self.subTest(output=output), patch.object(subprocess, 'run', return_value=subprocess.CompletedProcess([], 0, output, '')):
                with self.assertRaises(SystemExit):
                    self.build()

    def test_source_bytes_must_exist(self):
        original = self.repo / 'scripts/create_adoption_lock.py'
        # A separate committed revision lacks the tool; working-tree content cannot fill it.
        self.git('rm', '-q', 'scripts/create_adoption_lock.py')
        self.git('-c', 'user.name=Test', '-c', 'user.email=test@example.invalid',
                 '-c', 'core.hooksPath=/dev/null', 'commit', '-qm', 'missing tool')
        previous = self.revision
        self.revision = self.git('rev-parse', 'HEAD').strip()
        try:
            with self.assertRaises(subprocess.CalledProcessError):
                self.build()
        finally:
            self.revision = previous
            self.git('reset', '--hard', '-q', previous)
        self.assertTrue(original.exists())

    def test_working_tree_cannot_replace_source_pins(self):
        tool = self.repo / 'scripts/create_adoption_lock.py'
        before = tool.read_bytes()
        try:
            tool.write_text('# modified uncommitted tool\n')
            self.assertEqual(self.build()['source']['adoptionToolSha256'], hashlib.sha256(before).hexdigest())
        finally:
            tool.write_bytes(before)

    def test_release_revision_must_match_remote_tag(self):
        with patch.object(request.publication, 'canonical_tag_revision', side_effect=[self.revision, 'b' * 40]):
            with self.assertRaises(SystemExit):
                self.build()

    def test_committed_version_must_match_tag(self):
        path = self.repo / 'VERSION'
        path.write_text('0.20.104\n')
        self.git('add', 'VERSION')
        self.git('-c', 'user.name=Test', '-c', 'user.email=test@example.invalid',
                 '-c', 'core.hooksPath=/dev/null', 'commit', '-qm', 'wrong version')
        previous = self.revision
        self.revision = self.git('rev-parse', 'HEAD').strip()
        try:
            with self.assertRaises(ValueError):
                self.build()
        finally:
            self.revision = previous
            self.git('reset', '--hard', '-q', previous)

    def test_invalid_versions_rejected_before_network(self):
        for version in ('', '01.2.3', '1.2', '1.2.3-rc1', '1.2.3\n', '$(touch BAD)', True, 123, None):
            with self.subTest(version=version):
                self.event['inputs']['target-version'] = version
                with self.assertRaises(ValueError):
                    self.build()

    def test_live_or_ambiguous_dispatch_refused(self):
        for value in (False, 'false', 1, 'True', None, '', []):
            self.event['inputs']['dry-run'] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.build()
        self.event['inputs']['dry-run'] = True
        self.assertFalse(self.build()['executionAuthorized'])
        self.event['inputs']['extra'] = 'authority'
        with self.assertRaises(ValueError):
            self.build()

    def test_repository_and_event_name(self):
        for name in ('other/repo', None, 'wellmanifest/new-project\n'):
            self.event['repository']['full_name'] = name
            with self.assertRaises(ValueError):
                self.build()
        with self.assertRaises(ValueError):
            request.build_request(self.repo, 'push', self.event)

    def test_release_event_checks(self):
        event = {'action': 'published', 'repository': {'full_name': request.REPOSITORY}, 'release': self.release}
        self.assertFalse(request.build_request(self.repo, 'release', event)['executionAuthorized'])
        for field, value in (('draft', True), ('prerelease', True), ('tag_name', '0.20.103'), ('published_at', None)):
            bad = copy.deepcopy(event)
            bad['release'][field] = value
            with self.assertRaises(ValueError):
                request.build_request(self.repo, 'release', bad)

    def test_event_size_duplicates_and_type(self):
        path = self.repo / 'event.json'
        for raw in (b'[]', b'{"a":1,"a":2}', b'{"a":{"b":1,"b":2}}', b'{"a":NaN}', b'x' * (request.MAX_EVENT_BYTES + 1)):
            path.write_bytes(raw)
            with self.subTest(raw=raw[:50]), self.assertRaises(ValueError):
                request.read_event(path)
        path.unlink()

    def test_cli_refusal_writes_no_request(self):
        path = self.repo / 'event.json'
        bad = copy.deepcopy(self.event)
        bad['inputs']['dry-run'] = 'false'
        path.write_text(json.dumps(bad))
        result = subprocess.run([sys.executable, '-B', str(ROOT / 'scripts/standard_propagation_request.py'),
                                 '--event-name', 'workflow_dispatch', '--event-path', str(path)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, '')
        self.assertIn('protected product admission', result.stderr)
        path.unlink()

    def test_workflow_has_only_read_only_artifact_path(self):
        flow = json.loads((ROOT / '.github/workflows/propagate-standard.yml').read_text())
        self.assertEqual(flow['permissions'], {'contents': 'read'})
        self.assertEqual(set(flow['jobs']), {'advisory-request'})
        steps = flow['jobs']['advisory-request']['steps']
        self.assertEqual(len(steps), 3)
        self.assertTrue(steps[2]['with']['include-hidden-files'])
        self.assertEqual(steps[2]['with']['path'], '.subactor/receipts/standard-propagation-request.json')
        self.assertEqual(steps[0]['with'], {'fetch-depth': 0, 'persist-credentials': False})
        for step in steps:
            if 'uses' in step:
                self.assertRegex(step['uses'], r'@ [0-9a-f]{40}$'.replace(' ', ''))
            if 'run' in step:
                self.assertNotIn('${{', step['run'])
                self.assertIn('--event-path "$GITHUB_EVENT_PATH"', step['run'])
                self.assertEqual(step['env']['GH_TOKEN'], '${{ github.token }}')
        text = json.dumps(flow)
        for forbidden in ('ORG_GOVERNANCE_TOKEN', 'goal governance adopt', 'create-pull-request',
                          'pip install', 'gh repo list', 'rev-parse HEAD'):
            self.assertNotIn(forbidden, text)
        self.assertIn('tests/standard_propagation_request_test.py', (ROOT / '.github/workflows/ci.yml').read_text())


if __name__ == '__main__':
    unittest.main()
