#!/usr/bin/env python3
"""Real first-allocation regression; publication is mocked only in fixtures."""
from pathlib import Path
import importlib.util
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
CHANGED = ('project/new-ticket.sh', 'scripts/create_adoption_lock.py', 'scripts/work_start_check.py',
           'scripts/ticket_storage.py', 'scripts/governance_check.py')


class BootstrapTest(unittest.TestCase):
    fresh = False
    legacy_carriers = False
    expected_ticket = 'ticket-001'

    def command(self, cwd, *args, check=True):
        result = subprocess.run(args, cwd=cwd, capture_output=True, text=True,
                                env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
        if check and result.returncode:
            self.fail(result.stdout + result.stderr)
        return result

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.source = self.base / 'standard'
        self.target = self.base / 'product'
        self.command(self.base, 'git', 'clone', '--quiet', '--no-hardlinks', str(ROOT), str(self.source))
        if not os.environ.get('NP_TEST_BASELINE'):
            for rel in CHANGED:
                shutil.copy2(ROOT / rel, self.source / rel)
        self.command(self.source, 'git', 'config', 'user.name', 'Fixture')
        self.command(self.source, 'git', 'config', 'user.email', 'fixture@example.invalid')
        self.command(self.source, 'git', 'add', *CHANGED)
        self.command(self.source, 'git', 'commit', '--quiet', '--allow-empty', '-m', 'Fixture source')
        revision = self.command(self.source, 'git', 'rev-parse', 'HEAD').stdout.strip()
        self.command(self.base, 'git', 'init', '--quiet', '-b', 'main', str(self.target))
        self.command(self.target, 'git', 'config', 'user.name', 'Fixture')
        self.command(self.target, 'git', 'config', 'user.email', 'fixture@example.invalid')
        self.command(self.target, 'git', 'commit', '--quiet', '--allow-empty', '-m', 'Historical base')
        self.historical = self.command(self.target, 'git', 'rev-parse', 'HEAD').stdout.strip()
        (self.target / '.governance').mkdir()
        if not self.fresh:
            (self.target / '.governance/manifest.json').write_text(json.dumps({
                'schema': 'wellmanifest.manifest/v1',
                'standard': {'id': 'profile:baseline', 'version': '0.20.37'}}))
        (self.target / 'README.md').write_text('# Product\n')
        (self.target / '.gitignore').write_text('/.worktrees/\n/.subactor/receipts/\n')
        (self.target / 'foreign.txt').write_text('original\n')
        if self.legacy_carriers:
            carrier = self.target / 'project/ticket-007'
            carrier.mkdir(parents=True)
            (carrier / 'README.md').write_text('# Historical ticket\nStatus: IN_PROGRESS\n')
            (carrier / 'intent.json').write_text('{"ticket":"ticket-007","allowedPaths":["old.py"]}\n')
        self.command(self.target, 'git', 'add', '.')
        self.command(self.target, 'git', 'commit', '--quiet', '-m', 'Legacy scaffold')
        self.head = self.command(self.target, 'git', 'rev-parse', 'HEAD').stdout.strip()
        for rel in ['VERSION', 'CHANGELOG.md', 'TODO.md', 'project/TICKETS.md']:
            p = self.target / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text('0.1.0\n' if rel == 'VERSION' else '# Fixture\n')
        spec = importlib.util.spec_from_file_location('fixture_adopter', self.source / CHANGED[1])
        self.adopter = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.adopter)
        args = ['adopter', '--target-root', str(self.target), '--source-revision', revision,
                '--bootstrap-native-adoption' if self.fresh else '--migrate-wellman-scaffold',
                '--upgrade']
        with patch.object(sys, 'argv', args), patch.object(self.adopter, 'verify_publication_evidence'):
            self.assertEqual(self.adopter.main(), 0)
        self.receipt = self.target / '.subactor/receipts/bootstrap-adoption.json'
        self.assertTrue(self.receipt.is_file(), 'installer must record exact bootstrap bytes')

    def observation(self, checksum=None):
        args = ['python3', '.governance/work_start_check.py', '--root', '.',
                '--workstream', 'governance', '--path', '.governance/**', '--allocation-check']
        if checksum:
            args += ['--bootstrap-adoption-digest', checksum]
        result = self.command(self.target, *args, check=False)
        return result, json.loads(result.stdout)

    def checksum(self):
        # Malformed legacy inputs may refuse before a complete admission report;
        # obtain the exact dirty binding independently through the managed reader.
        result = self.command(self.target, sys.executable, '-c',
            "import sys; from pathlib import Path; sys.path.insert(0, '.governance'); "
            "import work_start_check; print(work_start_check.dirty_observation(Path('.'))[1])")
        return result.stdout.strip()

    def test_first_real_allocator_preserves_foreign_bytes_and_does_not_write_source(self):
        (self.target / 'foreign.txt').write_text('another writer\n')
        checksum = self.checksum()
        result, before = self.observation()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(before['route'], 'RECONCILE')
        result, admitted = self.observation(checksum)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(admitted['route'], 'NEW_TICKET_CANDIDATE')
        self.assertFalse(admitted['grantsAuthority'])
        args = ['bash', './project/new-ticket.sh', '--title', 'Adopt governance', '--agent', 'fixture',
                '--workstream', 'governance', '--path', '.governance/**',
                '--worktree-slug', 'adoption', '--bootstrap-adoption-digest', checksum]
        result = self.command(self.target, *args)
        self.assertIn('Successfully allocated ' + self.expected_ticket, result.stdout)
        wt = self.target / ('.worktrees/' + self.expected_ticket + '--adoption')
        intent = json.loads((wt / 'project' / self.expected_ticket / 'intent.json').read_text())
        self.assertIn('.governance/**', intent['allowedPaths'])
        self.assertEqual(self.command(wt, 'git', 'rev-parse', 'HEAD').stdout.strip(), self.head)
        # The allocator writes metadata only: product and adoption source stay on their old base.
        self.assertEqual((wt / 'foreign.txt').read_text(), 'original\n')
        self.assertEqual((self.target / 'foreign.txt').read_text(), 'another writer\n')
        if self.fresh:
            self.assertFalse((wt / '.governance/manifest.json').exists())
        else:
            self.assertEqual(json.loads((wt / '.governance/manifest.json').read_text())['schema'],
                             'wellmanifest.manifest/v1')
        result, _ = self.observation(checksum)
        self.assertNotEqual(result.returncode, 0, 'second allocation must not reuse bootstrap acknowledgement')

    def test_integrated_ref_survives_real_first_allocation(self):
        ref = 'ticket/003-historical'
        self.command(self.target, 'git', 'branch', ref, self.historical)
        self.test_first_real_allocator_preserves_foreign_bytes_and_does_not_write_source()
        self.assertEqual(self.command(self.target, 'git', 'rev-parse', ref).stdout.strip(),
                         self.historical)

    def test_ref_at_base_remains_ambiguous(self):
        self.command(self.target, 'git', 'branch', 'ticket/003-pending')
        result, _ = self.observation(self.checksum())
        self.assertNotEqual(result.returncode, 0)

    def test_unintegrated_ref_is_refused_without_deletion(self):
        tree = self.command(self.target, 'git', 'rev-parse', 'HEAD^{tree}').stdout.strip()
        sha = self.command(self.target, 'git', 'commit-tree', tree, '-m', 'Unrelated writer').stdout.strip()
        ref = 'refs/heads/ticket/003-unintegrated'
        self.command(self.target, 'git', 'update-ref', ref, sha)
        result, _ = self.observation(self.checksum())
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.command(self.target, 'git', 'rev-parse', ref).stdout.strip(), sha)

    def test_unreadable_ref_is_refused(self):
        checksum = self.checksum()
        path = self.target / '.git/refs/heads/ticket/003-broken'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('f' * 40 + '\n')
        result, _ = self.observation(checksum)
        self.assertNotEqual(result.returncode, 0)

    def test_integrated_ref_retains_live_ownership(self):
        ref = 'refs/heads/ticket/003-historical'
        self.command(self.target, 'git', 'update-ref', ref, self.historical)
        path = self.target / '.subactor/leases/ticket-003--historical.json'
        path.parent.mkdir(parents=True, exist_ok=True)
        for expiry, accepted in [('2099-01-01T00:00:00Z', False),
                                 ('invalid', False), ('2000-01-01T00:00:00Z', True)]:
            with self.subTest(expiry=expiry):
                path.write_text(json.dumps({'branchRef': ref, 'expiresAt': expiry}))
                result, _ = self.observation(self.checksum())
                self.assertEqual(result.returncode == 0, accepted, result.stdout)
                self.assertTrue(path.is_file())
                self.assertEqual(self.command(self.target, 'git', 'rev-parse', ref).stdout.strip(),
                                 self.historical)

    def test_integrated_refs_do_not_hide_native_reservation(self):
        self.command(self.target, 'git', 'branch', 'ticket/003-historical', self.historical)
        (self.target / '.git/new-project-ticket-high-water').write_text('4\n')
        result, _ = self.observation(self.checksum())
        self.assertNotEqual(result.returncode, 0)

    def seed_scope(self, *paths):
        args = [sys.executable, '.governance/ticket_storage.py', 'scope', '--root', '.',
                '--workstream', 'governance']
        for path in paths:
            args += ['--path', path]
        return self.command(self.target, *args, check=False)

    def test_complete_seed_scope_allocates_without_ownership_takeover(self):
        receipt = json.loads(self.receipt.read_text())
        scope = sorted(receipt['files'])
        self.assertIn('VERSION', scope)
        manifest_path = self.target / '.governance/manifest.json'
        original_manifest = manifest_path.read_bytes()
        query = self.seed_scope(*scope)
        self.assertEqual(query.returncode, 0, query.stderr)
        args = ['bash', './project/new-ticket.sh', '--title', 'Complete first adoption',
                '--agent', 'fixture', '--workstream', 'governance',
                '--worktree-slug', 'complete-adoption',
                '--bootstrap-adoption-digest', self.checksum()]
        for path in scope:
            args += ['--path', path]
        result = self.command(self.target, *args)
        self.assertIn('Successfully allocated ' + self.expected_ticket, result.stdout)
        records = [json.loads(line) for line in result.stdout.splitlines() if line.startswith('{')]
        self.assertFalse(records[-1]['executionAuthorized'])
        wt = self.target / ('.worktrees/' + self.expected_ticket + '--complete-adoption')
        intent = json.loads((wt / 'project' / self.expected_ticket / 'intent.json').read_text())
        self.assertIn('VERSION', intent['allowedPaths'])
        self.assertFalse((wt / 'VERSION').exists(), 'allocation remains metadata only')
        self.assertEqual(manifest_path.read_bytes(), original_manifest)
        self.assertNotEqual(self.seed_scope('VERSION').returncode, 0,
                            'native reservation must end the bootstrap-only allowance')

    def test_seed_scope_rejects_foreign_wildcard_and_changed_required_file(self):
        for path in ['foreign.txt', '*', 'VERS*']:
            with self.subTest(path=path):
                self.assertNotEqual(self.seed_scope(path).returncode, 0)
        (self.target / 'VERSION').write_text('9.9.9\n')
        self.assertNotEqual(self.seed_scope('VERSION').returncode, 0)

    def test_seed_scope_rejects_unpublished_proof_and_explicit_shared_path(self):
        path = self.target / '.governance/manifest.lock.json'
        raw = path.read_bytes()
        lock = json.loads(raw)
        lock['standard']['publicationStatus'] = 'unpublished-test'
        path.write_text(json.dumps(lock))
        self.assertNotEqual(self.seed_scope('VERSION').returncode, 0)
        path.write_bytes(raw)
        path = self.target / '.governance/manifest.json'
        document = json.loads(path.read_text())
        document['coordination']['integration']['requiredForPaths'].append('VERSION')
        path.write_text(json.dumps(document))
        receipt = json.loads(self.receipt.read_text())
        receipt['files']['.governance/manifest.json'] = hashlib.sha256(path.read_bytes()).hexdigest()
        self.receipt.write_text(json.dumps(receipt))
        self.assertNotEqual(self.seed_scope('VERSION').returncode, 0)

    def test_protected_seed_scope_recomputes_base_and_immutable_package(self):
        # Load the actual checker; source authority is mocked only by fixture publication above.
        sys.path.insert(0, str(ROOT / 'scripts'))
        self.addCleanup(sys.path.remove, str(ROOT / 'scripts'))
        import governance_check as gate
        manifest = json.loads((self.target / '.governance/manifest.json').read_text())
        receipt = json.loads(self.receipt.read_text())
        intent = {'ticket': self.expected_ticket, 'workstream': 'governance',
                  'allowedPaths': sorted(receipt['files']), 'forbiddenPaths': [],
                  'delivery': {'acceptedBaseSha': self.head, 'standardAdoption': {
                      'sourceRepository': 'wellmanifest/new-project', 'fromRevision': None,
                      'toRevision': receipt['sourceRevision']}}}
        before = json.dumps(manifest, sort_keys=True)
        bindings = gate.atomic_adoption_binding_paths(self.target, manifest, intent)
        self.assertIn('VERSION', bindings)
        report = gate.Report(self.target)
        record = gate.TicketRecord(Path('project') / self.expected_ticket,
                                   'IN_PROGRESS', 'EDIT', intent, None)
        verified = gate.atomic_standard_adoption_paths(
            self.target, self.head, sorted(receipt['files']), [record], report)
        self.assertTrue(verified)
        gate.check_workstream_change_scope(self.target, manifest, [record],
            manifest['coordination'], record, sorted(receipt['files']), report)
        self.assertFalse(report.findings, report.findings)
        managed = self.target / '.governance/work_start_check.py'
        original = managed.read_bytes()
        managed.write_bytes(original + b'\n# changed candidate\n')
        denied = gate.Report(self.target)
        self.assertFalse(gate.atomic_standard_adoption_paths(
            self.target, self.head, sorted(receipt['files']), [record], denied))
        self.assertTrue(any(finding.code == 'GOV-SYNC-001' for finding in denied.findings))
        managed.write_bytes(original)
        self.assertEqual(json.dumps(manifest, sort_keys=True), before)
        intent['delivery']['acceptedBaseSha'] = 'f' * 40
        self.assertNotIn('VERSION', gate.atomic_adoption_binding_paths(self.target, manifest, intent))
        intent['delivery']['acceptedBaseSha'] = self.head
        intent['delivery']['standardAdoption']['fromRevision'] = 'a' * 40
        self.assertNotIn('VERSION', gate.atomic_adoption_binding_paths(self.target, manifest, intent))
        intent['delivery']['standardAdoption']['fromRevision'] = None
        path = self.target / '.governance/manifest.base.json'
        path.write_bytes(path.read_bytes() + b'\n')
        self.assertNotIn('VERSION', gate.atomic_adoption_binding_paths(self.target, manifest, intent))

    def test_protected_seed_scope_refuses_existing_seed_and_partial_native_base(self):
        sys.path.insert(0, str(ROOT / 'scripts'))
        self.addCleanup(sys.path.remove, str(ROOT / 'scripts'))
        import governance_check as gate
        manifest = json.loads((self.target / '.governance/manifest.json').read_text())
        revision = json.loads(self.receipt.read_text())['sourceRevision']
        hooks = self.base / 'fixture-no-hooks'
        hooks.mkdir()
        self.command(self.target, 'git', 'add', 'VERSION')
        self.command(self.target, 'git', '-c', f'core.hooksPath={hooks}', 'commit',
                     '--quiet', '--only', '-m', 'Existing version', '--', 'VERSION')
        existing = self.command(self.target, 'git', 'rev-parse', 'HEAD').stdout.strip()
        self.assertNotIn('VERSION', gate.initial_adoption_seed_paths(
            self.target, existing, revision, manifest))
        self.command(self.target, 'git', 'add', '.governance/manifest.lock.json')
        self.command(self.target, 'git', '-c', f'core.hooksPath={hooks}', 'commit',
                     '--quiet', '--only', '-m', 'Partial native metadata', '--',
                     '.governance/manifest.lock.json')
        existing = self.command(self.target, 'git', 'rev-parse', 'HEAD').stdout.strip()
        self.assertFalse(gate.initial_adoption_seed_paths(
            self.target, existing, revision, manifest))

    def test_seed_scope_rejects_symlink_and_executable_seed(self):
        path = self.target / 'VERSION'
        path.chmod(0o755)
        self.assertNotEqual(self.seed_scope('VERSION').returncode, 0)
        path.unlink()
        path.symlink_to(self.target / 'foreign.txt')
        self.assertNotEqual(self.seed_scope('VERSION').returncode, 0)

    def test_changed_installed_bytes_are_not_acknowledged(self):
        p = self.target / '.governance/manifest.json'
        p.write_text(p.read_text() + '\n')
        result, _ = self.observation(self.checksum())
        self.assertNotEqual(result.returncode, 0)

    def test_stale_observation_is_rejected(self):
        checksum = self.checksum()
        (self.target / 'foreign.txt').write_text('concurrent change\n')
        result, _ = self.observation(checksum)
        self.assertNotEqual(result.returncode, 0)

    def test_receipt_cannot_claim_foreign_path(self):
        receipt = json.loads(self.receipt.read_text())
        receipt['files']['foreign.txt'] = hashlib.sha256((self.target / 'foreign.txt').read_bytes()).hexdigest()
        self.receipt.write_text(json.dumps(receipt))
        result, _ = self.observation(self.checksum())
        self.assertNotEqual(result.returncode, 0)

    def test_overlapping_foreign_governance_change_still_blocks(self):
        (self.target / '.governance/foreign.json').write_text('{}\n')
        result, report = self.observation(self.checksum())
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(report['blockers'])

    def test_moved_head_is_rejected(self):
        no_hooks = self.base / 'fixture-no-hooks'
        no_hooks.mkdir()
        # Isolated malformed-state fixture; production hooks remain required.
        self.command(self.target, 'git', '-c', f'core.hooksPath={no_hooks}',
                     'commit', '--quiet', '--allow-empty', '-m', 'Another head')
        result, _ = self.observation(self.checksum())
        self.assertNotEqual(result.returncode, 0)

    def test_receipt_cannot_grant_writer_authority(self):
        receipt = json.loads(self.receipt.read_text())
        receipt['grantsWriterAuthority'] = True
        self.receipt.write_text(json.dumps(receipt))
        result, _ = self.observation(self.checksum())
        self.assertNotEqual(result.returncode, 0)

    def test_change_between_bootstrap_proof_and_entry_observation_is_rejected(self):
        checksum = self.checksum()
        spec = importlib.util.spec_from_file_location(
            'bootstrap_race_probe', self.target / '.governance/work_start_check.py')
        module = importlib.util.module_from_spec(spec)
        with patch.object(sys, 'path', [str(self.target / '.governance'), *sys.path]):
            spec.loader.exec_module(module)
        original = module.dirty_observation
        calls = 0

        def observed(root):
            nonlocal calls
            calls += 1
            if calls == 2:
                path = self.target / '.governance/manifest.json'
                path.write_text(path.read_text() + '\n')
            return original(root)

        with patch.object(module, 'dirty_observation', observed):
            with self.assertRaisesRegex(module.ObservationError, 'Bootstrap changed during admission'):
                module.inspect(self.target, 'governance', ['.governance/**'],
                               bootstrap_adoption_digest=checksum)

    def test_receipt_from_other_clone_is_rejected(self):
        receipt = json.loads(self.receipt.read_text())
        receipt['commonGitDir'] = str(self.source / '.git')
        self.receipt.write_text(json.dumps(receipt))
        result, _ = self.observation(self.checksum())
        self.assertNotEqual(result.returncode, 0)


