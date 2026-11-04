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


if __name__ == '__main__':
    unittest.main()
