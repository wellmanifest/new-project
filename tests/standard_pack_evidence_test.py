"""Adoption evidence must prove its level (ticket-351).

A record could claim S4/S5 with the same `.governance/manifest.json` digest as
evidence for every level. Evidence now has to exist and match its digest, S3
must point to a CI definition, S4/S5 to external proof (hosted ruleset,
runtime receipt), and S3-S5 must each be a distinct proof.
"""
import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "scripts" / "standard_pack_check.py"
PACK = "wellmanifest/new-project"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class EvidenceTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name)
        (self.repo / ".governance").mkdir()
        (self.repo / ".github" / "workflows").mkdir(parents=True)
        catalog = json.loads((ROOT / "governance" / "standard-packs.json").read_text(encoding="utf-8"))
        catalog["profiles"]["probe"] = {"extends": [], "requirements": [{"id": PACK, "minimumLevel": "S4"}]}
        (self.repo / ".governance" / "standard-packs.json").write_text(json.dumps(catalog), encoding="utf-8")
        self.manifest = self.repo / ".governance" / "manifest.json"
        self.manifest.write_text('{"schema": "probe"}\n', encoding="utf-8")
        self.workflow = self.repo / ".github" / "workflows" / "governance.yml"
        self.workflow.write_text("name: governance\n", encoding="utf-8")

    def record(self, evidence):
        return {"id": PACK, "version": "0.20.92", "revision": "a" * 40, "model": "protected-conformance",
                "level": "S4", "artifacts": [{"target": ".governance/manifest.json", "sha256": digest(self.manifest)}],
                "evidence": evidence}

    def honest(self):
        m = {"uri": ".governance/manifest.json", "sha256": digest(self.manifest)}
        return [dict(m, level="S0"), dict(m, level="S1"), dict(m, level="S2"),
                {"level": "S3", "uri": ".github/workflows/governance.yml", "sha256": digest(self.workflow)},
                {"level": "S4", "uri": "https://github.com/acme/example/rules/1", "sha256": "b" * 64}]

    def check(self, evidence):
        adoption = {"schema": "wellmanifest.standard-adoption/v1", "mode": "enforce", "profile": "probe",
                    "repositoryRole": "unclassified", "adoptions": [self.record(evidence)]}
        (self.repo / ".governance" / "standard-adoption.json").write_text(json.dumps(adoption), encoding="utf-8")
        result = subprocess.run([sys.executable, str(CHECKER), "--root", str(self.repo), "--format", "json"],
                                capture_output=True, text=True, check=False)
        return [f["code"] for f in json.loads(result.stdout).get("findings", [])]

    def test_honest_evidence_passes(self):
        self.assertEqual(self.check(self.honest()), [])

    def test_manifest_reused_as_proof_for_every_level_is_rejected(self):
        m = {"uri": ".governance/manifest.json", "sha256": digest(self.manifest)}
        hollow = [dict(m, level=f"S{i}") for i in range(5)]
        self.assertIn("STD-ADOPTION-EVIDENCE", self.check(hollow))

    def test_missing_evidence_file_is_rejected(self):
        evidence = self.honest()
        evidence[3] = dict(evidence[3], uri=".github/workflows/missing.yml")
        self.assertIn("STD-ADOPTION-EVIDENCE", self.check(evidence))

    def test_digest_mismatch_is_rejected(self):
        evidence = self.honest()
        evidence[0] = dict(evidence[0], sha256="c" * 64)
        self.assertIn("STD-ADOPTION-EVIDENCE", self.check(evidence))

    def test_s4_must_be_external_proof(self):
        evidence = self.honest()
        evidence[4] = dict(evidence[3], level="S4")
        self.assertIn("STD-ADOPTION-EVIDENCE", self.check(evidence))


if __name__ == "__main__":
    unittest.main()
