"""Governance resolution shares observations and rejects invalidated inactivity."""
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SOURCE / "scripts"))
sys.path.insert(0, str(SOURCE / "tests"))
import governance_check as governance
import ticket_activity as activity
import ticket_activity_batch_test as fixtures


class GovernanceActivityPerformanceTests(unittest.TestCase):
    setUp = fixtures.BatchTests.setUp
    git = fixtures.BatchTests.git

    def records(self):
        return [governance.TicketRecord(t, "IN_PROGRESS", "EDIT", {}, None) for t in self.tickets]

    def resolve(self, report=None):
        return governance.active_ticket_records(self.root, {"activeStatuses": ["IN_PROGRESS"]}, self.records(), report)

    def test_stable_resolution_parity_and_shared_subprocess_bound(self):
        with patch.object(activity.subprocess, "run", wraps=subprocess.run) as calls:
            expected = [r for r in self.records() if activity.resolve(self.root, r.directory, {"IN_PROGRESS"}).active]
            baseline = calls.call_count
        with patch.object(activity.subprocess, "run", wraps=subprocess.run) as calls:
            observed = self.resolve()
            optimized = calls.call_count
        self.assertEqual(observed, expected)
        self.assertEqual(observed, [])
        self.assertLess(optimized, baseline // 2, (baseline, optimized))
        self.assertIsNone(activity._READ_BATCH.get())
        print(f"governance activity subprocesses: standalone={baseline}, batched={optimized}, tickets={len(self.tickets)}")

    def assert_invalidated(self, mutate):
        original = governance.resolve_ticket_activity
        def resolve(*args, **kwargs):
            result = original(*args, **kwargs)
            if args[1] == self.tickets[-1]:
                mutate()
            return result
        report = governance.Report(self.root)
        with patch.object(governance, "resolve_ticket_activity", side_effect=resolve):
            self.assertEqual(self.resolve(report), self.records())
        self.assertEqual([f.code for f in report.findings], ["GOV-TICKET-ACTIVITY-001"])
        self.assertEqual(report.findings[0].evidence["fallback"], "remain-active")
        self.assertIsNone(activity._READ_BATCH.get())

    def test_registry_change_retains_every_active_projection(self):
        self.assert_invalidated(lambda: self.registry.write_text("{}"))

    def test_target_change_retains_every_active_projection(self):
        self.assert_invalidated(lambda: self.git("update-ref", "refs/remotes/origin/main", self.head))

    def test_policy_change_retains_every_active_projection(self):
        self.assert_invalidated(lambda: (self.root / "governance/ticket-activity.json").write_text("{}"))

    def test_projection_change_retains_every_active_projection(self):
        self.assert_invalidated(lambda: (self.tickets[0] / "README.md").write_text("- **Status**: BLOCKED\n"))

    def test_missing_registry_never_fabricates_terminal_authority(self):
        self.registry.unlink()
        report = governance.Report(self.root)
        self.assertEqual(self.resolve(report), self.records())
        self.assertIsNone(activity._READ_BATCH.get())

    def test_unavailable_snapshot_retains_only_active_projections(self):
        records = self.records()
        records.append(governance.TicketRecord(self.root / "done", "DONE", "DONE", {}, None))
        report = governance.Report(self.root)
        with patch.object(activity.ActivityReadBatch, "_worktree_registration", side_effect=OSError("unavailable")):
            observed = governance.active_ticket_records(self.root, {}, records, report)
        self.assertEqual(observed, self.records())
        self.assertEqual([f.code for f in report.findings], ["GOV-TICKET-ACTIVITY-001"])
        self.assertIsNone(activity._READ_BATCH.get())

    def test_next_invocation_rechecks_reactivated_branch(self):
        self.assertEqual(self.resolve(), [])
        self.git("switch", "-qc", "ticket/001-followup")
        (self.root / "followup").write_text("new work")
        self.git("add", ".")
        self.git("commit", "-qm", "reopen")
        self.assertEqual([r.directory.name for r in self.resolve()], ["ticket-001"])
        self.assertIsNone(activity._READ_BATCH.get())

    def test_no_active_projections_need_no_git_repository(self):
        records = [governance.TicketRecord(self.root / "absent", "DONE", "DONE", {}, None)]
        with patch.object(activity.subprocess, "run", side_effect=AssertionError("unexpected Git")):
            self.assertEqual(governance.active_ticket_records(self.root / "not-a-repo", {}, records), [])


if __name__ == "__main__":
    unittest.main()
