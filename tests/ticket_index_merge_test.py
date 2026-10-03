#!/usr/bin/env python3
"""Three-way ticket merging preserves deletions, prose and actual Git conflicts."""
import os
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
SOURCE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SOURCE / "scripts"))
import ticket_index_merge_driver as driver


def table(rows, heading="# Tickets", footer=""):
    return (heading + "\n" + driver.START_MARKER + "\n| Ticket ID | State |\n| :--- | :--- |\n"
            + "".join(f"| **ticket-{number:03d}** | {state} |\n" for number, state in rows)
            + driver.END_MARKER + "\n" + footer)


class TicketIndexTests(unittest.TestCase):
    def test_one_sided_deletion_is_preserved(self):
        base = table([(1, "PLAN")])
        for current, other in ((table([]), base), (base, table([]))):
            self.assertEqual(driver.merge_ticket_index_content(base, current, other), table([]))

    def test_one_sided_edit_uses_changed_row_regardless_of_population(self):
        base = table([(1, "LONG | populated | fields")])
        changed = table([(1, "-")])
        self.assertEqual(driver.merge_ticket_index_content(base, base, changed), changed)
        self.assertEqual(driver.merge_ticket_index_content(base, changed, base), changed)

    def test_conflicting_edits_and_edit_delete_require_git_conflict(self):
        base = table([(1, "PLAN")])
        left = table([(1, "IN_PROGRESS")])
        right = table([(1, "BLOCKED")])
        self.assertIsNone(driver.merge_ticket_index_content(base, left, right))
        self.assertIsNone(driver.merge_ticket_index_content(base, left, table([])))

    def test_concurrent_distinct_additions_are_sorted(self):
        self.assertEqual(driver.merge_ticket_index_content(table([]), table([(3, "PLAN")]),
            table([(2, "PLAN")])), table([(2, "PLAN"), (3, "PLAN")]))

    def test_same_id_different_additions_conflict(self):
        self.assertIsNone(driver.merge_ticket_index_content(table([]), table([(1, "PLAN")]),
            table([(1, "BLOCKED")])))

    def test_header_and_footer_edits_are_merged_against_ancestor(self):
        base = table([(1, "PLAN")])
        left = table([(1, "PLAN")], heading="# Target-owned heading")
        right = table([(1, "PLAN")], footer="Target-owned footer\n")
        self.assertEqual(driver.merge_ticket_index_content(base, left, right),
            table([(1, "PLAN")], heading="# Target-owned heading", footer="Target-owned footer\n"))

    def test_unrecognized_content_and_duplicate_markers_fall_back(self):
        base = table([(1, "PLAN")])
        unknown = base.replace(driver.END_MARKER, "Keep this managed-section note\n" + driver.END_MARKER)
        self.assertIsNone(driver.merge_ticket_index_content(base, unknown, base))
        self.assertIsNone(driver.merge_ticket_index_content(base, base + base, base))

    def test_duplicate_ticket_ids_fall_back(self):
        base = table([(1, "PLAN")])
        duplicate = table([(1, "PLAN"), (1, "BLOCKED")])
        self.assertIsNone(driver.merge_ticket_index_content(base, duplicate, base))

    def git_merge(self, current, other):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
        def git(*args, check=True):
            return subprocess.run(["git", *args], cwd=root, env=env,
                                  text=True, capture_output=True, check=check)
        git("init", "-q", "-b", "main")
        git("config", "user.name", "Fixture")
        git("config", "user.email", "fixture@example.invalid")
        git("config", "commit.gpgsign", "false")
        git("config", "core.autocrlf", "false")
        command = shlex.quote(sys.executable) + " " + shlex.quote(str(SOURCE / "scripts/ticket_index_merge_driver.py")) + " %O %A %B"
        git("config", "merge.ticket-index.driver", command)
        (root / ".gitattributes").write_text("TICKETS.md merge=ticket-index\n")
        (root / "TICKETS.md").write_text(table([(1, "PLAN")]))
        git("add", ".")
        git("commit", "-qm", "base")
        git("checkout", "-qb", "other")
        (root / "TICKETS.md").write_text(other)
        git("commit", "-qam", "other change")
        git("checkout", "-q", "main")
        (root / "TICKETS.md").write_text(current)
        git("commit", "-qam", "current change")
        result = git("merge", "--no-edit", "other", check=False)
        return result, (root / "TICKETS.md").read_text()

    def test_real_git_merge_does_not_resurrect_deleted_ticket(self):
        result, merged = self.git_merge(table([(2, "PLAN")]), table([(1, "PLAN"), (3, "PLAN")]))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(merged, table([(2, "PLAN"), (3, "PLAN")]))

    def test_real_git_merge_exposes_conflicting_row_updates(self):
        result, merged = self.git_merge(table([(1, "IN_PROGRESS")]), table([(1, "BLOCKED")]))
        self.assertEqual(result.returncode, 1)
        self.assertIn("<<<<<<<", merged)
        self.assertIn("IN_PROGRESS", merged)
        self.assertIn("BLOCKED", merged)


if __name__ == "__main__":
    unittest.main()
