#!/usr/bin/env python3
"""Real Git migration fixtures, isolated from developer repositories and grants."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / 'scripts'))
import snapshot_migration as migration
import governance_check as governance


class MigrationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.outer = Path(self.temporary.name)
        self.root = self.outer / 'repo'
        self.root.mkdir()
        self.environment = {**os.environ, 'GIT_AUTHOR_NAME': 'Fixture', 'GIT_AUTHOR_EMAIL': 'fixture@example.invalid',
                            'GIT_COMMITTER_NAME': 'Fixture', 'GIT_COMMITTER_EMAIL': 'fixture@example.invalid'}
        self.git('init', '-b', 'main')
        (self.root / 'base.txt').write_text('preserved base\n')
        self.base = self.make_commit([], 'base')
        self.git('update-ref', 'refs/heads/main', self.base)
        self.git('checkout', '-b', 'source')
        for index in range(20):
            (self.root / f'file-{index:02}.py').write_text(f'value = {index}\n')
        legacy = self.root / 'project/ticket-099'
        legacy.mkdir(parents=True)
        (legacy / 'README.md').write_text('# Original ticket\n')
        (legacy / 'intent.json').write_text('{"ticket":"ticket-099"}')
        self.source = self.make_commit([self.base], 'original snapshot')
        self.git('update-ref', 'refs/heads/source', self.source)
        self.branch = 'ticket/001-migration'
        self.git('checkout', '-b', self.branch, self.base)
        observed = migration.inventory(self.root, self.base, self.source)
        self.contract = {'schema': migration.CONTRACT_SCHEMA, 'repository': 'fixture/product',
                         'baseSha': self.base, 'sourceSha': self.source, 'sourceTree': observed['sourceTree'],
                         'inventorySha256': observed['inventorySha256'], 'authorizationRef': 'authorization:fixture/migration-1'}
        self.intent = {'ticket': 'ticket-001', 'delivery': {'acceptedBaseSha': self.base, 'targetBranch': 'main',
                                                          'snapshotMigration': self.contract}}
        self.grant_path = self.outer / 'authorization.json'
        self.authorize()
        self.git('read-tree', '--reset', '-u', self.source)
        ticket = self.root / 'project/ticket-001'
        ticket.mkdir(parents=True)
        (ticket / 'README.md').write_text('# Fixture migration\n')
        self.write_intent()
        self.boundary = self.make_commit([self.base, self.source], 'one migration with original source parent')
        self.git('update-ref', 'refs/heads/' + self.branch, self.boundary)

    def git(self, *arguments):
        return subprocess.check_output(['git', '-C', str(self.root), *arguments], env=self.environment,
                                       stderr=subprocess.PIPE).decode().strip()

    def make_commit(self, parents, message):
        self.git('add', '-A')
        tree = self.git('write-tree')
        arguments = ['commit-tree', tree, '-m', message]
        for parent in parents:
            arguments += ['-p', parent]
        return self.git(*arguments)

    def write_intent(self):
        (self.root / 'project/ticket-001/intent.json').write_text(json.dumps(self.intent))

    def authorize(self, **overrides):
        self.grant = {'schema': migration.AUTHORIZATION_SCHEMA, 'grantId': self.contract['authorizationRef'],
                      'repository': 'fixture/product', 'ticket': 'ticket-001', 'branch': self.branch,
                      'targetBranch': 'main', 'baseSha': self.base, 'contractSha256': migration.digest(self.contract),
                      'intentSha256': migration.digest(self.intent),
                      'implementationPaths': [f'file-{i:02}.py' for i in range(20)], 'historicalTickets': ['ticket-099'], 'maxUses': 1, 'status': 'reserved',
                      **overrides}
        raw = json.dumps(self.grant, sort_keys=True).encode()
        self.grant_path.write_bytes(raw)
        self.grant_sha = hashlib.sha256(raw).hexdigest()

    def prove(self, **overrides):
        arguments = dict(base=self.base, head='HEAD', repository='fixture/product', branch=self.branch,
                         authorization_path=self.grant_path, authorization_sha256=self.grant_sha)
        arguments.update(overrides)
        return migration.prove(self.root, self.intent, **arguments)

    def assert_rejected(self, **overrides):
        with self.assertRaises(migration.MigrationError):
            self.prove(**overrides)

    def test_exact_inventory_preserves_history_and_does_not_mutate(self):
        before = self.git('status', '--porcelain=v1', '--untracked-files=all')
        refs = self.git('show-ref')
        proof = self.prove()
        self.assertEqual(proof['migrationCommit'], self.boundary)
        self.assertEqual(proof['unchangedImportedFiles'], 20)
        self.assertEqual(proof['authority'], 'VALIDATION_ONLY')
        self.assertEqual(self.git('status', '--porcelain=v1', '--untracked-files=all'), before)
        self.assertEqual(self.git('show-ref'), refs)
        self.assertEqual(self.git('rev-parse', 'source'), self.source)

    def test_missing_pin_modified_grant_and_checkout_owned_grant_fail(self):
        self.assert_rejected(authorization_path=None)
        self.assert_rejected(authorization_sha256='0' * 64)
        inside = self.root / 'candidate-grant.json'
        inside.write_bytes(self.grant_path.read_bytes())
        self.assert_rejected(authorization_path=inside)
        self.grant_path.write_text('{}')
        self.assert_rejected()

    def test_external_symlink_and_duplicate_keys_fail(self):
        linked = self.outer / 'symlink.json'
        linked.symlink_to(self.grant_path)
        self.assert_rejected(authorization_path=linked)
        raw = self.grant_path.read_text().replace('{', '{"maxUses":1,', 1).encode()
        self.grant_path.write_bytes(raw)
        self.assert_rejected(authorization_sha256=hashlib.sha256(raw).hexdigest())

    def test_foreign_repository_branch_and_intent_fail(self):
        self.assert_rejected(repository='foreign/product')
        self.assert_rejected(branch='ticket/002-migration')
        self.intent['unapproved'] = True
        self.assert_rejected()

    def test_consumed_grant_and_moved_base_fail(self):
        self.authorize(status='consumed')
        self.assert_rejected()
        self.authorize()
        self.assert_rejected(base=self.boundary)

    def test_wrong_tree_inventory_or_source_fail(self):
        for field in ('sourceTree', 'inventorySha256', 'sourceSha'):
            original = self.contract[field]
            self.contract[field] = '0' * len(original)
            self.authorize()
            self.assert_rejected()
            self.contract[field] = original

    def test_squashed_source_cannot_claim_preserved_history(self):
        squashed = self.make_commit([self.base], 'same tree but lost original history')
        self.git('update-ref', 'refs/heads/' + self.branch, squashed)
        self.assert_rejected()

    def test_extra_file_in_import_is_not_hidden_by_matching_final_tree(self):
        (self.root / 'unapproved.py').write_text('extra = True\n')
        invalid = self.make_commit([self.base, self.source], 'unapproved extra import file')
        self.git('update-ref', 'refs/heads/' + self.branch, invalid)
        self.assert_rejected()

    def test_intent_cannot_be_added_after_import(self):
        self.git('read-tree', '--reset', '-u', self.source)
        invalid = self.make_commit([self.base, self.source], 'import without new intent')
        self.git('update-ref', 'refs/heads/' + self.branch, invalid)
        self.assert_rejected()

    def test_unrelated_authorized_inventory_entry_fails(self):
        self.authorize(implementationPaths=['base.txt', *self.grant['implementationPaths']])
        self.assert_rejected()

    def test_uncommitted_and_committed_repairs_use_ordinary_budget(self):
        target = self.root / 'file-00.py'
        target.write_text('value = 100\n')
        proof = self.prove()
        self.assertNotIn('file-00.py', proof['importedPaths'])
        self.assertIn('file-00.py', proof['repairPaths'])
        head = self.make_commit([self.boundary], 'separate ordinary repair')
        self.git('update-ref', 'refs/heads/' + self.branch, head)
        self.assertEqual(self.prove()['unchangedImportedFiles'], 19)
        delivery = {'budgets': {'maxImplementationFiles': 1, 'maxAffectedComponents': 1, 'maxPublicInterfaceChanges': 0},
                    'runtimeDependencies': []}
        limits = {'maxImplementationFiles': 1, 'publicInterfacePaths': [], 'dependencyManifestPaths': []}
        record = governance.TicketRecord(self.root / 'project/ticket-001', 'IN_PROGRESS', 'EDIT', self.intent, None)
        report = governance.Report(self.root)
        report.snapshot_migrations = {'ticket-001': self.prove()}
        governance.check_actual_delivery_budget(limits, delivery, record, self.grant['implementationPaths'], {'app'}, False, False, report)
        self.assertFalse(report.findings)
        (self.root / 'file-01.py').write_text('value = 101\n')
        report.snapshot_migrations = {'ticket-001': self.prove()}
        governance.check_actual_delivery_budget(limits, delivery, record, self.grant['implementationPaths'], {'app'}, False, False, report)
        self.assertTrue(any(item.code == 'GOV-BUDGET-001' for item in report.findings))

    def test_reverting_an_import_to_base_still_counts_as_repair(self):
        (self.root / 'file-00.py').unlink()
        head = self.make_commit([self.boundary], 'remove one imported file')
        self.git('update-ref', 'refs/heads/' + self.branch, head)
        proof = self.prove()
        self.assertIn('file-00.py', proof['repairPaths'])
        self.assertNotIn('file-00.py', proof['importedPaths'])

    def test_only_verified_source_history_is_excluded(self):
        report = governance.Report(self.root)
        governance.check_history_order(self.root, self.base, 'HEAD', 'ticket-001', 'project', 'intent.json', ['project/**'], report)
        self.assertTrue(any(item.code == 'GOV-INTENT-003' for item in report.findings))
        accepted = governance.Report(self.root)
        accepted.snapshot_migrations = {'ticket-001': self.prove()}
        governance.check_history_order(self.root, self.base, 'HEAD', 'ticket-001', 'project', 'intent.json', ['project/**'], accepted)
        self.assertFalse(accepted.findings)

    def test_historical_tickets_are_explicit_and_must_remain_unchanged(self):
        self.assertEqual(self.prove()['historicalTickets'], ['ticket-099'])
        (self.root / 'project/ticket-099/README.md').write_text('# Changed old ticket\n')
        self.assert_rejected()

    def test_old_migration_metadata_does_not_require_a_grant_for_new_work(self):
        from types import SimpleNamespace
        record = governance.TicketRecord(self.root / 'project/ticket-001', 'IN_PROGRESS', 'EDIT', self.intent, None)
        report = governance.Report(self.root)
        args = SimpleNamespace(migration_authorization=None)
        historical, repairs = governance.prepare_snapshot_migrations(
            args, self.root, [record], self.base, ['another.py'], report)
        self.assertFalse(historical or repairs or report.findings)
        self.assertFalse(report.snapshot_migrations)

    def test_ordinary_budget_has_no_implicit_migration_exception(self):
        report = governance.Report(self.root)
        delivery = {'budgets': {'maxImplementationFiles': 1, 'maxAffectedComponents': 1, 'maxPublicInterfaceChanges': 0},
                    'runtimeDependencies': []}
        record = governance.TicketRecord(self.root / 'project/ticket-001', 'IN_PROGRESS', 'EDIT', self.intent, None)
        limits = {'maxImplementationFiles': 1, 'publicInterfacePaths': [], 'dependencyManifestPaths': []}
        governance.check_actual_delivery_budget(limits, delivery, record, self.grant['implementationPaths'], {'app'}, False, False, report)
        self.assertTrue(any(item.code == 'GOV-BUDGET-001' for item in report.findings))


if __name__ == '__main__':
    unittest.main()
