#!/usr/bin/env python3
"""Exercise the actual advisory analyzer with complete synthetic plan records."""
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("remediation_plan_runtime", ROOT / "scripts/remediation_intent.py")
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def fixtures():
    # Reuse the repository's existing READY semantic fixture, without running
    # Bash, allocating tickets, or writing target incident data into Git.
    source = (ROOT / "tests/governance-scripts.test.sh").read_text(encoding="utf-8")
    marker = 'python3 - "$remediation_root" <<\'PY\'\n'
    start = source.index(marker) + len(marker)
    program = source[start:source.index("\nPY\n", start)]
    with tempfile.TemporaryDirectory(prefix="remediation-plan-safety-") as temporary:
        previous = sys.argv
        sys.argv = ["fixture", temporary]
        try:
            exec(compile(program, "existing-remediation-fixture", "exec"), {})
        finally:
            sys.argv = previous
        return tuple(json.loads((Path(temporary) / (name + ".json")).read_text(encoding="utf-8"))
                     for name in ("intent", "graph", "diagnostics", "plans"))


def complete_plan(graph, original, action="modify", record=None):
    plan = deepcopy(original)
    plan.update(status="proposed", createdAt="2026-10-03T00:00:00Z",
                description="Implement the accepted diagnostics while retaining source files.",
                risk={"level": "high", "reasons": ["Preserve source and accepted scope."]},
                rollback="Restore the original source from version control.", confidence=1)
    plan["target"].update(symbols=[], tickets=["ticket-123"], versions=[])
    for key in plan["target"]:
        plan["target"][key] = sorted(set(plan["target"][key]))
    plan["acceptanceCriteria"] = sorted(set(plan["acceptanceCriteria"]))
    plan["changes"] = [{"path": "src/discovery.py", "action": action,
                        "symbols": [], "rationale": "Resolve F-UNREADABLE."}]
    plan["evidence"] = {"graphFingerprint": hashlib.sha256(canonical(graph)).hexdigest(),
                        "recordIds": [record or graph["records"][0]["id"]],
                        "diagnosticIds": ["DIAG-" + "d" * 20], "conclusionIds": [], "proposalIds": []}
    plan["generation"] = {"generator": "fixture", "generatorVersion": "1", "runtimeVersion": "0.17.2",
                          "generatedAt": plan["createdAt"], "requestedMode": "deterministic",
                          "effectiveMode": "deterministic", "degraded": False,
                          "model": None, "provider": None, "responseId": None,
                          "configurationFingerprint": "e" * 64, "reason": None}
    semantic = {key: plan[key] for key in ("title", "description", "priority", "target",
                                          "acceptanceCriteria", "changes", "risk", "rollback", "evidence")}
    plan["planHash"] = hashlib.sha256(canonical(semantic)).hexdigest()
    plan["id"] = "CPLAN-" + plan["planHash"][:20]
    return plan


class RemediationPlanSafetyTests(unittest.TestCase):
    def setUp(self):
        self.intent, self.graph, self.diagnostics, original = fixtures()
        for record, letter in zip(self.graph["records"], "abc"):
            record["id"] = "INT-" + ("NL" if letter == "a" else "TODO") + "-" + letter * 20
        self.diagnostics["diagnostics"][0].update(id="DIAG-" + "d" * 20,
            recordIds=[self.graph["records"][2]["id"]])
        self.original = original["plans"][0]

    def analyze(self, action="modify", extra=None):
        plan = complete_plan(self.graph, self.original, action)
        self.assertNotIn("actionRef", plan["changes"][0])
        plans = {"schemaVersion": "t2c.code-change-plan-set/v1",
                 "generation": {"runtimeVersion": "0.17.2"}, "plans": [plan] + (extra or [])}
        result, blocking = runtime.analyze_todo2code(self.intent, self.graph, self.diagnostics, plans)
        overlay = result["advisoryAnalysis"]
        self.assertEqual(overlay["authority"], "ADVISORY")
        self.assertEqual(overlay["plansDigest"], hashlib.sha256(canonical(plans)).hexdigest())
        return overlay, blocking

    def destructive_metadata(self, index=1):
        self.intent["actions"][index]["risk"].update(level="DESTRUCTIVE",
            authorization="EXPLICIT_HUMAN", automation="PROHIBITED")

    def assert_delete_blocked(self):
        overlay, blocking = self.analyze("delete")
        self.assertTrue(blocking)
        findings = [item for item in overlay["findings"] if item["code"] == "T2C_UNAUTHORIZED_DELETION"]
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["severity"], "BLOCKING")

    def test_implementation_risk_metadata_does_not_authorize_file_deletion(self):
        self.destructive_metadata()
        self.intent["actions"][1]["description"] = "Implement the diagnostic while retaining its source file."
        self.assert_delete_blocked()

    def test_deletion_without_destructive_metadata_is_blocked(self):
        self.assert_delete_blocked()

    def test_destructive_metadata_for_another_path_does_not_authorize_deletion(self):
        self.destructive_metadata(index=0)
        self.assert_delete_blocked()

    def test_modify_remains_nonblocking_and_advisory(self):
        self.destructive_metadata()
        overlay, blocking = self.analyze()
        self.assertFalse(blocking)
        self.assertEqual(overlay["findings"], [])

    def test_unrelated_history_deletion_does_not_enter_the_overlay(self):
        history = complete_plan(self.graph, self.original, "delete", self.graph["records"][2]["id"])
        overlay, blocking = self.analyze(extra=[history])
        self.assertFalse(blocking)
        self.assertNotIn(history["id"], overlay["planIds"])
        self.assertEqual(overlay["findings"], [])

    def test_changed_plan_is_bound_to_a_new_digest(self):
        before, _ = self.analyze()
        after, _ = self.analyze("delete")
        self.assertNotEqual(before["plansDigest"], after["plansDigest"])
        self.assertEqual(before["intentDigest"], after["intentDigest"])


if __name__ == "__main__":
    unittest.main()
