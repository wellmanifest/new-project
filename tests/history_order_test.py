"""Real Git regressions for material history and inherited baseline payloads."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / 'scripts'))
import governance_check as governance


class HistoryOrderTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='history-order-')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.git('init', '-q', '-b', 'main')
        self.git('config', 'user.name', 'history-fixture')
        self.git('config', 'user.email', 'history@example.invalid')
        self.git('config', 'commit.gpgsign', 'false')
        self.git('config', 'core.filemode', 'false')
        self.write('payload.txt', 'before\n')
        self.base = self.commit('baseline')

    def git(self, *args, check=True):
        result = subprocess.run(['git', *args], check=False, cwd=self.root, capture_output=True, text=True)
        if check and result.returncode:
            self.fail(f'Git fixture command failed: {args!r}: {result.stderr}')
        return result

    def write(self, name, value):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(value)

    def intent(self):
        self.write('project/ticket-001/intent.json', json.dumps({
            'schema': 'new-project.intent/v3',
            'ticket': 'ticket-001',
            'summary': 'History order test fixture',
            'workstream': 'governance',
            'classification': {'kind': 'BUG', 'priority': 'P1', 'origin': 'health'},
            'allowedPaths': ['project/ticket-001/**', 'payload.txt', 'operator.md', 'temporary.py', 'imported.py'],
            'forbiddenPaths': ['project/ticket-*/user-*.md'],
            'stacks': [],
            'dependsOn': [],
            'conflictsWith': [],
            'integrationTicket': None,
        }))

    def commit(self, message, stage=True):
        if stage:
            self.git('add', '-A')
        self.git('commit', '-qm', message)
        return self.git('rev-parse', 'HEAD').stdout.strip()

    def inspect(self, head='HEAD', migration_source=None):
        report = governance.Report(self.root)
        if migration_source:
            # The outer migration verifier supplies this proof in production;
            # this isolated unit fixture exercises only its history boundary.
            report.snapshot_migrations = {'ticket-001': {'sourceSha': migration_source}}
        governance.check_history_order(self.root, self.base, head, 'ticket-001',
                                       'project', 'intent.json', ['project/**'], report)
        return report

    def assert_missing_at(self, commit):
        report = self.inspect()
        findings = [item for item in report.findings if item.code == 'GOV-INTENT-003']
        self.assertEqual(len(findings), 1, report.findings)
        self.assertEqual(findings[0].evidence['firstImplementationCommit'], commit)

    def imported_merge(self, *, include_intent=True, side_payload='accepted\n', mode=False, extra=False):
        self.git('switch', '-qc', 'old-backup')
        self.write('payload.txt', side_payload)
        self.write('project/ticket-099/intent.json', '{"legacy":"stub"}')
        if extra:
            self.write('unreviewed.py', 'unexpected = True\n')
        self.git('add', '-A')
        if mode:
            self.git('update-index', '--chmod=+x', 'payload.txt')
        side = self.commit('old backup with a different carrier', stage=False)
        self.git('switch', '-q', 'main')
        self.write('payload.txt', 'accepted\n')
        self.write('project/ticket-099/intent.json', '{"accepted":"full target carrier"}')
        self.base = self.commit('accepted target payload and full carrier')
        self.git('switch', '-qc', 'ticket-001')
        merged = self.git('merge', '--no-ff', '--no-commit', 'old-backup', check=False)
        self.assertEqual(merged.returncode, 1, merged.stdout + merged.stderr)
        # Resolve the historical carrier collision by preserving every target
        # byte; no ours merge strategy or policy exception is involved.
        self.git('restore', '--source=' + self.base, '--staged', '--worktree', '--',
                 'payload.txt', 'project/ticket-099/intent.json')
        if extra:
            (self.root / 'unreviewed.py').unlink()
        self.write('operator.md', 'New material observation.\n')
        if include_intent:
            self.intent()
        merged_head = self.commit('atomic material merge' if include_intent else 'merge before intent')
        return side, merged_head

    def synthetic_ci_merge(self):
        self.git('switch', '-q', 'main')
        self.git('merge', '--no-ff', 'ticket-001', '-m', 'synthetic CI merge')

    def test_ordinary_atomic_intent_remains_valid(self):
        self.intent()
        self.write('payload.txt', 'new implementation\n')
        self.commit('atomic implementation')
        self.assertFalse(self.inspect().findings)

    def test_ordinary_late_intent_is_rejected(self):
        self.write('payload.txt', 'implementation before intent\n')
        bad = self.commit('early implementation')
        self.intent()
        self.commit('late intent')
        self.assert_missing_at(bad)

    def test_transient_implementation_is_not_hidden_by_final_net_paths(self):
        self.write('temporary.py', 'unapproved = True\n')
        bad = self.commit('transient implementation')
        (self.root / 'temporary.py').unlink()
        self.write('operator.md', 'Final new material.\n')
        self.intent()
        self.commit('remove transient file and add late intent')
        self.assert_missing_at(bad)

    def test_equivalent_import_and_different_old_carrier_are_inherited(self):
        self.imported_merge()
        report = self.inspect()
        self.assertFalse(report.findings)
        self.assertEqual(report.snapshot_migrations, {})

    def test_new_merge_resolution_requires_atomic_intent(self):
        _, bad = self.imported_merge(include_intent=False)
        self.intent()
        self.commit('late carrier-only intent')
        self.assert_missing_at(bad)

    def test_synthetic_ci_merge_retains_valid_history(self):
        self.imported_merge()
        self.synthetic_ci_merge()
        self.assertFalse(self.inspect().findings)

    def test_synthetic_ci_merge_does_not_hide_late_source_intent(self):
        _, bad = self.imported_merge(include_intent=False)
        self.intent()
        self.commit('late source intent')
        self.synthetic_ci_merge()
        self.assert_missing_at(bad)

    def test_non_equivalent_import_is_rejected_even_if_resolved_away(self):
        side, _ = self.imported_merge(side_payload='not accepted by target\n')
        self.assert_missing_at(side)

    def test_equal_blob_with_different_executable_mode_is_not_inherited(self):
        side, _ = self.imported_merge(mode=True)
        self.assert_missing_at(side)

    def test_one_equivalent_path_does_not_hide_new_imported_material(self):
        side, _ = self.imported_merge(extra=True)
        self.assert_missing_at(side)

    def test_deletion_before_intent_remains_material(self):
        (self.root / 'payload.txt').unlink()
        bad = self.commit('delete accepted material before intent')
        self.intent()
        self.write('operator.md', 'New material after the deletion.\n')
        self.commit('late intent')
        self.assert_missing_at(bad)

    def test_migration_revert_to_base_still_requires_intent_at_first_repair(self):
        self.write('imported.py', 'accepted_import = True\n')
        source = self.commit('historical imported source')
        self.intent()
        self.commit('authorized metadata boundary')
        (self.root / 'imported.py').unlink()
        (self.root / 'project/ticket-001/intent.json').unlink()
        bad = self.commit('first repair returns to base without intent')
        self.intent()
        self.write('operator.md', 'Later material with restored intent.\n')
        self.commit('late repair intent')
        report = self.inspect(migration_source=source)
        findings = [item for item in report.findings if item.code == 'GOV-INTENT-003']
        self.assertEqual(len(findings), 1, report.findings)
        self.assertEqual(findings[0].evidence['firstImplementationCommit'], bad)

    def test_git_errors_fail_closed(self):
        with mock.patch.object(governance, 'git_output', side_effect=subprocess.CalledProcessError(128, ['git'])):
            report = self.inspect()
        self.assertEqual([item.code for item in report.findings], ['GOV-DIFF-001'])


if __name__ == '__main__':
    unittest.main()
