"""Typed malformed-policy diagnostics through source and delivered checker code."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
IMPLEMENTATIONS = [ROOT / 'scripts/governance_check.py', ROOT / 'packages/wellman/src/wellman/_bundled/governance_check.py']


def load(path):
    name = 'malformed_governance_fixture_' + str(len(sys.modules))
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class MalformedGovernanceTest(unittest.TestCase):
    def test_adoption_binding_registry_rejects_malformed_values_without_crashing(self):
        valid = json.loads((ROOT / 'governance/adoption-bindings.json').read_text())
        for implementation in IMPLEMENTATIONS:
            module = load(implementation)
            with tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                registry = root / 'governance/adoption-bindings.json'
                registry.parent.mkdir()
                registry.write_text(json.dumps(valid))
                self.assertEqual(module.adoption_binding_registry(root), (
                    valid['revisionBoundWorkflowPaths'], valid['digestBoundTargetPatterns']))
                invalid = [None, [], {}, 'invalid', 1]
                for field in ('revisionBoundWorkflowPaths', 'digestBoundTargetPatterns'):
                    duplicate = [valid[field][0], valid[field][0]]
                    for paths in ([{}], [[]], ['valid', {}], [None], duplicate):
                        document = copy.deepcopy(valid)
                        document[field] = paths
                        invalid.append(document)
                for document in invalid:
                    with self.subTest(implementation=str(implementation), document=document):
                        registry.write_text(json.dumps(document))
                        self.assertIsNone(module.adoption_binding_registry(root))

    def test_null_profiles_are_rejected_consistently_with_manifest_schema(self):
        for path in IMPLEMENTATIONS:
            module = load(path)
            policy = json.loads((ROOT / 'governance/manifest.default.json').read_text())['delivery']
            policy['profiles'] = None
            with self.subTest(implementation=str(path)):
                manifest = json.loads((ROOT / 'governance/manifest.default.json').read_text())
                manifest['delivery'] = policy
                schema = json.loads((ROOT / 'governance/manifest.schema.json').read_text())
                self.assertFalse(Draft202012Validator(schema).is_valid(manifest))
                self.assertFalse(module.delivery_policy_valid(policy))

    def test_omitted_and_valid_profiles_keep_their_limits(self):
        for path in IMPLEMENTATIONS:
            module = load(path)
            policy = json.loads((ROOT / 'governance/manifest.default.json').read_text())['delivery']
            with self.subTest(implementation=str(path)):
                self.assertTrue(module.delivery_policy_valid(policy))
                for complexity, profile in policy['profiles'].items():
                    resolved = module.effective_delivery_policy(policy, complexity)
                    self.assertEqual({key: resolved[key] for key in profile}, profile)
                plain = copy.deepcopy(policy)
                del plain['profiles']
                self.assertTrue(module.delivery_policy_valid(plain))
                self.assertEqual(module.effective_delivery_policy(plain, 'S'), plain)

    def test_nonobject_locks_use_existing_sync_diagnostic(self):
        for path in IMPLEMENTATIONS:
            module = load(path)
            with tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                lock = root / 'lock.json'
                for value in [None, [], [1], False, 'invalid', 1, 1.5]:
                    with self.subTest(implementation=str(path), value=value):
                        lock.write_text(json.dumps(value))
                        report = module.Report(root)
                        module.check_lock(root, lock, {'standard': {'version': '1.0.0'}}, report)
                        self.assertEqual([finding.code for finding in report.findings], ['GOV-SYNC-001'])

    def test_valid_lock_still_checks_actual_content(self):
        for path in IMPLEMENTATIONS:
            module = load(path)
            with tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                (root / 'owned.txt').write_text('fixture content')
                lock = root / 'lock.json'
                lock.write_text(json.dumps({'schema': 'new-project.lock/v1',
                    'standard': {'id': 'wellmanifest/new-project', 'version': '1.0.0',
                        'sourceRepository': 'wellmanifest/new-project', 'sourceRevision': 'a' * 40,
                        'publicationStatus': 'published'},
                    'managedFiles': {'owned.txt': hashlib.sha256(b'fixture content').hexdigest()}}))
                with self.subTest(implementation=str(path)):
                    report = module.Report(root)
                    module.check_lock(root, lock, {'standard': {'version': '1.0.0'}}, report)
                    self.assertEqual(report.findings, [])
                    (root / 'owned.txt').write_text('changed fixture')
                    report = module.Report(root)
                    module.check_lock(root, lock, {'standard': {'version': '1.0.0'}}, report)
                    self.assertEqual([finding.code for finding in report.findings], ['GOV-SYNC-001'])


if __name__ == '__main__':
    unittest.main()
