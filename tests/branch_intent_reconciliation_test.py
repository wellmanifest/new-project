"""Conformance regressions: reports cannot authorize deletion or lose work."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/branch_intent_reconciliation.py"
spec = importlib.util.spec_from_file_location("reconciliation", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ReconciliationTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.bindings = {"repository": "example/product", "sourceRef": "refs/heads/ticket/001",
                         "targetRef": "refs/heads/main", "sourceHeadSha": "1" * 40,
                         "targetHeadSha": "2" * 40, "intentSha256": "3" * 64}
        self.observation = {"schema": "new-project.branch-intent-observation/v1",
                            "bindings": self.bindings, "criteria": [{"id": "AC-01", "requiredProof": "content"}],
                            "receipts": {}}
        archive = self.receipt("preservation", {"archiveRef": "archive:source", "archiveSha256": "4" * 64,
                                                 "restoreVerified": True})
        self.proof = self.receipt("content-equivalence", {"sourcePath": "old/schema.json", "targetPath": "models/schema.json",
                                                         "sourceSha256": "5" * 64, "targetSha256": "5" * 64})
        self.row = {"id": "AC-01", "outcome": "implemented", "evidence": [self.proof], "followUp": None, "decision": None}
        self.report = {"schema": "new-project.branch-intent-reconciliation/v1", "bindings": copy.deepcopy(self.bindings),
                       "preservation": archive, "criteria": [self.row]}

    def receipt(self, kind, facts, **overrides):
        item = {"schema": "new-project.branch-intent-evidence/v1", "receiptRef": "receipt:" + kind,
                "kind": kind, "bindings": self.bindings, "criterionIds": ["AC-01"], "facts": facts, **overrides}
        content = json.dumps(item, sort_keys=True).encode()
        sha = hashlib.sha256(content).hexdigest()
        (self.root / (sha + ".json")).write_bytes(content)
        self.observation["receipts"][item["receiptRef"]] = sha
        return {"receiptRef": item["receiptRef"], "sha256": sha}

    def run_report(self):
        return module.reconcile(self.report, self.observation, self.root)

    def invalid(self, message):
        with self.assertRaisesRegex(module.Invalid, message):
            self.run_report()

    def test_different_commits_and_paths_with_equal_content_are_reviewable(self):
        result = self.run_report()
        self.assertEqual(result["status"], "ready-for-owner-review")
        self.assertEqual(result["authority"], "none")
        self.assertIs(result["deletionAuthorized"], False)

    def test_behavior_cannot_be_inferred_from_content_or_patch_similarity(self):
        self.observation["criteria"][0]["requiredProof"] = "behavior"
        self.invalid("implementation proof required")

    def test_passed_behavioral_receipt_satisfies_behavior_inventory(self):
        self.observation["criteria"][0]["requiredProof"] = "behavior"
        self.row["evidence"] = [self.receipt("test-result", {"suiteSha256": "6" * 64,
                                                             "resultSha256": "7" * 64, "passed": True})]
        self.assertEqual(self.run_report()["status"], "ready-for-owner-review")

    def test_failed_behavior_is_not_equivalence(self):
        self.row["evidence"] = [self.receipt("test-result", {"suiteSha256": "6" * 64,
                                                             "resultSha256": "7" * 64, "passed": False})]
        self.invalid("did not pass")

    def test_partial_work_requires_residual_disposition(self):
        self.row["outcome"] = "partial"
        self.invalid("remaining work needs")
        self.row["followUp"] = self.receipt("follow-up", {"ticketRef": "ticket:002", "intentSha256": "8" * 64})
        self.assertEqual(self.run_report()["status"], "ready-for-owner-review")

    def test_missing_work_can_be_explicitly_discarded_but_not_marked_done(self):
        self.row.update(outcome="missing", evidence=[])
        self.invalid("remaining work needs")
        self.row["decision"] = self.receipt("decision", {"decisionRef": "decision:owner", "actor": "owner:verified",
                                                         "disposition": "discard"})
        self.assertIs(self.run_report()["deletionAuthorized"], False)

    def test_superseded_needs_a_verified_superseding_decision(self):
        self.row.update(outcome="superseded", evidence=[])
        self.invalid("superseding decision required")
        self.row["decision"] = self.receipt("decision", {"decisionRef": "decision:new-requirement", "actor": "owner:verified",
                                                         "disposition": "superseded"})
        self.assertEqual(self.run_report()["status"], "ready-for-owner-review")

    def test_unknown_is_unresolved_even_with_backups(self):
        self.row.update(outcome="unknown", evidence=[])
        self.assertEqual(self.run_report()["unresolvedCriteria"], ["AC-01"])
        self.assertEqual(self.run_report()["status"], "needs-review")

    def test_advisory_only_cannot_prove_implementation(self):
        self.row["evidence"] = [self.receipt("advisory", {"analysisRef": "analysis:llm-aligned"})]
        self.invalid("advisory is insufficient")

    def test_missing_or_duplicate_criteria_fail_closed(self):
        self.report["criteria"] = []
        self.invalid("omits expected criteria")
        self.report["criteria"] = [self.row, self.row]
        self.invalid("duplicate criterion")

    def test_wrong_target_source_or_intent_invalidates_report(self):
        for key, value in (("targetHeadSha", "9" * 40), ("sourceHeadSha", "9" * 40), ("intentSha256", "9" * 64)):
            with self.subTest(key=key):
                original = self.report["bindings"][key]
                self.report["bindings"][key] = value
                self.invalid("mismatched report")
                self.report["bindings"][key] = original

    def test_old_receipt_bindings_fail_closed(self):
        old = {**self.bindings, "targetHeadSha": "9" * 40}
        self.row["evidence"] = [self.receipt("content-equivalence", {"sourcePath": "a", "targetPath": "b",
                                                                     "sourceSha256": "5" * 64, "targetSha256": "5" * 64}, bindings=old)]
        self.invalid("mismatched evidence")

    def test_unknown_fields_and_receipts_fail_closed(self):
        self.report["deletionAuthorized"] = True
        self.invalid("unknown fields")
        del self.report["deletionAuthorized"]
        self.observation["receipts"].pop(self.proof["receiptRef"])
        self.invalid("allowlist")

    def test_changed_artifact_is_rejected(self):
        (self.root / (self.proof["sha256"] + ".json")).write_text("{}")
        self.invalid("digest mismatch")

    def test_missing_artifact_and_path_escape_do_not_get_read(self):
        (self.root / (self.proof["sha256"] + ".json")).unlink()
        self.invalid("regular local artifact")
        self.proof["sha256"] = "../../outside"
        self.invalid("invalid digest")

    def test_symlinked_receipt_is_rejected(self):
        path = self.root / (self.proof["sha256"] + ".json")
        saved = self.root / "saved.json"
        path.rename(saved)
        try:
            path.symlink_to(saved)
        except OSError:
            self.skipTest("host does not permit symlinks")
        self.invalid("regular local artifact")

    def test_empty_and_duplicate_expected_inventory_are_rejected(self):
        self.observation["criteria"] = []
        self.invalid("empty criterion inventory")
        row = {"id": "AC-01", "requiredProof": "content"}
        self.observation["criteria"] = [row, row]
        self.invalid("duplicate expected criterion")

    def test_wrong_criterion_evidence_is_rejected(self):
        self.observation["criteria"].append({"id": "AC-02", "requiredProof": "content"})
        self.report["criteria"].append({**self.row, "id": "AC-02"})
        self.invalid("does not cite this criterion")

    def test_unverified_preservation_is_rejected(self):
        self.report["preservation"] = self.receipt("preservation", {"archiveRef": "archive:source", "archiveSha256": "4" * 64,
                                                                   "restoreVerified": False})
        self.invalid("restoration not verified")

    def test_different_bytes_are_not_content_equivalence(self):
        self.row["evidence"] = [self.receipt("content-equivalence", {"sourcePath": "a", "targetPath": "b",
                                                                     "sourceSha256": "5" * 64, "targetSha256": "6" * 64})]
        self.invalid("not byte-equivalent")

    def test_implemented_cannot_hide_a_discard_decision(self):
        self.row["decision"] = self.receipt("decision", {"decisionRef": "decision:discard", "actor": "owner:verified", "disposition": "discard"})
        self.invalid("contradictory disposition")

    def test_duplicate_json_keys_fail_closed(self):
        with self.assertRaises(module.Invalid):
            module.parse_json('{"schema": 1, "schema": 2}')

    def test_repeated_receipt_is_not_additional_evidence(self):
        self.row["evidence"].append(self.proof)
        self.invalid("duplicate criterion evidence")

    def test_cli_exit_codes_and_read_only_behavior(self):
        report, observation = self.root / "report.json", self.root / "observation.json"
        for outcome, expected in (("implemented", 0), ("unknown", 1), ("invented", 2)):
            self.row["outcome"] = outcome
            report.write_text(json.dumps(self.report))
            observation.write_text(json.dumps(self.observation))
            before = {p.name: p.read_bytes() for p in self.root.iterdir()}
            result = subprocess.run([sys.executable, "-B", str(SCRIPT), "--report", str(report),
                                     "--observation", str(observation), "--evidence-root", str(self.root)], capture_output=True, text=True)
            self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
            self.assertIs(json.loads(result.stdout)["deletionAuthorized"], False)
            self.assertEqual(before, {p.name: p.read_bytes() for p in self.root.iterdir()})

    def test_schema_accepts_all_positive_fixture_artifacts(self):
        import jsonschema
        schema = json.loads((ROOT / "governance/branch-intent-reconciliation.schema.json").read_text())
        jsonschema.Draft202012Validator.check_schema(schema)
        for item in (self.report, self.observation, *(json.loads(p.read_text()) for p in self.root.iterdir())):
            jsonschema.validate(item, schema)


if __name__ == "__main__":
    unittest.main()
