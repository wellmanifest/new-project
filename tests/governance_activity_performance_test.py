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


class ScopeOverlapCostTests(unittest.TestCase):
    def record(self, number, allowed, forbidden=()):
        return governance.TicketRecord(
            Path(f"project/ticket-{number:03d}"), "IN_PROGRESS", "EDIT",
            {"allowedPaths": list(allowed), "forbiddenPaths": list(forbidden)}, None,
        )

    def overlap(self, records, files, governance_paths=()):
        report = governance.Report(Path("unused"))
        governance.check_scope_overlaps(records, files, list(governance_paths), report)
        return report.findings

    def test_findings_match_existing_predicates_and_preserve_path_positions(self):
        records = [
            self.record(1, ["src/**"], ["src/private/**"]),
            self.record(2, ["src/*.py"], ["src/hidden.py"]),
            self.record(3, ["future/**"]),
            self.record(4, ["future/lib/*.py"]),
        ]
        files = ["src/z.py", "project/ticket-001/README.md", "src/a.py",
                 "src/z.py", "src/private/secret.py", "src/hidden.py", "TODO.md"]
        governance_paths = ["project/**", "TODO.md"]
        expected = []
        for index, first in enumerate(records):
            for second in records[index + 1:]:
                shared = governance.ticket_shared_files(first, second, files, governance_paths)
                patterns = governance.ticket_overlapping_patterns(first, second, governance_paths)
                if shared or patterns:
                    expected.append((sorted(set(shared[:20])), {
                        "tickets": [first.directory.name, second.directory.name],
                        "overlappingPatterns": patterns, "concretePathCount": len(shared),
                    }))
        findings = self.overlap(records, files, governance_paths)
        self.assertEqual([(f.paths, f.evidence) for f in findings], expected)
        self.assertEqual([f.code for f in findings], ["GOV-WORKSTREAM-004"] * 2)
        self.assertEqual(findings[0].paths, ["src/a.py", "src/z.py"])
        self.assertEqual(findings[0].evidence["concretePathCount"], 3)
        self.assertEqual(findings[1].evidence["concretePathCount"], 0)

    def test_report_limit_preserves_input_order_and_full_count(self):
        files = [f"src/{index}.py" for index in range(30, 0, -1)]
        records = [self.record(1, ["src/**"]), self.record(2, ["src/**"])]
        finding, = self.overlap(records, files)
        self.assertEqual(finding.paths, sorted(files[:20]))
        self.assertEqual(finding.evidence["concretePathCount"], len(files))

    def test_path_matching_cost_is_bounded_by_tickets_times_files(self):
        records = [self.record(i + 1, [f"src/part-{i}/**"]) for i in range(24)]
        files = [f"src/part-{i}/file-{j}.py" for i in range(24) for j in range(4)]
        actual_files = set(files)
        original = governance.matches
        path_calls = 0

        def counted(path, patterns):
            nonlocal path_calls
            if path in actual_files:
                path_calls += 1
            return original(path, patterns)

        with patch.object(governance, "matches", side_effect=counted):
            self.assertEqual(self.overlap(records, files, ["project/**"]), [])
        self.assertLessEqual(path_calls, len(files) * (2 * len(records) + 1))

    def test_next_invocation_rechecks_paths_exclusions_and_governance(self):
        records = [self.record(1, ["src/**"]), self.record(2, ["src/*.py"])]
        files = ["src/a.py"]
        self.assertEqual(self.overlap(records, files)[0].evidence["concretePathCount"], 1)
        records[0].intent["forbiddenPaths"] = ["src/**"]
        files.append("src/b.py")
        finding, = self.overlap(records, files)
        self.assertEqual(finding.paths, [])
        self.assertEqual(finding.evidence["concretePathCount"], 0)
        self.assertEqual(self.overlap(records, files, ["src/**"]), [])

    def test_zero_or_one_ticket_needs_no_path_matching(self):
        with patch.object(governance, "matches", side_effect=AssertionError("unexpected matching")):
            self.assertEqual(self.overlap([], ["src/a.py"]), [])
            self.assertEqual(self.overlap([self.record(1, ["src/**"])], ["src/a.py"]), [])


if __name__ == "__main__":
    unittest.main()