class FreshBootstrapTest(BootstrapTest):
    fresh = True

    def test_duplicate_bootstrap_paths_keep_one_intent_and_matching_lease(self):
        if self.legacy_carriers:
            self.skipTest('legacy carrier recovery has a separate reservation path')
        receipt = json.loads(self.receipt.read_text())
        scope = sorted(receipt['files'])
        self.assertIn('TODO.md', scope)
        self.assertIn('project/TICKETS.md', scope)
        args = ['bash', './project/new-ticket.sh', '--title', 'Complete first adoption',
                '--agent', 'fixture', '--workstream', 'governance',
                '--worktree-slug', 'dedup-adoption',
                '--bootstrap-adoption-digest', self.checksum()]
        for path in scope:
            args += ['--path', path]
        args += ['--path', 'TODO.md', '--path', 'project/TICKETS.md']
        result = self.command(self.target, *args)
        self.assertIn('Successfully allocated ' + self.expected_ticket, result.stdout)
        wt = self.target / ('.worktrees/' + self.expected_ticket + '--dedup-adoption')
        intent = json.loads((wt / 'project' / self.expected_ticket / 'intent.json').read_text())
        expected = list(dict.fromkeys([f'project/{self.expected_ticket}/**',
                                       'TODO.md', 'project/TICKETS.md', *scope]))
        self.assertEqual(intent['allowedPaths'], expected)
        lease = json.loads((self.target / '.subactor/leases' /
                            (self.expected_ticket + '--dedup-adoption.json')).read_text())
        canonical = json.dumps(expected, sort_keys=True, separators=(',', ':')).encode()
        self.assertEqual(lease['scopeHash'], hashlib.sha256(canonical).hexdigest())
        manifest = json.loads((self.target / '.governance/manifest.json').read_text())
        owned = manifest['coordination']['workstreams']['governance']['ownedPaths']
        self.assertIn('.gitattributes', owned)
        self.assertIn('.github/workflows/new-project-branch-hygiene.yml', owned)

    def test_fresh_receipt_records_absent_original_governance(self):
        receipt = json.loads(self.receipt.read_text())
        self.assertEqual(receipt['bootstrapKind'], 'fresh')
        self.assertFalse(receipt['grantsWriterAuthority'])
        self.assertFalse(receipt['grantsPublicationAuthority'])
        result, _ = self.observation(self.checksum())
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_unknown_bootstrap_kind_is_rejected(self):
        receipt = json.loads(self.receipt.read_text())
        receipt['bootstrapKind'] = 'unrestricted'
        self.receipt.write_text(json.dumps(receipt))
        result, _ = self.observation(self.checksum())
        self.assertNotEqual(result.returncode, 0)


