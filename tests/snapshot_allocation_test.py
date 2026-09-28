#!/usr/bin/env python3
"""Disposable real Git/controller snapshot allocation regressions."""
from datetime import datetime, timedelta, timezone
import importlib.util
import hashlib
import json
import multiprocessing
import os
from pathlib import Path
import shutil
import subprocess
import sys
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import snapshot_allocation as allocation
import snapshot_migration as migration
import work_start_check as start

spec = importlib.util.spec_from_file_location('allocation_fixtures', ROOT / 'tests/work_start_test.py')
fixtures = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixtures)


def reserve_process(root, request, connection):
    try:
        connection.send(('ok', allocation.prepare(Path(root), Path(request), 'api')['ticket']))
    except (OSError, ValueError):
        connection.send(('busy', None))
    finally:
        connection.close()


class AllocationTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.WorkStartTest()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.root = self.fixture.root
        self.git = lambda *args: self.fixture.git(self.root, *args)
        self.outer = Path(self.fixture.temp.name)
        self.git('remote', 'add', 'origin', 'https://github.com/example/project.git')
        for name in ('snapshot_allocation.py', 'snapshot_migration.py', 'ticket_recovery.py', 'ticket_allocation.py'):
            shutil.copy2(ROOT / 'scripts' / name, self.root / '.governance' / name)
        self.git('add', '.')
        self.git('commit', '-m', 'managed fixture helpers')
        self.base = self.git('rev-parse', 'HEAD')
        self.git('update-ref', 'refs/remotes/origin/main', self.base)
        (self.root / 'api/a.txt').write_text('pre-adoption source\n')
        (self.root / 'ui/a.txt').write_text('imported outside repair ownership\n')
        self.git('commit', '-am', 'preserved bootstrap')
        self.source = self.git('rev-parse', 'HEAD')
        self.template = {
            'schema': 'new-project.intent/v3', 'summary': 'Preserve source',
            'classification': {'kind': 'BUG', 'priority': 'P1', 'origin': 'health'},
            'workstream': 'api', 'allowedPaths': ['api/**'], 'forbiddenPaths': ['project/ticket-*/user-*.md'],
            'stacks': [], 'dependsOn': [], 'conflictsWith': [], 'integrationTicket': None,
            'delivery': {'acceptedBaseSha': self.base, 'targetBranch': 'main', 'outcome': 'Preserve source history',
                'nonGoals': ['Protected merge approval'], 'complexity': 'S', 'estimatedMinutes': 15,
                'budgets': {'maxImplementationFiles': 5, 'maxAffectedComponents': 1, 'maxPublicInterfaceChanges': 0, 'maxRuntimeDependencies': 0},
                'architecture': {'status': 'accepted', 'decision': 'Preserve original sources',
                    'components': [{'name': 'api', 'paths': ['api/**']}], 'responsibilityChanges': False,
                    'interfaceChanges': [], 'dataChanges': [], 'ui': {'impact': 'none', 'states': [], 'evidence': []}, 'rollback': 'Preserve source refs'},
                'runtimeDependencies': [], 'validation': [{'criterion': 'AC-01', 'commands': ['true'], 'evidence': 'Isolated fixture'}]}}
        self.request = {'schema': allocation.REQUEST_SCHEMA, 'requestId': 'fixture/recovery', 'repository': 'example/project',
            'baseSha': self.base, 'sourceSha': self.source, 'targetBranch': 'main', 'slug': 'migration', 'intentTemplate': self.template}
        self.request_path = self.outer / 'proposal-request.json'
        self.persist()

    def persist(self):
        self.request_path.write_text(json.dumps(self.request))

    def prepare(self):
        self.persist()
        return allocation.prepare(self.root, self.request_path, 'api')

    def authority(self):
        self.proposal = self.prepare()
        intent = self.proposal['intent']
        contract = intent['delivery']['snapshotMigration']
        self.grant = {'schema': migration.AUTHORIZATION_SCHEMA, 'grantId': contract['authorizationRef'],
            'repository': 'example/project', 'ticket': intent['ticket'], 'branch': self.proposal['layout']['branch'],
            'targetBranch': 'main', 'baseSha': self.base, 'contractSha256': migration.digest(contract), 'intentSha256': migration.digest(intent),
            'implementationPaths': ['api/a.txt', 'ui/a.txt'], 'historicalTickets': [], 'maxUses': 1, 'status': 'reserved'}
        self.grant_path = self.outer / 'grant.json'
        self.grant_path.write_text(json.dumps(self.grant))
        self.grant_sha = allocation.raw_digest(self.grant_path)
        self.store = self.outer / 'controller'
        self.store.mkdir()
        (self.store / '.lock').touch()
        self.material = {'schema': allocation.MATERIAL_SCHEMA, 'proposalPath': self.proposal['proposalPath'],
            'proposalSha256': self.proposal['proposalSha256'], 'leaseId': 'fixture-lease', 'leaseRevision': 2, 'fencingToken': 7,
            'ownerActor': 'fixture', 'ownerSession': 'fixture-session'}
        self.lease = {'schema': 'wellmanifest.change-lease/v1', 'leaseId': 'fixture-lease', 'leaseRevision': 2,
            'fencingToken': 7, 'ownerActor': 'fixture', 'ownerSession': 'fixture-session', 'repositoryRef': 'example/project',
            'ticketId': intent['ticket'], 'targetBranch': 'main', 'branchRef': 'refs/heads/' + self.proposal['layout']['branch'],
            'workstream': 'api', 'worktreeId': Path(self.proposal['layout']['worktreePath']).name,
            'scopeHash': start.digest(intent['allowedPaths']), 'planHash': hashlib.sha256(allocation.intent_bytes(intent)).hexdigest(),
            'phase': 'editing', 'publicationFrozen': False, 'expiresAt': (datetime.now(timezone.utc) + timedelta(minutes=10)).isoformat()}
        self.resource = start.digest({'repositoryRef': 'example/project', 'targetBranch': 'main'})
        self.state = {'schema': 'subactor.repository-change-lease-store/v1', 'leases': {'fixture-lease': self.lease}, 'active': {self.resource: 'fixture-lease'}}
        self.material_path = self.outer / 'material.json'
        self.persist_authority()

    def persist_authority(self):
        self.material_path.write_text(json.dumps(self.material))
        (self.store / 'state.json').write_text(json.dumps(self.state))

    def materialize(self):
        self.persist_authority()
        return allocation.materialize(self.root, self.material_path, self.store, self.grant_path, self.grant_sha, 'api')

    def test_proposal_reserves_only_identity_and_is_exactly_idempotent(self):
        refs = self.git('show-ref')
        dirty = self.git('status', '--porcelain=v1')
        first = self.prepare()
        self.assertEqual(self.prepare(), first)
        self.assertFalse(first['grantsAuthority'])
        self.assertEqual(self.git('show-ref'), refs)
        self.assertEqual(self.git('status', '--porcelain=v1'), dirty)
        self.assertFalse(Path(first['layout']['worktreePath']).exists())
        self.request['intentTemplate']['summary'] = 'Changed same request'
        with self.assertRaises(ValueError):
            self.prepare()

    def test_allocator_cli_routes_proposal_without_authority(self):
        result = subprocess.run(['bash', 'project/new-ticket.sh', '--workstream', 'api', '--snapshot-proposal', str(self.request_path)], cwd=self.root, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(json.loads(result.stdout)['grantsAuthority'])

    def test_two_process_reservation_never_duplicates_and_readback_agrees(self):
        ctx = multiprocessing.get_context('fork')
        pipes = [ctx.Pipe(False) for _ in range(2)]
        children = [ctx.Process(target=reserve_process, args=(str(self.root), str(self.request_path), pipe[1])) for pipe in pipes]
        for child in children:
            child.start()
        results = [pipe[0].recv() for pipe in pipes]
        for child in children:
            child.join(10)
            self.assertEqual(child.exitcode, 0)
        tickets = {ticket for status, ticket in results if status == 'ok'}
        self.assertEqual(len(tickets), 1)
        self.assertIn(self.prepare()['ticket'], tickets)

    def test_declared_repair_scope_is_not_an_import_ownership_exception(self):
        self.template['allowedPaths'] += ['ui/**']
        with self.assertRaises(ValueError):
            self.prepare()

    def test_reserved_identity_is_not_reused_by_ordinary_allocator(self):
        proposal = self.prepare()
        (self.root / '.git/new-project-ticket-high-water').write_text('2\n')
        self.request['requestId'] = 'different-request'
        self.request['slug'] = 'second'
        later = self.prepare()
        self.assertEqual(later['ticket'], 'ticket-003')
        self.assertNotEqual(later['ticket'], proposal['ticket'])

    def test_source_preservation_and_exact_two_parent_candidate(self):
        self.authority()
        refs = self.git('show-ref')
        primary = start.dirty_observation(self.root)
        # Isolate filesystem/controller transport from the governance gate,
        # whose policy acceptance/rejections are covered by migration tests.
        with patch.object(allocation, 'validate_candidate') as validate:
            result = self.materialize()
        candidate = Path(result['worktree'])
        self.assertFalse(result['grantsMergeAuthority'])
        self.assertEqual(self.git('rev-parse', 'main'), self.source)
        self.assertEqual(start.dirty_observation(self.root), primary)
        self.assertEqual(self.fixture.git(candidate, 'show', '-s', '--format=%P', 'HEAD'), self.base + ' ' + self.source)
        self.assertEqual((candidate / 'ui/a.txt').read_bytes(), (self.root / 'ui/a.txt').read_bytes())
        for line in refs.splitlines():
            sha, ref = line.split()
            self.assertEqual(self.git('rev-parse', ref), sha)
        validate.assert_called_once()
        self.assertEqual(allocation.load(Path(self.proposal['layout']['leasePath'])), self.lease)
        with self.assertRaises(ValueError):
            self.materialize()

    def test_failed_full_gate_preserves_detached_candidate_without_branch(self):
        self.authority()
        with patch.object(allocation.governance, 'main', return_value=1):
            with self.assertRaises(ValueError):
                self.materialize()
        candidate = Path(self.proposal['layout']['worktreePath'])
        self.assertTrue(candidate.exists())
        self.assertEqual(self.fixture.git(candidate, 'show', '-s', '--format=%P', 'HEAD'), self.base + ' ' + self.source)
        self.assertEqual((candidate / 'ui/a.txt').read_bytes(), (self.root / 'ui/a.txt').read_bytes())
        self.assertFalse(allocation.load(candidate / 'project' / self.proposal['ticket'] / 'intent.json').get('grantsAuthority', False))
        self.assertFalse(start.git(self.root, 'show-ref', '--verify', 'refs/heads/' + self.proposal['layout']['branch'], optional=True))
        self.assertEqual(self.git('rev-parse', 'main'), self.source)

    def test_grant_pin_and_lease_cas_failure_have_no_checkout_effect(self):
        self.authority()
        for field, value in [('leaseRevision', 3), ('fencingToken', 8), ('ownerSession', 'other'), ('planHash', '0' * 64), ('expiresAt', '2020-01-01T00:00:00Z')]:
            with self.subTest(field=field):
                previous = self.lease[field]
                self.lease[field] = value
                with self.assertRaises(ValueError):
                    self.materialize()
                self.lease[field] = previous
                self.assertFalse(Path(self.proposal['layout']['worktreePath']).exists())
        self.grant_sha = '0' * 64
        with self.assertRaises(ValueError):
            self.materialize()
        self.assertFalse(Path(self.proposal['layout']['worktreePath']).exists())

    def test_peer_dirty_or_reserved_repair_is_not_covered_by_import_grant(self):
        self.authority()
        (self.root / 'api/a.txt').write_text('concurrent local edit\n')
        with self.assertRaises(ValueError):
            self.materialize()
        self.assertFalse(Path(self.proposal['layout']['worktreePath']).exists())

    def test_target_movement_and_unsafe_authority_paths_fail(self):
        self.authority()
        self.git('update-ref', 'refs/remotes/origin/main', self.source)
        with self.assertRaises(ValueError):
            self.materialize()
        self.git('update-ref', 'refs/remotes/origin/main', self.base)
        linked = self.outer / 'linked-grant.json'
        linked.symlink_to(self.grant_path)
        self.grant_path = linked
        with self.assertRaises(ValueError):
            self.materialize()

    def full_gate_fixture(self):
        # Build a complete hub-policy baseline, then preserve a fresh source.
        # The transport tests above intentionally use a minimal admission fixture.
        (self.root / '.governance/manifest.json').unlink()
        manifest = json.loads((ROOT / 'governance/manifest.hub.json').read_text())
        manifest['coordination']['workstreams']['api'] = {'ownedPaths': ['api/**']}
        governance = self.root / 'governance'
        governance.mkdir()
        (governance / 'manifest.hub.json').write_text(json.dumps(manifest))
        for name in ('stack-profiles.json', 'work-classification.dsl.json'):
            shutil.copy2(ROOT / 'governance' / name, governance / name)
        for name in manifest['requiredFiles']:
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            if not path.exists():
                path.write_text('Fixture baseline\n')
        (self.root / 'VERSION').write_text(manifest['standard']['version'] + '\n')
        self.git('add', '.')
        self.git('commit', '-m', 'complete governed baseline')
        self.base = self.git('rev-parse', 'HEAD')
        self.git('update-ref', 'refs/remotes/origin/main', self.base)
        (self.root / 'api/a.txt').write_text('approved API snapshot\n')
        (self.root / 'ui/a.txt').write_text('approved UI snapshot\n')
        self.git('commit', '-am', 'exact preserved snapshot')
        self.source = self.git('rev-parse', 'HEAD')
        self.request.update(baseSha=self.base, sourceSha=self.source)
        self.template['delivery']['acceptedBaseSha'] = self.base

    def test_full_unpatched_gate_accepts_exact_import_without_repair_ownership(self):
        self.full_gate_fixture()
        self.authority()
        result = self.materialize()
        candidate = Path(result['worktree'])
        proof = migration.prove(candidate, self.proposal['intent'], base=self.base,
            head=result['headSha'], repository='example/project', branch=result['branch'],
            authorization_path=self.grant_path, authorization_sha256=self.grant_sha)
        self.assertEqual(proof['importedPaths'], ['api/a.txt', 'ui/a.txt'])
        self.assertEqual(self.git('rev-parse', 'main'), self.source)
        self.assertEqual(self.fixture.git(candidate, 'symbolic-ref', 'HEAD'), 'refs/heads/' + result['branch'])

    def test_installed_allocator_does_not_execute_candidate_helper(self):
        for name in ('snapshot_allocation.py', 'ticket_allocation.py', 'worktree_path_check.py'):
            (self.root / '.governance' / name).write_text("raise RuntimeError('candidate executable')\n")
        shutil.copy2(ROOT / 'governance/ticket-allocation.json', self.root / '.governance/ticket-allocation.json')
        result = subprocess.run(['bash', str(ROOT / 'project/new-ticket.sh'), '--workstream', 'api',
            '--snapshot-proposal', str(self.request_path)], cwd=self.root, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(json.loads(result.stdout)['grantsAuthority'])

    def test_plan_change_during_validation_stops_branch_publication(self):
        self.authority()
        def race(*args):
            self.lease['planHash'] = '0' * 64
            self.persist_authority()
        with patch.object(allocation, 'validate_candidate', side_effect=race):
            with self.assertRaisesRegex(ValueError, 'Controller plan changed'):
                self.materialize()
        self.assertFalse(start.git(self.root, 'show-ref', '--verify', 'refs/heads/' + self.proposal['layout']['branch'], optional=True))

    def test_branch_change_during_admission_stops_checkout_creation(self):
        self.authority()
        original = allocation.admit
        def race(*args):
            result = original(*args)
            self.git('update-ref', 'refs/heads/unregistered-concurrent', self.source)
            return result
        with patch.object(allocation, 'admit', side_effect=race):
            with self.assertRaisesRegex(ValueError, 'Refs changed during admission'):
                self.materialize()
        self.assertFalse(Path(self.proposal['layout']['worktreePath']).exists())

    def test_legacy_ticket_branch_identity_is_not_reused(self):
        self.git('branch', 'ticket-009-legacy')
        self.assertEqual(self.prepare()['ticket'], 'ticket-010')

    def test_peer_change_during_validation_stops_branch_publication(self):
        self.authority()
        def race(*args):
            (self.root / 'api/a.txt').write_text('late concurrent edit\n')
        with patch.object(allocation, 'validate_candidate', side_effect=race):
            with self.assertRaises(ValueError):
                self.materialize()
        self.assertFalse(start.git(self.root, 'show-ref', '--verify', 'refs/heads/' + self.proposal['layout']['branch'], optional=True))
        self.assertEqual((self.root / 'api/a.txt').read_text(), 'late concurrent edit\n')


if __name__ == '__main__':
    unittest.main()
