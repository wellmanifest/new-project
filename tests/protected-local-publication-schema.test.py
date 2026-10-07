#!/usr/bin/env python3
"""Structural contract fixtures only; these are never production admission."""

import copy
import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads(
    (ROOT / "governance/protected-local-publication.schema.json").read_text()
)


def fixture():
    """Build TEST_ONLY receipt references, without asserting signature validity."""
    receipt = {"uri": "fixture:TEST_ONLY/not-admission", "sha256": "a" * 64}
    value = {
        "schema": "wellmanifest.protected-local-publication/v1",
        "subject": {
            "repository": "fixture/repo", "pullRequest": 1, "ticket": "ticket-001",
            "baseRef": "refs/heads/main", "headRef": "refs/heads/ticket/001-case",
            "baseSha": "1" * 40, "headSha": "2" * 40,
            "testedCommit": "3" * 40, "testedTree": "4" * 40,
        },
        "boundary": {
            "kind": "protected-local-ref", "storageIdentity": "fixture:storage",
            "instanceIdentity": "fixture:instance", "profileSha256": "b" * 64,
            "runtimeSha256": "c" * 64, "policySha256": "d" * 64,
            "isolationReceipt": receipt,
        },
        "actors": {"writer": "fixture:writer", "onedev": "fixture:ci",
                   "validator": "fixture:reviewer"},
        "ci": {"actorRole": "onedev", "runId": "fixture:run",
               "requiredChecks": ["conformance"], "checks": {"conformance": "PASS"},
               "receipt": receipt},
        "approval": {"actorRole": "validator", "actor": "fixture:reviewer",
                     "approvalEvidence": receipt, "trustedVerifierReceipt": receipt},
        "publication": {
            "actorRole": "validator", "transactionId": "fixture:transaction",
            "beforeBaseSha": "1" * 40, "beforeHeadSha": "2" * 40,
            "afterBaseSha": "3" * 40, "afterHeadSha": "2" * 40,
            "receipt": receipt, "liveReadbackReceipt": receipt,
            "hostedPublicationPerformed": False,
        },
        "proof": {
            "issuer": "fixture:TEST_ONLY/issuer",
            "predicateType": "https://wellmanifest.com/attestations/validator/v1",
            "signedAttestation": receipt, "protectedVerificationReceipt": receipt,
        },
        "freshness": {"issuedAt": "2026-10-07T20:00:00Z",
                      "expiresAt": "2026-10-07T20:05:00Z", "maxAgeSeconds": 300},
        "negativeCanaries": {
            name: receipt for name in SCHEMA["properties"]["negativeCanaries"]["required"]
        },
    }
    return copy.deepcopy(value)


class PublicationCompositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Draft202012Validator.check_schema(SCHEMA)
        cls.validator = Draft202012Validator(SCHEMA, format_checker=FormatChecker())

    def refused(self, value):
        self.assertTrue(list(self.validator.iter_errors(value)))

    def test_complete_fixture_is_structural_only(self):
        self.validator.validate(fixture())
        # No signature, Git process or protected trust input is involved here.
        self.assertNotIn("authorizesEffects", SCHEMA["properties"])

    def test_every_required_binding_and_canary_is_mandatory(self):
        original = fixture()
        for key in original:
            with self.subTest(key=key):
                value = copy.deepcopy(original)
                del value[key]
                self.refused(value)
        for section in ["subject", "boundary", "ci", "approval", "publication",
                        "proof", "freshness", "actors", "negativeCanaries"]:
            for key in original[section]:
                with self.subTest(section=section, key=key):
                    value = copy.deepcopy(original)
                    del value[section][key]
                    self.refused(value)

    def test_unknown_boolean_authority_is_closed_at_every_object(self):
        for section in [None, "subject", "boundary", "actors", "ci", "approval",
                        "publication", "proof", "freshness", "negativeCanaries"]:
            with self.subTest(section=section):
                value = fixture()
                target = value if section is None else value[section]
                target["verified"] = True
                self.refused(value)
        value = fixture()
        value["proof"]["protectedVerificationReceipt"]["verified"] = True
        self.refused(value)

    def test_wrong_roles_and_hosted_claims_are_refused(self):
        for section in ["ci", "approval", "publication"]:
            value = fixture()
            value[section]["actorRole"] = "writer"
            self.refused(value)
        for key, invalid in [("kind", "hosted-github"), ("kind", "local-audit")]:
            value = fixture()
            value["boundary"][key] = invalid
            self.refused(value)
        value = fixture()
        value["publication"]["hostedPublicationPerformed"] = True
        self.refused(value)

    def test_invalid_subject_and_receipt_digests_are_refused(self):
        for key, invalid in [
            ("pullRequest", 0), ("pullRequest", True), ("ticket", "ticket-1"),
            ("repository", "../repo"), ("headRef", "main"),
            ("baseRef", "refs/heads/a b"), ("testedCommit", "main"),
            ("testedTree", "f" * 64), ("headSha", "a" * 39),
        ]:
            with self.subTest(key=key, invalid=invalid):
                value = fixture()
                value["subject"][key] = invalid
                self.refused(value)
        for invalid in ["", "latest", "a" * 63, "F" * 64]:
            value = fixture()
            value["proof"]["signedAttestation"]["sha256"] = invalid
            self.refused(value)

    def test_incomplete_failed_or_duplicate_check_shapes_are_refused(self):
        for invalid in [{}, {"conformance": "FAIL"}, {"conformance": True}]:
            value = fixture()
            value["ci"]["checks"] = invalid
            self.refused(value)
        for invalid in [[], ["conformance", "conformance"], [""], [True]]:
            value = fixture()
            value["ci"]["requiredChecks"] = invalid
            self.refused(value)

    def test_invalid_lifetime_and_signature_contract_are_refused(self):
        for invalid in [0, -1, 3601, True, "300"]:
            value = fixture()
            value["freshness"]["maxAgeSeconds"] = invalid
            self.refused(value)
        value = fixture()
        value["freshness"]["issuedAt"] = "2026-10-07T20:00:00"
        self.refused(value)
        value = fixture()
        value["proof"]["predicateType"] = "fixture:unverified-predicate"
        self.refused(value)

    def test_semantic_trust_requires_protected_runtime_beyond_schema(self):
        value = fixture()
        # These shapes are valid; a protected verifier MUST reject their live
        # semantic bindings. This prevents calling this suite crypto/admission.
        value["publication"]["afterBaseSha"] = "9" * 40
        value["actors"]["validator"] = value["actors"]["writer"]
        value["ci"]["requiredChecks"] = ["different-required-check"]
        self.validator.validate(value)
        content = (ROOT / "docs/information/protected-local-publication.md").read_text()
        self.assertIn("Schema validation alone", content)
        catalog = json.loads((ROOT / "governance/standard-packs.json").read_text())
        self.assertEqual(catalog["levels"]["S4"],
                         "Hosted branch protection or rulesets require the exact CI check before merge.")


if __name__ == "__main__":
    unittest.main()
