"""Malformed JSON arrays must be rejected by both distributed policy readers."""
import copy
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class RepositoryPolicyInputTest(unittest.TestCase):
    def readers(self):
        for index, relative in enumerate((
            'scripts/repository_policy.py',
            'packages/wellman/src/wellman/_bundled/repository_policy.py',
        )):
            spec = importlib.util.spec_from_file_location('policy_input_' + str(index), ROOT / relative)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            yield relative, module

    def test_target_branches_reject_invalid_json_members_without_crashing(self):
        for relative, module in self.readers():
            for value in ({}, [], None, 1, True, ''):
                with self.subTest(reader=relative, member=value):
                    policy = module.default_policy()
                    policy['delivery']['targetBranches'] = ['main', value]
                    self.assertIsInstance(module.policy_error(policy), str)

    def test_target_branch_duplicate_and_valid_lists(self):
        for relative, module in self.readers():
            for branches, valid in ((['main'], True), (['main', 'release'], True),
                                    (['main', 'main'], False), ([], False)):
                with self.subTest(reader=relative, branches=branches):
                    policy = module.default_policy()
                    policy['delivery']['targetBranches'] = branches
                    self.assertEqual(module.policy_error(policy) is None, valid)

    def test_adapter_path_lists_reject_invalid_members_without_crashing(self):
        adapter = dict(schema='wellmanifest.external-ticket-adapter/v1',
                       ticket='PLF-7', summary='JSON input fixture', status='IN_PROGRESS',
                       workflow='EDIT', workstream='governance', allowedPaths=['src/**'],
                       forbiddenPaths=[], sourcePaths=['.planfile/events.jsonl'])
        policy = dict(profile='main-only-planfile', enforcement='enforce',
                      delivery=dict(mode='main-only', checkout='primary', targetBranches=['main']),
                      tickets=dict(backend='planfile', idPattern=r'^PLF-[0-9]+$', referenceRequired=True,
                                   adapterPath='.governance/ticket-adapter.json', sourcePaths=['.planfile/events.jsonl']))
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for relative, module in self.readers():
                for field in ('allowedPaths', 'forbiddenPaths', 'sourcePaths'):
                    for value in ({}, [], None, 1, True, ''):
                        with self.subTest(reader=relative, field=field, member=value):
                            candidate = copy.deepcopy(adapter)
                            candidate[field].append(value)
                            self.assertIsInstance(module.adapter_error(
                                candidate, root, policy['tickets']['adapterPath'], policy['tickets']), str)


    def git(self, root, *args):
        import os, subprocess
        env = {k: v for k, v in os.environ.items() if not k.startswith(('GIT_', 'NEW_PROJECT_'))}
        return subprocess.check_output(['git', '-C', str(root), *args], env=env, stderr=subprocess.DEVNULL)

    def test_staged_regular_adapter_ignores_unstaged_missing_or_symlinked_file(self):
        for reader, module in self.readers():
            with self.subTest(reader=reader), tempfile.TemporaryDirectory() as td:
                parent = Path(td); root = parent / 'repo'; root.mkdir(); self.git(root, 'init', '-q')
                path = root / 'żółć adapter.json'; path.write_bytes(b'{}'); self.git(root, 'add', path.name)
                path.unlink(); outside = parent / 'outside.json'; outside.write_text('external fixture'); path.symlink_to(outside)
                self.assertIsNone(module._safe_snapshot_path(root, path.name, staged=True))
                self.assertEqual(module._snapshot_bytes(root, path.name, staged=True), b'{}')
                self.assertIsInstance(module._safe_snapshot_path(root, path.name, staged=False), str)
                path.unlink()
                self.assertIsNone(module._safe_snapshot_path(root, path.name, staged=True))
                self.assertEqual(module._snapshot_bytes(root, path.name, staged=True), b'{}')

    def test_staged_regular_source_ignores_unstaged_parent_symlink(self):
        for reader, module in self.readers():
            with self.subTest(reader=reader), tempfile.TemporaryDirectory() as td:
                parent = Path(td); root = parent / 'repo'; root.mkdir(); self.git(root, 'init', '-q')
                directory = root / 'nested'; directory.mkdir(); path = directory / 'source.json'; path.write_bytes(b'{"fixture":true}')
                self.git(root, 'add', 'nested/source.json'); path.unlink(); directory.rmdir()
                outside = parent / 'outside'; outside.mkdir(); (outside / 'source.json').write_text('outside fixture')
                directory.symlink_to(outside, target_is_directory=True)
                self.assertIsNone(module._safe_snapshot_path(root, 'nested/source.json', staged=True))
                self.assertEqual(module._snapshot_bytes(root, 'nested/source.json', staged=True), b'{"fixture":true}')
                self.assertIsInstance(module._safe_snapshot_path(root, 'nested/source.json', staged=False), str)

    def test_indexed_symlink_is_rejected_even_when_working_file_is_regular(self):
        for reader, module in self.readers():
            with self.subTest(reader=reader), tempfile.TemporaryDirectory() as td:
                root = Path(td); self.git(root, 'init', '-q'); path = root / 'adapter.json'
                path.symlink_to(root / 'target.json'); self.git(root, 'add', 'adapter.json'); path.unlink(); path.write_text('{}')
                self.assertIsInstance(module._safe_snapshot_path(root, 'adapter.json', staged=True), str)

    def test_unsafe_staged_syntax_is_rejected_before_index_lookup(self):
        from unittest.mock import patch
        for reader, module in self.readers():
            for path in ('../outside', '/outside', 'dir/../outside', 'C:/outside', 'dir//file', './file', 'dir\\..\\outside'):
                with self.subTest(reader=reader, path=path), tempfile.TemporaryDirectory() as td:
                    with patch.object(module, '_index_has_symlink', side_effect=AssertionError('unsafe index lookup')):
                        self.assertIsInstance(module._safe_snapshot_path(Path(td), path, staged=True), str)

    def test_adapter_source_paths_require_non_empty_exact_binding_to_policy(self):
        import json
        base_adapter = dict(
            schema='wellmanifest.external-ticket-adapter/v1',
            ticket='PLF-9',
            summary='Source binding fixture',
            status='IN_PROGRESS',
            workflow='EDIT',
            workstream='governance',
            allowedPaths=['src/**'],
            forbiddenPaths=[],
            sourcePaths=['.planfile/events.jsonl'],
        )
        base_tickets = dict(
            backend='planfile',
            idPattern=r'^PLF-[0-9]+$',
            referenceRequired=True,
            adapterPath='.governance/ticket-adapter.json',
            sourcePaths=['.planfile/events.jsonl'],
        )
        for reader, module in self.readers():
            with self.subTest(reader=reader), tempfile.TemporaryDirectory() as td:
                root = Path(td)
                (root / '.planfile').mkdir()
                (root / 'forged').mkdir()
                payload = json.dumps({'event': {'ticket_id': 'PLF-9', 'status': 'open'}}) + '\n'
                (root / '.planfile/events.jsonl').write_text(payload, encoding='utf-8')
                (root / 'forged/events.jsonl').write_text(payload, encoding='utf-8')

                self.assertIsNone(
                    module.adapter_error(base_adapter, root, base_tickets['adapterPath'], base_tickets)
                )

                empty_sources = copy.deepcopy(base_adapter)
                empty_sources['sourcePaths'] = []
                self.assertIn(
                    'sourcePaths is empty',
                    module.adapter_error(empty_sources, root, base_tickets['adapterPath'], base_tickets) or '',
                )

                forged_sources = copy.deepcopy(base_adapter)
                forged_sources['sourcePaths'] = ['forged/events.jsonl']
                self.assertIn(
                    'must match repositoryPolicy.tickets.sourcePaths',
                    module.adapter_error(forged_sources, root, base_tickets['adapterPath'], base_tickets) or '',
                )

                missing_policy_sources = copy.deepcopy(base_tickets)
                del missing_policy_sources['sourcePaths']
                self.assertIsInstance(
                    module.adapter_error(base_adapter, root, base_tickets['adapterPath'], missing_policy_sources),
                    str,
                )

                base_policy = dict(
                    profile='main-only-planfile',
                    enforcement='enforce',
                    delivery=dict(mode='main-only', checkout='primary', targetBranches=['main']),
                    tickets=copy.deepcopy(base_tickets),
                )
                self.assertIsNone(module.policy_error(base_policy))

                missing_policy = copy.deepcopy(base_policy)
                del missing_policy['tickets']['sourcePaths']
                self.assertIn(
                    'tickets.sourcePaths',
                    module.policy_error(missing_policy) or '',
                )

                for invalid_sources in (
                    [],
                    '.planfile/events.jsonl',
                    None,
                    ['../outside/events.jsonl'],
                    ['.planfile/*.jsonl'],
                    ['.planfile/events.jsonl', '.planfile/events.jsonl'],
                ):
                    with self.subTest(reader=reader, invalid_sources=invalid_sources):
                        bad_policy = copy.deepcopy(base_policy)
                        bad_policy['tickets']['sourcePaths'] = invalid_sources
                        self.assertIn(
                            'sourcePaths must be a safe non-empty path list',
                            module.policy_error(bad_policy) or '',
                        )


if __name__ == '__main__':
    unittest.main()
