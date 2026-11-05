"""Decision codec fixtures are test data and grant no review/publication authority."""
import copy
import importlib.util
import json
from pathlib import Path
import sys
import unittest

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
IMPLEMENTATIONS = [ROOT / 'scripts/decision_record.py', ROOT / 'packages/wellman/src/wellman/_bundled/decision_record.py']


def load(path):
    spec = importlib.util.spec_from_file_location('decision_codec_fixture', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def fixture():
    return dict(schema='new-project.decision-record/v1', decisionId='D-030-0001',
        ticket='ticket-030', headSha='0' * 40, correlationId='test-fixture-no-authority',
        actor='test-fixture:no-review-authority', appliedRule='P-CORE-015',
        inputs={'required_checks': ['fixture'], 'observed_checks': ['fixture=FAIL']},
        verdict='REQUEST_CHANGES', verdictAuthority='DETERMINISTIC',
        rejected={'alternative': 'APPROVE', 'because': 'FIXTURE_ONLY'},
        assertions=['TEST_FIXTURE_NO_PUBLICATION_AUTHORITY'], advisory=None, derivedFrom=None)


class DecisionCodecTest(unittest.TestCase):
    def check_roundtrip(self, module, record):
        schema = json.loads((ROOT / 'governance/decision-record.schema.json').read_text())
        Draft202012Validator(schema).validate(record)
        self.assertEqual(module.validate_record(record), [])
        encoded = module.to_dsl(record)
        self.assertEqual(module.parse_dsl_record(encoded), record)
        self.assertEqual(module.to_dsl(module.parse_dsl_record(encoded)), encoded)

    def test_existing_canonical_fixture_bytes_do_not_change(self):
        expected = (
            'DECISION D-030-0001\nTICKET ticket-030\nHEAD_SHA ' + '0' * 40 + '\n'
            'CORRELATION_ID test-fixture-no-authority\nACTOR test-fixture:no-review-authority\n'
            'APPLIED_RULE P-CORE-015\nINPUT observed_checks = ["fixture=FAIL"]\n'
            'INPUT required_checks = ["fixture"]\nVERDICT REQUEST_CHANGES AUTHORITY DETERMINISTIC\n'
            'REJECTED APPROVE BECAUSE FIXTURE_ONLY\nASSERT TEST_FIXTURE_NO_PUBLICATION_AUTHORITY\n'
        )
        for path in IMPLEMENTATIONS:
            with self.subTest(implementation=str(path)):
                self.assertEqual(load(path).to_dsl(fixture()), expected)

    def test_schema_valid_input_names_roundtrip(self):
        for path in IMPLEMENTATIONS:
            module = load(path)
            for name in ['change-type', 'source path', '', 'quoted"name', r'path\name',
                         'first\nsecond', 'żółć', 'line\u2028separator', 'next\u0085line']:
                with self.subTest(implementation=str(path), name=name):
                    record = fixture()
                    record['inputs'][name] = {'nested': [True, None, 'fixture/value']}
                    self.check_roundtrip(module, record)

    def test_rejected_alternatives_roundtrip(self):
        for path in IMPLEMENTATIONS:
            module = load(path)
            for alternative in ['manual approval', 'manual\napproval', 'quoted "action" with space',
                                'żółć alternative', 'JSON "reserved" syntax']:
                with self.subTest(implementation=str(path), alternative=alternative):
                    record = fixture()
                    record['rejected']['alternative'] = alternative
                    self.check_roundtrip(module, record)

    def test_legacy_bare_alternatives_remain_literal(self):
        for path in IMPLEMENTATIONS:
            module = load(path)
            for alternative in ['APPROVE', 'REQUEST_CHANGES', 'JSON', '"quoted"', r'path\action']:
                with self.subTest(implementation=str(path), alternative=alternative):
                    record = fixture()
                    record['rejected']['alternative'] = alternative
                    self.assertIn('REJECTED ' + alternative + ' BECAUSE FIXTURE_ONLY\n', module.to_dsl(record))
                    self.check_roundtrip(module, record)

    def test_unicode_line_separators_in_values_and_fences(self):
        for path in IMPLEMENTATIONS:
            module = load(path)
            for separator in ['\u0085', '\u2028', '\u2029']:
                with self.subTest(implementation=str(path), separator=repr(separator)):
                    record = fixture()
                    record['inputs']['payload'] = {'text': 'first' + separator + 'second'}
                    self.check_roundtrip(module, record)
                    self.assertEqual(module.parse_dsl_record('```dsl\n' + module.to_dsl(record) + '```\n'), record)

    def test_malformed_json_identifiers_do_not_mutate_record(self):
        for path in IMPLEMENTATIONS:
            module = load(path)
            for line in [r'INPUT "bad\q" = null', r'INPUT "\u12" = null',
                         r'REJECTED JSON "bad\q" BECAUSE FIXTURE_ONLY',
                         r'REJECTED JSON "\u12" BECAUSE FIXTURE_ONLY',
                         'REJECTED JSON "" BECAUSE FIXTURE_ONLY']:
                with self.subTest(implementation=str(path), line=line):
                    record = fixture()
                    before = copy.deepcopy(record)
                    self.assertFalse(module.apply_decision_line(record, line))
                    self.assertEqual(record, before)

    def test_append_only_still_detects_changes_to_quoted_inputs(self):
        for path in IMPLEMENTATIONS:
            module = load(path)
            record = fixture()
            record['inputs']['source path'] = 'original'
            with self.subTest(implementation=str(path)):
                previous = module.to_dsl(record)
                record['inputs']['source path'] = 'changed'
                self.assertTrue(any('GOV-DECISION-001' in error for error in
                                    module.check_append_only(previous, module.to_dsl(record))))


if __name__ == '__main__':
    unittest.main()
