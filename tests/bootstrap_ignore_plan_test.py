"""Real Git qualification of opt-in first-bootstrap trackability prerequisites."""
import contextlib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def load(path):
    spec = importlib.util.spec_from_file_location('bootstrap_ignore_adopter', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class BootstrapIgnorePlanTest(unittest.TestCase):
    def command(self, root, *args, check=True):
        result = subprocess.run(args, cwd=root, capture_output=True, text=True,
                                env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
        if check and result.returncode:
            self.fail(result.stdout + result.stderr)
        return result

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.target = self.base / 'product'
        self.command(self.base, 'git', 'init', '-q', '-b', 'main', str(self.target))
        self.command(self.target, 'git', 'config', 'user.name', 'Fixture')
        self.command(self.target, 'git', 'config', 'user.email', 'fixture@example.invalid')
        self.command(self.target, 'git', 'remote', 'add', 'origin', 'https://github.com/owner/product.git')
        self.original = b'.aider*\n/project/\n!/project/\n/project/*\nsecrets/\n'
        (self.target / '.gitignore').write_bytes(self.original)
        (self.target / 'project').mkdir()
        for rel in ['README.md', 'VERSION', 'CHANGELOG.md', 'TODO.md']:
            (self.target / rel).write_text('0.1.0\n' if rel == 'VERSION' else '# Product\n')
        (self.target / 'foreign.txt').write_text('original\n')
        self.command(self.target, 'git', 'add', '.')
        self.command(self.target, 'git', 'commit', '-q', '-m', 'Fixture product')
        self.head = self.command(self.target, 'git', 'rev-parse', 'HEAD').stdout.strip()
        self.names = ['.aider.conf.yml', 'project/new-ticket.sh']
        self.payloads = {name: b'fixture' for name in self.names}
        self.payloads['.gitignore'] = self.original
        self.document = {'schema': 'new-project.bootstrap-ignore-plan/v1', 'baseSha': self.head,
                         'gitignoreSha256': hashlib.sha256(self.original).hexdigest(), 'paths': self.names}
        self.plan = self.base / 'plan.json'
        self.save()
        self.module = load(ROOT / 'scripts/create_adoption_lock.py')

    def save(self):
        self.plan.write_text(json.dumps(self.document))

    def resolve(self):
        return self.module.bootstrap_ignore_payload(self.target, self.payloads, self.plan)[0]

    def test_exact_leaf_projection_preserves_unrelated_ignore_rules(self):
        projected = self.resolve()
        self.assertEqual((self.target / '.gitignore').read_bytes(), self.original)
        self.assertTrue(projected.startswith(self.original))
        (self.target / '.gitignore').write_bytes(projected)
        self.assertEqual(self.module.ignored_payload_targets(self.target, set(self.names)), [])
        self.assertEqual(self.module.ignored_payload_targets(
            self.target, {'.aider.history', 'project/private.txt', 'secrets/password'}),
            ['.aider.history', 'project/private.txt', 'secrets/password'])

    def test_invalid_and_stale_plans_refuse_without_writes(self):
        original_plan = dict(self.document)
        for change in [{'baseSha': 'a' * 40}, {'gitignoreSha256': '0' * 64},
                       {'schema': 'unknown'}, {'extra': True}, {'paths': []},
                       {'paths': self.names * 2}, {'paths': self.names[:1]},
                       {'paths': ['../outside']}, {'paths': ['project/*']},
                       {'paths': ['project/']}, {'paths': ['source.py']}, {'paths': [None]},
                       {'paths': ['.gitignore']}]:
            with self.subTest(change=change):
                self.document = {**original_plan, **change}
                self.save()
                with self.assertRaises(SystemExit):
                    self.resolve()
                self.assertEqual((self.target / '.gitignore').read_bytes(), self.original)

    def test_dirty_ignore_is_not_admitted_even_with_matching_hash(self):
        changed = self.original + b'# other writer\n'
        (self.target / '.gitignore').write_bytes(changed)
        self.document['gitignoreSha256'] = hashlib.sha256(changed).hexdigest()
        self.save()
        with self.assertRaisesRegex(SystemExit, 'committed root ignore'):
            self.resolve()
        self.assertEqual((self.target / '.gitignore').read_bytes(), changed)

    def test_excluded_parent_and_nested_ignore_rules_refuse(self):
        for content in [b'.aider*\n/project/\n', self.original]:
            with self.subTest(content=content):
                (self.target / '.gitignore').write_bytes(content)
                (self.target / 'project').mkdir(exist_ok=True)
                if content == self.original:
                    (self.target / 'project/.gitignore').write_text('new-ticket.sh\n')
                self.command(self.target, 'git', 'add', '.gitignore')
                self.command(self.target, 'git', 'commit', '-q', '--allow-empty', '-m', 'Changed ignore fixture')
                self.document.update(baseSha=self.command(self.target, 'git', 'rev-parse', 'HEAD').stdout.strip(),
                                     gitignoreSha256=hashlib.sha256(content).hexdigest())
                self.payloads['.gitignore'] = content
                self.save()
                with self.assertRaisesRegex(SystemExit, 'excluded parent|only root'):
                    self.resolve()

    def test_duplicate_keys_and_symlinked_inputs_refuse(self):
        original = self.plan.read_bytes()
        self.plan.write_bytes(original[:-1] + b',"paths":[]}')
        with self.assertRaisesRegex(SystemExit, 'duplicate'):
            self.resolve()
        self.plan.write_bytes(original)
        real = self.base / 'real.json'
        self.plan.rename(real)
        self.plan.symlink_to(real)
        with self.assertRaises(SystemExit):
            self.resolve()
        self.plan.unlink()
        real.rename(self.plan)
        (self.target / '.gitignore').rename(self.base / 'ignore')
        (self.target / '.gitignore').symlink_to(self.base / 'ignore')
        with self.assertRaises(SystemExit):
            self.resolve()

    def test_internal_plan_and_symlinked_leaf_refuse(self):
        self.plan = self.target / 'plan.json'
        self.save()
        with self.assertRaisesRegex(SystemExit, 'external'):
            self.resolve()
        self.plan.unlink()
        self.plan = self.base / 'plan.json'
        (self.target / '.aider.conf.yml').symlink_to(self.base / 'outside')
        with self.assertRaisesRegex(SystemExit, 'symlinked'):
            self.resolve()

    def test_cli_refuses_plan_outside_first_bootstrap(self):
        with self.assertRaises(SystemExit), contextlib.redirect_stderr(io.StringIO()):
            self.module.main(['--target-root', str(self.target), '--source-revision', self.head,
                              '--bootstrap-ignore-plan', str(self.plan), '--check'])
        self.assertEqual(self.command(self.target, 'git', 'status', '--porcelain').stdout, '')

    def test_missing_parent_refuses_without_creating_it(self):
        (self.target / 'project').rmdir()
        with self.assertRaisesRegex(SystemExit, 'existing parent'):
            self.resolve()
        self.assertFalse((self.target / 'project').exists())

    def installed_source(self):
        source = self.base / 'standard'
        self.command(self.base, 'git', 'clone', '-q', '--shared', '--no-hardlinks', str(ROOT), str(source))
        if not os.environ.get('NP_TEST_BASELINE'):
            shutil.copy2(ROOT / 'scripts/create_adoption_lock.py', source / 'scripts/create_adoption_lock.py')
        self.command(source, 'git', 'config', 'user.name', 'Fixture')
        self.command(source, 'git', 'config', 'user.email', 'fixture@example.invalid')
        self.command(source, 'git', 'add', 'scripts/create_adoption_lock.py')
        self.command(source, 'git', 'commit', '-q', '--allow-empty', '-m', 'Fixture implementation')
        return load(source / 'scripts/create_adoption_lock.py'), self.command(source, 'git', 'rev-parse', 'HEAD').stdout.strip()

    def exercise_install_and_allocation(self, mode):
        module, revision = self.installed_source()
        paths = ['.aider.conf.yml', 'project/governance-check.bat', 'project/governance-check.sh',
                 'project/new-ticket.sh', 'project/readme.sh', 'project/TICKETS.md']
        self.document['paths'] = paths
        self.save()
        seed = self.base / 'seeds.json'
        content = '# Ticket index\n'
        seed.write_text(json.dumps({'schema': 'new-project.bootstrap-prerequisites-plan/v1',
            'baseSha': self.head, 'files': [{'path': 'project/TICKETS.md', 'content': content,
                                           'sha256': hashlib.sha256(content.encode()).hexdigest()}]}))
        args = ['--target-root', str(self.target), '--source-revision', revision,
                mode, '--bootstrap-prerequisites-plan', str(seed)]
        before = self.command(self.target, 'git', 'status', '--porcelain').stdout
        with patch.object(module, 'verify_publication_evidence'), contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaisesRegex(SystemExit, 'ignored by target Git rules'):
                module.main(args + ['--check'])
            self.assertEqual(module.main(args + ['--bootstrap-ignore-plan', str(self.plan), '--check']), 1)
            self.assertEqual(self.command(self.target, 'git', 'status', '--porcelain').stdout, before)
            self.assertEqual(module.main(args + ['--bootstrap-ignore-plan', str(self.plan), '--upgrade']), 0)
        self.assertEqual(module.ignored_payload_targets(self.target, set(paths)), [])
        receipt = json.loads((self.target / '.subactor/receipts/bootstrap-adoption.json').read_text())
        self.assertFalse(receipt['grantsWriterAuthority'])
        self.assertEqual(receipt['files']['.gitignore'], hashlib.sha256((self.target / '.gitignore').read_bytes()).hexdigest())
        scope = []
        for name in sorted(receipt['files']):
            scope += ['--path', name]
        observed = self.command(self.target, sys.executable, '.governance/work_start_check.py',
            '--root', '.', '--workstream', 'governance', *scope, '--allocation-check', check=False)
        digest = json.loads(observed.stdout)['worktrees'][0]['dirtyDigest']
        result = self.command(self.target, 'bash', 'project/new-ticket.sh', '--title', 'Bootstrap ignore adoption',
            '--agent', 'fixture', '--writer-actor', 'agent:fixture', '--writer-session', 'ignore-plan-fixture',
            '--workstream', 'governance', *scope, '--worktree-slug', 'ignore-plan', '--bootstrap-adoption-digest', digest)
        wt = self.target / '.worktrees/ticket-001--ignore-plan'
        self.assertTrue((wt / 'project/ticket-001/intent.json').is_file(), result.stdout)
        self.assertEqual(self.command(wt, 'git', 'rev-parse', 'HEAD').stdout.strip(), self.head)
        self.assertEqual((wt / '.gitignore').read_bytes(), self.original)

    def test_first_install_check_and_canonical_allocation(self):
        self.exercise_install_and_allocation('--bootstrap-native-adoption')

    def test_legacy_migration_check_and_canonical_allocation(self):
        (self.target / '.governance').mkdir()
        (self.target / '.governance/manifest.json').write_text(json.dumps({
            'schema': 'wellmanifest.manifest/v1',
            'standard': {'id': 'profile:baseline', 'version': '0.20.37'}}))
        self.command(self.target, 'git', 'add', '.governance/manifest.json')
        self.command(self.target, 'git', 'commit', '-q', '-m', 'Minimal legacy scaffold')
        self.head = self.command(self.target, 'git', 'rev-parse', 'HEAD').stdout.strip()
        self.document['baseSha'] = self.head
        self.save()
        self.exercise_install_and_allocation('--migrate-wellman-scaffold')

    def test_prewrite_recheck_preserves_concurrent_ignore_change(self):
        self.exercise_prewrite_race(change_plan=False)

    def test_prewrite_recheck_refuses_rebound_plan_with_identical_projection(self):
        self.exercise_prewrite_race(change_plan=True)

    def exercise_prewrite_race(self, change_plan):
        # The second plan resolution is the effect fence, after read-only planning.
        module, revision = self.installed_source()
        self.document['paths'] = ['.aider.conf.yml', 'project/governance-check.bat',
            'project/governance-check.sh', 'project/new-ticket.sh', 'project/readme.sh']
        self.save()
        (self.target / 'project/TICKETS.md').write_text('# Tickets\n')
        original = module.bootstrap_ignore_payload
        calls = 0
        changed = self.original + b'# concurrent writer\n'
        def race(*args):
            nonlocal calls
            calls += 1
            if calls == 2:
                if change_plan:
                    self.command(self.target, 'git', 'commit', '-q', '--allow-empty', '-m', 'Concurrent base')
                    self.document['baseSha'] = self.command(self.target, 'git', 'rev-parse', 'HEAD').stdout.strip()
                    self.save()
                else:
                    (self.target / '.gitignore').write_bytes(changed)
            return original(*args)
        # This fixture starts with the prerequisite already committed. Force
        # staging is fixture setup only, never a production bootstrap remedy.
        self.command(self.target, 'git', 'add', '-f', 'project/TICKETS.md')
        self.command(self.target, 'git', 'commit', '-q', '-m', 'Committed fixture prerequisite')
        self.document['baseSha'] = self.command(self.target, 'git', 'rev-parse', 'HEAD').stdout.strip()
        self.save()
        with patch.object(module, 'verify_publication_evidence'), patch.object(module, 'bootstrap_ignore_payload', side_effect=race):
            with self.assertRaisesRegex(SystemExit, 'plan changed|committed root ignore'):
                module.main(['--target-root', str(self.target), '--source-revision', revision,
                    '--bootstrap-native-adoption', '--bootstrap-ignore-plan', str(self.plan), '--upgrade'])
        self.assertEqual((self.target / '.gitignore').read_bytes(), self.original if change_plan else changed)
        self.assertFalse((self.target / '.governance/manifest.json').exists())


if __name__ == '__main__':
    unittest.main()
