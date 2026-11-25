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

    def prepare_subactor_layout(self, rule=b'.subactor/'):
        self.original = b'# Legacy ignores\nsecrets/\n' + rule + b'\n*.scratch\n'
        (self.target / '.gitignore').write_bytes(self.original)
        (self.target / 'project/TICKETS.md').write_text('# Ticket index\n')
        self.command(self.target, 'git', 'add', '.gitignore', 'project/TICKETS.md')
        self.command(self.target, 'git', 'commit', '-q', '-m', 'Committed legacy Subactor ignore')
        self.head = self.command(self.target, 'git', 'rev-parse', 'HEAD').stdout.strip()
        (self.target / '.subactor').mkdir()
        self.names = ['.subactor/manifest.json', '.subactor/.gitignore']
        self.payloads = {'.gitignore': self.original, '.subactor/manifest.json': b'{}\n',
                         '.subactor/.gitignore': b'/leases/\n/cache/\n'}
        self.document.update(baseSha=self.head, paths=self.names,
                             gitignoreSha256=hashlib.sha256(self.original).hexdigest())
        self.save()

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

    def test_subactor_requires_literal_root_rule(self):
        self.prepare_subactor_layout(b'/.subactor/')
        with self.assertRaisesRegex(SystemExit, 'literal .subactor/'):
            self.resolve()
        self.assertEqual((self.target / '.gitignore').read_bytes(), self.original)

    def test_subactor_refuses_repository_exclude_source(self):
        self.prepare_subactor_layout(b'# No root Subactor exclusion')
        (self.target / '.git/info/exclude').write_bytes(b'.subactor/\n')
        with self.assertRaisesRegex(SystemExit, 'only root'):
            self.resolve()
        self.assertEqual((self.target / '.gitignore').read_bytes(), self.original)

    def test_subactor_refuses_case_insensitive_git_matching(self):
        self.prepare_subactor_layout()
        self.command(self.target, 'git', 'config', 'core.ignoreCase', 'true')
        with self.assertRaisesRegex(SystemExit, 'case-sensitive'):
            self.resolve()
        self.assertEqual((self.target / '.gitignore').read_bytes(), self.original)

    def test_subactor_requires_exact_pair_base_and_digest(self):
        self.prepare_subactor_layout()
        approved = dict(self.document)
        other = '.subactor/arbitrary.json'
        self.payloads[other] = b'{}\n'
        for change in [{'paths': self.names[:1]}, {'paths': self.names + [other]},
                       {'paths': [self.names[0], other]}, {'baseSha': 'a' * 40},
                       {'gitignoreSha256': '0' * 64}]:
            with self.subTest(change=change):
                self.document = {**approved, **change}
                self.save()
                with self.assertRaises(SystemExit):
                    self.resolve()
                self.assertEqual((self.target / '.gitignore').read_bytes(), self.original)
                self.assertEqual(list((self.target / '.subactor').iterdir()), [])

    def test_subactor_refuses_symlinked_parent_and_leaves(self):
        self.prepare_subactor_layout()
        directory = self.target / '.subactor'
        referent = self.base / 'referent'
        referent.mkdir()
        directory.rmdir()
        directory.symlink_to(referent, target_is_directory=True)
        with self.assertRaisesRegex(SystemExit, 'symlinked'):
            self.resolve()
        directory.unlink()
        directory.mkdir()
        for name in self.names:
            with self.subTest(name=name):
                leaf = self.target / name
                leaf.symlink_to(referent / 'absent')
                with self.assertRaisesRegex(SystemExit, 'symlinked'):
                    self.resolve()
                leaf.unlink()
        self.assertEqual(list(referent.iterdir()), [])
        self.assertEqual((self.target / '.gitignore').read_bytes(), self.original)

    def test_subactor_refuses_committed_symlink_at_root_ignore(self):
        self.prepare_subactor_layout()
        root_ignore = self.target / '.gitignore'
        root_ignore.unlink()
        root_ignore.symlink_to('.subactor/', target_is_directory=True)
        self.command(self.target, 'git', 'add', '.gitignore')
        self.command(self.target, 'git', 'commit', '-q', '-m', 'Symlinked root ignore')
        root_ignore.unlink()
        self.original = b'.subactor/'
        root_ignore.write_bytes(self.original)
        self.payloads['.gitignore'] = self.original
        self.document.update(baseSha=self.command(self.target, 'git', 'rev-parse', 'HEAD').stdout.strip(),
                             gitignoreSha256=hashlib.sha256(self.original).hexdigest())
        self.save()
        with self.assertRaisesRegex(SystemExit, 'committed regular root'):
            self.resolve()
        self.assertEqual(root_ignore.read_bytes(), self.original)

    def test_subactor_accepts_safe_existing_child_ignore(self):
        self.prepare_subactor_layout()
        leaf = self.target / '.subactor/.gitignore'
        content = b'# Existing Git rules\r\n/private/\r\n'
        leaf.write_bytes(content)
        self.assertTrue(self.resolve().startswith(self.original))
        self.assertEqual(leaf.read_bytes(), content)

    def test_subactor_refuses_unsafe_existing_or_projected_child_ignore(self):
        self.prepare_subactor_layout()
        leaf = self.target / '.subactor/.gitignore'
        for content in [b'!/private.txt\n', b'*\n', b'/manifest.json\n']:
            with self.subTest(content=content):
                leaf.write_bytes(content)
                with self.assertRaisesRegex(SystemExit, 'literal anchored directory exclusions'):
                    self.resolve()
                self.assertEqual(leaf.read_bytes(), content)
                leaf.unlink()
                self.payloads['.subactor/.gitignore'] = content
                with self.assertRaisesRegex(SystemExit, 'literal anchored directory exclusions'):
                    self.resolve()
                self.payloads['.subactor/.gitignore'] = b'/leases/\n'
                self.assertEqual((self.target / '.gitignore').read_bytes(), self.original)

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

    def install(self, mode, *options, protected=None):
        module, revision = self.installed_source()
        args = ['--target-root', str(self.target), '--source-revision', revision, mode, *options]
        receipt_path = '.subactor/receipts/bootstrap-adoption.json'
        before = self.command(self.target, 'git', 'status', '--porcelain').stdout
        planned = io.StringIO()
        with patch.object(module, 'verify_publication_evidence'), contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaisesRegex(SystemExit, 'ignored by target Git rules'):
                module.main(args + ['--check'])
            args += ['--bootstrap-ignore-plan', str(self.plan)]
            with contextlib.redirect_stdout(planned):
                self.assertEqual(module.main(args + ['--check']), 1)
            self.assertIn('UPDATE .gitignore', planned.getvalue())
            self.assertEqual((self.target / '.gitignore').read_bytes(), self.original)
            self.assertFalse((self.target / receipt_path).exists())
            self.assertFalse((self.target / '.governance/manifest.lock.json').exists())
            self.assertEqual(self.command(self.target, 'git', 'status', '--porcelain').stdout, before)
            for name, content in (protected or {}).items():
                self.assertEqual((self.target / name).read_bytes(), content)
            self.assertEqual(module.main(args + ['--upgrade']), 0)
        self.assertEqual(module.ignored_payload_targets(self.target, set(self.document['paths'])), [])
        root_ignore = (self.target / '.gitignore').read_bytes()
        self.assertTrue(root_ignore.startswith(self.original))
        receipt = json.loads((self.target / receipt_path).read_text())
        self.assertFalse(receipt['grantsWriterAuthority'])
        self.assertFalse(receipt['grantsPublicationAuthority'])
        self.assertEqual(receipt['baseSha'], self.head)
        self.assertEqual(receipt['sourceRevision'], revision)
        self.assertEqual(receipt['commonGitDir'], str(self.target / '.git'))
        self.assertEqual(receipt['files']['.gitignore'], hashlib.sha256(root_ignore).hexdigest())
        return receipt

    def allocate(self, receipt):
        scope = []
        for name in sorted(receipt['files']):
            scope += ['--path', name]
        inspect = [sys.executable, '.governance/work_start_check.py',
                   '--root', '.', '--workstream', 'governance', *scope, '--allocation-check']
        observed = self.command(self.target, *inspect, check=False)
        digest = json.loads(observed.stdout)['worktrees'][0]['dirtyDigest']
        self.assertNotEqual(observed.returncode, 0)
        denied = self.command(self.target, *inspect, '--bootstrap-adoption-digest', '0' * 64, check=False)
        self.assertNotEqual(denied.returncode, 0)
        admitted = self.command(self.target, *inspect, '--bootstrap-adoption-digest', digest)
        report = json.loads(admitted.stdout)
        self.assertEqual(report['route'], 'NEW_TICKET_CANDIDATE')
        acknowledgement = report['bootstrapOwnerAcknowledgement']
        self.assertEqual(acknowledgement['dirtyDigest'], digest)
        self.assertFalse(acknowledgement['grantsWriterAuthority'])
        self.assertTrue(set(self.document['paths']).issubset(acknowledgement['paths']))
        result = self.command(self.target, 'bash', 'project/new-ticket.sh', '--title', 'Bootstrap ignore adoption',
            '--agent', 'fixture', '--writer-actor', 'agent:fixture', '--writer-session', 'ignore-plan-fixture',
            '--workstream', 'governance', *scope, '--worktree-slug', 'ignore-plan', '--bootstrap-adoption-digest', digest)
        wt = self.target / '.worktrees/ticket-001--ignore-plan'
        intent_path = wt / 'project/ticket-001/intent.json'
        self.assertTrue(intent_path.is_file(), result.stdout)
        self.assertTrue(set(receipt['files']).issubset(json.loads(intent_path.read_text())['allowedPaths']))
        self.assertEqual(self.command(wt, 'git', 'rev-parse', 'HEAD').stdout.strip(), self.head)
        self.assertEqual((wt / '.gitignore').read_bytes(), self.original)
        lease = json.loads((self.target / '.subactor/leases/ticket-001--ignore-plan.json').read_text())
        self.assertEqual(lease['ticketId'], 'ticket-001')
        self.assertEqual(lease['branchRef'], 'refs/heads/ticket/001-ignore-plan')
        self.assertEqual(lease['worktreeId'], wt.name)
        self.assertEqual(lease['headSha'], self.head)
        self.assertEqual(lease['ownerActor'], 'agent:fixture')
        self.assertEqual(lease['ownerSession'], 'ignore-plan-fixture')
        self.assertEqual((lease['leaseRevision'], lease['fencingToken']), (1, 1))
        self.assertFalse(lease['publicationFrozen'])
        return wt

    def exercise_install_and_allocation(self, mode):
        self.document['paths'] = [
            '.aider.conf.yml', 'project/governance-check.bat', 'project/governance-check.sh',
            'project/new-ticket.sh', 'project/readme.sh', 'project/TICKETS.md',
        ]
        self.save()
        seed = self.base / 'seeds.json'
        content = '# Ticket index\n'
        seed.write_text(json.dumps({'schema': 'new-project.bootstrap-prerequisites-plan/v1',
            'baseSha': self.head, 'files': [{'path': 'project/TICKETS.md', 'content': content,
                                           'sha256': hashlib.sha256(content.encode()).hexdigest()}]}))
        receipt = self.install(mode, '--bootstrap-prerequisites-plan', str(seed))
        self.allocate(receipt)

    def test_first_install_check_and_canonical_allocation(self):
        self.exercise_install_and_allocation('--bootstrap-native-adoption')

    def test_legacy_subactor_parent_first_install_and_canonical_allocation(self):
        self.prepare_subactor_layout()
        protected = {}
        for name in [
            '.subactor/recovery/local.json', '.subactor/leases/local.json', '.subactor/cache/local.json',
            '.subactor/sessions/local.jsonl', '.subactor/snapshots/local.json', '.subactor/unknown-before',
            '.subactor/MANIFEST.JSON', 'nested/.subactor/manifest.json', 'keep.scratch',
        ]:
            path = self.target / name
            path.parent.mkdir(parents=True, exist_ok=True)
            protected[name] = f'Fixture data for {name}\n'.encode()
            path.write_bytes(protected[name])
        leaves = set(self.names)
        before = leaves | set(protected)
        self.assertEqual(self.module.ignored_payload_targets(self.target, before), sorted(before))
        receipt = self.install('--bootstrap-native-adoption', protected=protected)
        self.assertTrue((self.target / '.gitignore').read_bytes().endswith(
            b'!/.subactor/\n/.subactor/*\n!/.subactor/.gitignore\n!/.subactor/manifest.json\n'))
        unknown = '.subactor/unknown-after/arbitrary.json'
        (self.target / unknown).parent.mkdir()
        (self.target / unknown).write_text('{}\n')
        hidden = set(protected) | {'.subactor/receipts/bootstrap-adoption.json', unknown}
        self.assertEqual(self.module.ignored_payload_targets(self.target, leaves | hidden), sorted(hidden))
        status = self.command(self.target, 'git', 'status', '--porcelain', '--untracked-files=all').stdout
        self.assertEqual({line[3:] for line in status.splitlines() if line[3:].startswith('.subactor/')}, leaves)
        for name, content in protected.items():
            self.assertEqual((self.target / name).read_bytes(), content)
        lock = json.loads((self.target / '.governance/manifest.lock.json').read_text())
        self.assertEqual(lock['standard']['sourceRevision'], receipt['sourceRevision'])
        self.assertEqual(lock['standard']['publicationStatus'], 'published')
        for name in leaves:
            checksum = hashlib.sha256((self.target / name).read_bytes()).hexdigest()
            self.assertEqual(receipt['files'][name], checksum)
            self.assertEqual(lock['managedFiles'][name], checksum)
        wt = self.allocate(receipt)
        self.assertFalse((wt / '.subactor').exists())

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
