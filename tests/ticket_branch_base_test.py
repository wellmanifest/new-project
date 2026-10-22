#!/usr/bin/env python3
"""A bare local gate run on a ticket branch validates its PR range; disposable fixtures only."""
import io
import json
from contextlib import redirect_stderr
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import governance_check as gc


class TicketBranchBaseTest(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name) / "repo"
        self.git("init", "-q", "-b", "main", str(self.root), cwd=temp.name)
        for key, value in (("user.name", "fixture"), ("user.email", "f@example.invalid"), ("commit.gpgsign", "false")):
            self.git("config", key, value)
        self.manifest = self.root / "manifest.json"
        self.targets(["main"])
        self.base = self.commit("seed")
        self.git("update-ref", "refs/remotes/origin/main", self.base)
        self.git("checkout", "-q", "-b", "ticket/007-sample")
        self.commit("implementation")

    def git(self, *args, cwd=None):
        return subprocess.run(["git", *args], cwd=cwd or self.root, check=True,
                              capture_output=True, text=True).stdout.strip()

    def commit(self, message):
        (self.root / f"{message}.txt").write_text(message)
        self.git("add", "-A")
        self.git("commit", "-qm", message)
        return self.git("rev-parse", "HEAD")

    def targets(self, targets):
        self.manifest.write_text(json.dumps({"delivery": {"targetBranches": targets}}))

    def infer(self):
        report = gc.Report(self.root)
        with redirect_stderr(io.StringIO()) as err:
            base = gc.infer_ticket_branch_base(self.root, self.manifest, "HEAD", report)
        return base, [finding.code for finding in report.findings], err.getvalue()

    def test_ticket_branch_binds_the_merge_base_with_its_target(self):
        self.git("checkout", "-q", "--detach", self.base)
        self.git("update-ref", "refs/remotes/origin/main", self.commit("target-moves-on"))
        self.git("checkout", "-q", "ticket/007-sample")
        base, codes, err = self.infer()
        self.assertEqual((base, codes), (self.base, []))
        self.assertIn(f"--base {self.base} (merge-base of ticket/007-sample and origin/main)", err)

    def test_other_branches_and_detached_heads_are_unchanged(self):
        for ref in ("main", "--detach"):
            with self.subTest(ref=ref):
                self.git("checkout", "-q", ref) if ref == "main" else self.git("checkout", "-q", "--detach", "HEAD")
                self.assertEqual(self.infer()[:2], (None, []))

    def test_missing_target_ref_fails_closed(self):
        self.git("update-ref", "-d", "refs/remotes/origin/main")
        base, codes, _ = self.infer()
        self.assertEqual((base, codes), (None, ["GOV-BASE-001"]))

    def test_several_targets_need_the_ticket_declaration(self):
        self.targets(["main", "release"])
        self.assertEqual(self.infer()[:2], (None, ["GOV-BASE-001"]))
        intent = self.root / "project/ticket-007/intent.json"
        intent.parent.mkdir(parents=True)
        intent.write_text(json.dumps({"delivery": {"targetBranch": "main"}}))
        self.assertEqual(self.infer()[:2], (self.base, []))
        intent.write_text(json.dumps({"delivery": {"targetBranch": "other"}}))
        self.assertEqual(self.infer()[:2], (None, ["GOV-BASE-001"]))

    def test_main_binds_only_bare_flagged_runs(self):
        seen = []
        def capture(args, root, manifest, report):
            seen.append(args.base)
        base_args = ["--root", str(self.root), "--manifest", "manifest.json", "--no-cache", "--format", "json"]
        with patch.object(gc, "run_governance_checks", side_effect=capture), patch.object(gc, "write_report"), \
                patch.object(gc, "load_manifest", return_value={}), \
                redirect_stderr(io.StringIO()):
            for extra in (["--infer-ticket-base"], [], ["--infer-ticket-base", "--base", "HEAD"],
                          ["--infer-ticket-base", "--changed-file", "x.txt"]):
                gc.main(base_args + extra)
        self.assertEqual(seen, [self.base, None, "HEAD", None])

    def test_managed_wrappers_request_inference(self):
        for name in ("project/governance-check.sh", "project/governance-check.bat"):
            text = (ROOT / name).read_text()
            self.assertEqual(text.count("--infer-ticket-base"), 2, name)

    def test_bundled_copy_is_identical(self):
        bundled = ROOT / "packages/wellman/src/wellman/_bundled/governance_check.py"
        self.assertEqual(bundled.read_bytes(), (ROOT / "scripts/governance_check.py").read_bytes())


if __name__ == "__main__":
    unittest.main()