class FreshLegacyBootstrapTest(FreshBootstrapTest):
    legacy_carriers = True
    expected_ticket = 'ticket-008'

    def test_historical_carriers_are_preserved_without_activity_claim(self):
        before = {p.name: p.read_bytes() for p in (self.target / 'project/ticket-007').iterdir()}
        self.test_first_real_allocator_preserves_foreign_bytes_and_does_not_write_source()
        after = {p.name: p.read_bytes() for p in (self.target / 'project/ticket-007').iterdir()}
        self.assertEqual(before, after)
        self.assertIn(b'IN_PROGRESS', after['README.md'])

    def test_modified_historical_carrier_is_refused(self):
        (self.target / 'project/ticket-007/README.md').write_text('unfinished changes\n')
        result, _ = self.observation(self.checksum())
        self.assertNotEqual(result.returncode, 0)

    def test_missing_historical_carrier_is_refused(self):
        (self.target / 'project/ticket-007/intent.json').unlink()
        result, _ = self.observation(self.checksum())
        self.assertNotEqual(result.returncode, 0)

    def test_untracked_carrier_is_refused(self):
        (self.target / 'project/ticket-007/extra.md').write_text('unknown owner\n')
        result, _ = self.observation(self.checksum())
        self.assertNotEqual(result.returncode, 0)

    def test_symlinked_carrier_is_refused(self):
        p = self.target / 'project/ticket-007/README.md'
        p.unlink()
        p.symlink_to(self.target / 'foreign.txt')
        result, _ = self.observation(self.checksum())
        self.assertNotEqual(result.returncode, 0)

    def test_live_ticket_branch_is_refused(self):
        self.command(self.target, 'git', 'branch', 'ticket/008-other-writer')
        result, _ = self.observation(self.checksum())
        self.assertNotEqual(result.returncode, 0)

    def test_prior_allocation_reservation_is_refused(self):
        (self.target / '.git/new-project-ticket-high-water').write_text('8\n')
        result, _ = self.observation(self.checksum())
        self.assertNotEqual(result.returncode, 0)


