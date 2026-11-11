"""Adoption evidence integrity and declared external proof (tickets 351, 424).

A record could claim S4/S5 with the same `.governance/manifest.json` digest as
evidence for every level. Local evidence must exist and match its digest, S3
must point to a CI definition, S4/S5 to declared external proof (hosted ruleset,
runtime receipt), and S3-S5 must each have a distinct URI. Acceptance does not
authenticate external evidence or verify its content, digest or freshness.
"""
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

    def record(self, evidence, level="S4"):
        model = "runtime-conformance" if level == "S5" else "protected-conformance"
        return {"id": PACK, "version": "0.20.92", "revision": "a" * 40, "model": model,
                "level": level, "artifacts": [{"target": ".governance/manifest.json", "sha256": digest(self.manifest)}],
                "evidence": evidence}

    def declared_evidence(self, level="S4"):
        m = {"uri": ".governance/manifest.json", "sha256": digest(self.manifest)}
        evidence = [dict(m, level="S0"), dict(m, level="S1"), dict(m, level="S2"),
                    {"level": "S3", "uri": ".github/workflows/governance.yml", "sha256": digest(self.workflow)},
                    {"level": "S4", "uri": "https://evidence.invalid/rules/1", "sha256": "b" * 64}]
        if level == "S5":
            evidence.append({"level": "S5", "uri": "https://evidence.invalid/receipts/1", "sha256": "c" * 64})
        return evidence

    def check(self, evidence, level="S4"):
        adoption = {"schema": "wellmanifest.standard-adoption/v1", "mode": "enforce", "profile": "probe",
                    "repositoryRole": "unclassified", "adoptions": [self.record(evidence, level)]}
        (self.repo / ".governance" / "standard-adoption.json").write_text(json.dumps(adoption), encoding="utf-8")
        result = subprocess.run([sys.executable, str(CHECKER), "--root", str(self.repo), "--format", "json"],
                                capture_output=True, text=True, check=False, timeout=10)
        report = json.loads(result.stdout)
        self.assertEqual(result.returncode, 0 if report["ok"] else 1, result.stderr)
        return [f["code"] for f in report["findings"]]

    def test_declared_external_s4_and_s5_evidence_passes_offline(self):
        # Reserved .invalid hosts and opaque custom URIs have no fetched proof.
        for level in ("S4", "S5"):
            for prefix in ("https://evidence.invalid/", "wm:", "proof+archive.v1-receipt:"):
                with self.subTest(level=level, prefix=prefix):
                    evidence = self.declared_evidence(level)
                    for item in evidence[4:]:
                        item["uri"] = prefix + item["level"]
                    self.assertEqual(self.check(evidence, level), [])

    def test_manifest_reused_as_proof_for_every_level_is_rejected(self):
        m = {"uri": ".governance/manifest.json", "sha256": digest(self.manifest)}
        hollow = [dict(m, level=f"S{i}") for i in range(5)]
        self.assertIn("STD-ADOPTION-EVIDENCE", self.check(hollow))

    def test_missing_evidence_file_is_rejected(self):
        evidence = self.declared_evidence()
        evidence[3] = dict(evidence[3], uri=".github/workflows/missing.yml")
        self.assertIn("STD-ADOPTION-EVIDENCE", self.check(evidence))

    def test_digest_mismatch_is_rejected(self):
        evidence = self.declared_evidence()
        evidence[0] = dict(evidence[0], sha256="c" * 64)
        self.assertIn("STD-ADOPTION-EVIDENCE", self.check(evidence))

    def test_windows_drive_paths_are_not_external_proof(self):
        for index in (4, 5):
            for uri in (r"C:\proof.json", "C:/proof.json", "C:proof.json"):
                with self.subTest(level=f"S{index}", uri=uri):
                    evidence = self.declared_evidence("S5")
                    evidence[index]["uri"] = uri
                    self.assertIn("STD-ADOPTION-EVIDENCE", self.check(evidence, "S5"))

    def test_external_digest_must_be_lowercase_sha256(self):
        for index in (4, 5):
            for invalid in (None, "", "b" * 63, "b" * 65, "g" * 64, "B" * 64):
                with self.subTest(level=f"S{index}", sha256=invalid):
                    evidence = self.declared_evidence("S5")
                    evidence[index]["sha256"] = invalid
                    self.assertIn("STD-ADOPTION-EVIDENCE", self.check(evidence, "S5"))

    def test_s4_and_s5_require_external_proof_even_for_valid_local_files(self):
        proof = self.repo / "proof.json"
        proof.write_text('{"declared": true}\n', encoding="utf-8")
        for index in (4, 5):
            with self.subTest(level=f"S{index}"):
                evidence = self.declared_evidence("S5")
                evidence[index] = {"level": f"S{index}", "uri": "proof.json", "sha256": digest(proof)}
                self.assertIn("STD-ADOPTION-EVIDENCE", self.check(evidence, "S5"))

    def test_s3_s4_and_s5_cannot_reuse_lower_level_proof_uris(self):
        for lower, upper in ((3, 4), (3, 5), (4, 5), (0, 3), (0, 4), (0, 5)):
            with self.subTest(lower=f"S{lower}", upper=f"S{upper}"):
                evidence = self.declared_evidence("S5")
                # External URIs are valid at every level, isolating reuse from
                # file existence, digest matching and CI-path requirements.
                evidence[lower]["uri"] = "wm:shared-proof"
                evidence[upper]["uri"] = evidence[lower]["uri"]
                self.assertIn("STD-ADOPTION-EVIDENCE", self.check(evidence, "S5"))

    def test_s4_and_s5_need_every_level_in_the_evidence_chain(self):
        for level in ("S4", "S5"):
            for index in range(int(level[1:]) + 1):
                with self.subTest(level=level, missing=f"S{index}"):
                    evidence = self.declared_evidence(level)
                    del evidence[index]
                    self.assertIn("STD-ADOPTION-EVIDENCE", self.check(evidence, level))


if __name__ == "__main__":
    unittest.main()