class HistoricalRefObservationTest(unittest.TestCase):
    """Exercise the actual source against real Git, including error outcomes."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.git('init', '--quiet', '-b', 'main')
        self.git('config', 'user.name', 'Fixture')
        self.git('config', 'user.email', 'fixture@example.invalid')
        self.git('commit', '--quiet', '--allow-empty', '-m', 'Historical')
        self.old = self.git('rev-parse', 'HEAD')
        self.git('commit', '--quiet', '--allow-empty', '-m', 'Accepted base')
        self.head = self.git('rev-parse', 'HEAD')
        self.ref = 'refs/heads/ticket/003-historical'
        self.git('update-ref', self.ref, self.old)
        spec = importlib.util.spec_from_file_location('actual_bootstrap_guard',
                                                     ROOT / 'scripts/work_start_check.py')
        self.guard = importlib.util.module_from_spec(spec)
        with patch.object(sys, 'path', [str(ROOT / 'scripts'), *sys.path]):
            spec.loader.exec_module(self.guard)

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.root), *args],
                                       text=True, stderr=subprocess.PIPE).strip()

    def test_preserves_strict_ancestors_and_rejects_ambiguous_or_unreadable_refs(self):
        self.assertIn(self.ref, self.guard.bootstrap_historical_refs(self.root, self.head))
        self.assertEqual(self.git('rev-parse', self.ref), self.old)
        for sha in (self.head, 'f' * 40):
            with self.subTest(sha=sha):
                path = self.root / '.git' / self.ref
                path.write_text(sha + '\n')
                with self.assertRaises(self.guard.ObservationError):
                    self.guard.bootstrap_historical_refs(self.root, self.head)

    def test_shallow_history_and_symlinked_lease_directory_are_refused(self):
        shallow = self.root / '.git/shallow'
        shallow.write_text(self.head + '\n')
        with self.assertRaisesRegex(self.guard.ObservationError, 'incomplete'):
            self.guard.bootstrap_historical_refs(self.root, self.head)
        shallow.unlink()
        (self.root / '.subactor').mkdir()
        (self.root / '.subactor/leases').symlink_to(self.root / '.git', target_is_directory=True)
        with self.assertRaisesRegex(self.guard.ObservationError, 'lease observation'):
            self.guard.bootstrap_historical_refs(self.root, self.head)

    def test_lease_ambiguity_blocks_and_expired_evidence_is_preserved(self):
        path = self.root / '.subactor/leases/ticket-003--historical.json'
        path.parent.mkdir(parents=True)
        for expiry in (None, 'invalid', '2099-01-01T00:00:00Z', '2000-01-01T00:00:00'):
            with self.subTest(expiry=expiry):
                path.write_text(json.dumps({'branchRef': self.ref, 'expiresAt': expiry}))
                with self.assertRaises(self.guard.ObservationError):
                    self.guard.bootstrap_historical_refs(self.root, self.head)
        path.write_text(json.dumps({'branchRef': self.ref, 'expiresAt': '2000-01-01T00:00:00Z'}))
        before = path.read_bytes()
        self.assertIn(self.ref, self.guard.bootstrap_historical_refs(self.root, self.head))
        self.assertEqual(path.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
