#!/usr/bin/env python3
"""Registration fixtures never call GitHub, Git or a production Planfile store."""
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import work_registration as registration


def snapshot(state="queued"):
    value = {
        "schema": "new-project.work-registration/v1", "repository": "example/project",
        "sequence": 1, "previousDigest": None,
        "planfile": {"project": "example/project", "version": "0.1.125",
                     "sourceRevision": "a" * 40, "configPath": ".planfile/planfile.yaml",
                     "installationReceipt": "receipt:installer/project/a"},
        "requests": [{"id": "request-1", "planfileTicket": "PLF-001", "state": state,
                      "issue": {"number": 7, "receiptRef": "receipt:github/project/7"},
                      "binding": None, "pr": None, "terminalReceipt": None}],
        "inventoryComplete": True, "worktrees": [], "outbox": [],
    }
    if state in {"editing", "publication", "merged"}:
        request = value["requests"][0]
        request["binding"] = {
            "ticket": "ticket-001", "branch": "ticket/001-example",
            "worktree": ".worktrees/ticket-001--example", "materialHead": None,
            "lease": {"phase": "editing", "revision": 1, "fencingToken": 1,
                      "receiptRef": "receipt:lease/project/1", "ownerActor": "fixture-agent",
                      "ownerSession": "fixture-session", "scopeHash": "d" * 64},
        }
        value["worktrees"] = [{"id": "checkout-1", "path": ".worktrees/ticket-001--example",
                               "branch": "ticket/001-example", "dirty": "clean"}]
        if state != "editing":
            request["binding"]["materialHead"] = "b" * 40
            request["binding"]["lease"]["phase"] = "publication_frozen"
            request["pr"] = {"number": 8, "headSha": "b" * 40, "receiptRef": "receipt:github/pr/8"}
        if state == "merged":
            request["binding"]["lease"]["phase"] = "released"
            request["terminalReceipt"] = "receipt:merge/project/8"
            value["worktrees"] = []
    return value


def pending(value, action):
    rid = value["requests"][0]["id"]
    value["outbox"].append({"requestId": rid, "effect": action,
                            "idempotencyKey": registration.effect_key(value["repository"], rid, action),
                            "journalReceipt": "receipt:outbox/project/1"})


def advance(previous):
    value = copy.deepcopy(previous)
    value["sequence"] += 1
    value["previousDigest"] = registration.digest(previous)
    return value


class RegistrationTest(unittest.TestCase):
    def check(self, value, code=None, previous=None, status="invalid"):
        before = copy.deepcopy(value)
        result = registration.validate(value, previous)
        self.assertEqual(value, before)
        self.assertFalse(result["grantsAuthority"])
        self.assertTrue(result["readOnly"])
        self.assertEqual(result["status"], status, result)
        if code:
            self.assertIn(code, [f["code"] for f in result["findings"]], result)
        return result

    def test_waiting_editing_publication_terminal_shapes(self):
        for state in ("queued", "editing", "publication", "merged"):
            with self.subTest(state=state):
                self.check(snapshot(state), status="complete")

    def test_offline_issue_intake_is_durable_but_incomplete(self):
        value = snapshot()
        value["requests"][0]["issue"] = None
        pending(value, "ensure-issue")
        self.assertTrue(self.check(value, "REG-PENDING", status="pending")["valid"])

    def test_missing_identity_needs_journal(self):
        for field in ("issue", "planfileTicket"):
            value = snapshot()
            value["requests"][0][field] = None
            self.check(value, "REG-BINDING")

    def test_editing_cannot_start_before_issue_exists(self):
        value = snapshot("editing")
        value["requests"][0]["issue"] = None
        pending(value, "ensure-issue")
        self.check(value, "REG-PHASE")

    def test_queued_intake_cannot_reserve_editing_slot(self):
        value = snapshot("editing")
        value["requests"][0]["state"] = "queued"
        self.check(value, "REG-PHASE")

    def test_blocked_work_releases_lease_but_preserves_worktree(self):
        value = snapshot("editing")
        value["requests"][0]["state"] = "blocked"
        self.check(value, "REG-PHASE")
        value["requests"][0]["binding"]["lease"]["phase"] = "released"
        self.check(value, status="complete")

    def test_wrong_planfile_project_and_unsafe_config_paths(self):
        value = snapshot()
        value["planfile"]["project"] = "other/project"
        self.check(value, "REG-PROJECT")
        for path in ("../planfile.yaml", "/tmp/planfile.yaml", "a\\planfile.yaml", "a/./planfile.yaml"):
            value = snapshot()
            value["planfile"]["configPath"] = path
            self.check(value, "REG-PROJECT")

    def test_installation_must_be_pinned_and_receipted(self):
        for field in ("sourceRevision", "installationReceipt"):
            value = snapshot()
            value["planfile"][field] = "latest"
            self.check(value, "REG-SHAPE")

    def test_duplicate_request_issue_ticket_branch_pr(self):
        value = snapshot("publication")
        value["requests"].append(copy.deepcopy(value["requests"][0]))
        self.check(value, "REG-IDENTITY")

    def test_lease_requires_explicit_owner_session_and_scope(self):
        for field in ("ownerActor", "ownerSession", "scopeHash"):
            value = snapshot("editing")
            del value["requests"][0]["binding"]["lease"][field]
            self.check(value, "REG-SHAPE")

    def test_duplicate_planfile_id_even_with_distinct_issue(self):
        value = snapshot()
        duplicate = copy.deepcopy(value["requests"][0])
        duplicate.update(id="request-2", issue={"number": 9, "receiptRef": "receipt:issue/9"})
        value["requests"].append(duplicate)
        self.check(value, "REG-IDENTITY")

    def test_wrong_ticket_branch_or_worktree(self):
        for field, replacement in (("ticket", "ticket-002"), ("branch", "ticket/001-other"),
                                   ("worktree", ".worktrees/ticket/001-example")):
            value = snapshot("editing")
            value["requests"][0]["binding"][field] = replacement
            self.check(value, "REG-LAYOUT")

    def test_orphan_and_external_legacy_checkouts_are_preserved(self):
        value = snapshot()
        value["worktrees"] = [{"id": "legacy", "path": None, "branch": "old/work", "dirty": "unknown"}]
        self.check(value, "REG-ORPHAN", status="pending")

    def test_orphan_cannot_disappear_from_the_next_inventory(self):
        for path in (None, ".worktrees/ticket-001--example"):
            with self.subTest(path=path):
                previous = snapshot()
                previous["worktrees"] = [{"id": "legacy", "path": path,
                                          "branch": "ticket/001-example", "dirty": "unknown"}]
                value = advance(previous)
                value["worktrees"] = []
                self.check(value, "REG-INVENTORY", previous=previous)

    def test_relabelling_an_orphan_does_not_resolve_its_history(self):
        previous = snapshot()
        previous["worktrees"] = [{"id": "legacy", "path": None, "branch": "old/work", "dirty": "unknown"}]
        value = advance(previous)
        value["worktrees"][0]["id"] = "new-label"
        self.check(value, "REG-INVENTORY", previous=previous)

    def test_blocked_checkout_cannot_disappear(self):
        previous = snapshot("editing")
        previous["requests"][0]["state"] = "blocked"
        previous["requests"][0]["binding"]["lease"]["phase"] = "released"
        self.check(previous, status="complete")
        value = advance(previous)
        value["worktrees"] = []
        self.check(value, "REG-INVENTORY", previous=previous)

    def test_known_inventory_path_and_branch_are_stable(self):
        previous = snapshot("editing")
        previous["requests"][0]["state"] = "blocked"
        previous["requests"][0]["binding"]["lease"]["phase"] = "released"
        for field, replacement in (("path", ".worktrees/ticket-002--other"),
                                   ("branch", "ticket/001-other"), ("path", None), ("branch", None)):
            with self.subTest(field=field, replacement=replacement):
                value = advance(previous)
                value["worktrees"][0][field] = replacement
                self.check(value, "REG-IDENTITY", previous=previous)

    def test_unknown_inventory_observation_can_be_resolved_without_relabelling(self):
        previous = snapshot()
        previous["worktrees"] = [{"id": "legacy", "path": None, "branch": None, "dirty": "unknown"}]
        value = advance(previous)
        editing = snapshot("editing")
        value["requests"] = editing["requests"]
        value["worktrees"] = editing["worktrees"]
        value["worktrees"][0]["id"] = "legacy"
        self.check(value, status="complete", previous=previous)

    def test_retirement_requires_a_previously_bound_terminal_request(self):
        previous = snapshot("editing")
        value = advance(previous)
        request = value["requests"][0]
        request["state"] = "cancelled"
        request["terminalReceipt"] = "receipt:controller/cancellation"
        request["binding"]["lease"].update(phase="released", revision=2, fencingToken=2)
        value["worktrees"] = []
        self.check(value, status="complete", previous=previous)
        # A brand-new binding cannot retroactively authorize losing an orphan.
        previous["requests"][0]["binding"] = None
        previous["requests"][0]["state"] = "queued"
        value["previousDigest"] = registration.digest(previous)
        self.check(value, "REG-INVENTORY", previous=previous)

    def test_merged_checkout_can_retire_and_terminal_record_stays(self):
        previous = snapshot("publication")
        value = advance(previous)
        request = value["requests"][0]
        request["state"] = "merged"
        request["terminalReceipt"] = "receipt:controller/merge"
        request["binding"]["lease"].update(phase="released", revision=2, fencingToken=2)
        value["worktrees"] = []
        self.check(value, status="complete", previous=previous)
        self.check(advance(value), status="complete", previous=value)

    def test_terminal_checkout_cannot_be_relabelled_while_remaining_present(self):
        previous = snapshot("merged")
        previous["worktrees"] = snapshot("editing")["worktrees"]
        value = advance(previous)
        value["worktrees"][0]["id"] = "replacement"
        self.check(value, "REG-IDENTITY", previous=previous)

    def test_active_checkout_must_be_observed(self):
        value = snapshot("editing")
        value["worktrees"] = []
        self.check(value, "REG-INVENTORY")

    def test_incomplete_inventory_is_not_complete_registration(self):
        value = snapshot()
        value["inventoryComplete"] = False
        self.check(value, "REG-INVENTORY", status="pending")

    def test_empty_pr_is_not_required_or_accepted(self):
        value = snapshot("editing")
        value["requests"][0]["pr"] = {"number": 8, "headSha": "b" * 40, "receiptRef": "receipt:pr/8"}
        self.check(value, "REG-BINDING")

    def test_first_material_commit_must_register_publication_or_retry(self):
        value = snapshot("editing")
        value["requests"][0]["binding"]["materialHead"] = "b" * 40
        self.check(value, "REG-BINDING")
        pending(value, "ensure-pr")
        self.check(value, "REG-PENDING", status="pending")

    def test_pr_must_bind_exact_head(self):
        value = snapshot("publication")
        value["requests"][0]["pr"]["headSha"] = "c" * 40
        self.check(value, "REG-HEAD")

    def test_terminal_receipt_is_required_and_not_early_approval(self):
        value = snapshot("merged")
        value["requests"][0]["terminalReceipt"] = None
        self.check(value, "REG-PHASE")
        value = snapshot("publication")
        value["requests"][0]["terminalReceipt"] = "receipt:fake/merge"
        self.check(value, "REG-PHASE")

    def test_cancellation_preserves_unpublished_material_without_creating_pr(self):
        value = snapshot("editing")
        request = value["requests"][0]
        request["state"] = "cancelled"
        request["binding"]["materialHead"] = "b" * 40
        request["binding"]["lease"]["phase"] = "released"
        request["terminalReceipt"] = "receipt:owner/cancel"
        self.check(value, status="complete")

    def test_effect_keys_bind_repository_request_and_operation(self):
        value = snapshot()
        pending(value, "ensure-issue")
        value["outbox"][0]["idempotencyKey"] = registration.effect_key("other/project", "request-1", "ensure-issue")
        self.check(value, "REG-IDENTITY")

    def test_duplicate_and_unknown_recovery_effects(self):
        value = snapshot()
        pending(value, "ensure-pr")
        value["outbox"].append(copy.deepcopy(value["outbox"][0]))
        self.check(value, "REG-IDENTITY")
        value["outbox"] = value["outbox"][:1]
        value["outbox"][0]["requestId"] = "unknown"
        self.check(value, "REG-IDENTITY")

    def test_chain_rejects_skips_wrong_digest_and_missing_previous(self):
        previous = snapshot()
        value = advance(previous)
        self.check(value, status="complete", previous=previous)
        self.check(value, "REG-CHAIN")
        value["sequence"] += 1
        self.check(value, "REG-CHAIN", previous=previous)
        value = advance(previous)
        value["previousDigest"] = "0" * 64
        self.check(value, "REG-CHAIN", previous=previous)

    def test_identity_and_terminal_history_do_not_disappear(self):
        previous = snapshot()
        value = advance(previous)
        value["requests"] = []
        self.check(value, "REG-CHAIN", previous=previous)
        value = advance(previous)
        value["requests"][0]["issue"]["number"] = 99
        self.check(value, "REG-IDENTITY", previous=previous)
        previous = snapshot("merged")
        value = advance(previous)
        value["requests"][0]["state"] = "editing"
        value["requests"][0]["binding"]["lease"]["phase"] = "editing"
        self.check(value, "REG-CHAIN", previous=previous)

    def test_new_head_needs_fresh_fencing(self):
        previous = snapshot("editing")
        value = advance(previous)
        value["requests"][0]["binding"]["materialHead"] = "b" * 40
        value["requests"][0]["pr"] = {"number": 8, "headSha": "b" * 40, "receiptRef": "receipt:pr/8"}
        self.check(value, "REG-CHAIN", previous=previous)
        value["requests"][0]["binding"]["lease"].update(revision=2, fencingToken=2)
        self.check(value, status="complete", previous=previous)

    def test_frozen_head_cannot_change_while_publishing(self):
        previous = snapshot("publication")
        value = advance(previous)
        request = value["requests"][0]
        request["binding"]["materialHead"] = request["pr"]["headSha"] = "c" * 40
        request["binding"]["lease"].update(revision=2, fencingToken=2)
        self.check(value, "REG-HEAD", previous=previous)

    def test_closed_shape_rejects_unknown_fields_and_boolean_integers(self):
        value = snapshot()
        value["requests"][0]["approval"] = True
        self.check(value, "REG-SHAPE")
        value = snapshot()
        value["sequence"] = True
        self.check(value, "REG-SHAPE")

    def test_pin_update_needs_fresh_installation_observation(self):
        previous = snapshot()
        value = advance(previous)
        value["planfile"]["sourceRevision"] = "c" * 40
        self.check(value, "REG-PROJECT", previous=previous)
        value["planfile"]["installationReceipt"] = "receipt:installer/project/c"
        self.check(value, status="complete", previous=previous)

    def test_existing_pr_identity_cannot_be_replaced(self):
        previous = snapshot("publication")
        value = advance(previous)
        value["requests"][0]["pr"]["number"] = 100
        self.check(value, "REG-IDENTITY", previous=previous)

    def test_inventory_dirty_observation_can_refresh_without_new_identity(self):
        previous = snapshot("editing")
        previous["worktrees"][0]["dirty"] = "unknown"
        for dirty in ("clean", "dirty"):
            with self.subTest(dirty=dirty):
                value = advance(previous)
                value["worktrees"][0]["dirty"] = dirty
                self.check(value, status="complete", previous=previous)

    def test_unknown_dirty_state_needs_reconciliation(self):
        value = snapshot("editing")
        value["worktrees"][0]["dirty"] = "unknown"
        self.check(value, "REG-INVENTORY", status="pending")

    def test_bundled_schema_matches_independent_jsonschema(self):
        import jsonschema
        schema = registration.load(registration.SCHEMA_PATH)
        jsonschema.Draft202012Validator.check_schema(schema)
        for state in ("queued", "editing", "publication", "merged"):
            jsonschema.validate(snapshot(state), schema)
        value = snapshot()
        value["sequence"] = True
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(value, schema)

    def test_cli_is_read_only_and_rejects_duplicate_keys_nan_and_symlink(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "snapshot.json"
            path.write_text(json.dumps(snapshot()))
            before = path.read_bytes()
            def run(candidate):
                return subprocess.run([sys.executable, str(ROOT / "scripts/work_registration.py"), str(candidate)],
                                      capture_output=True, text=True, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
            self.assertEqual(run(path).returncode, 0)
            self.assertEqual(path.read_bytes(), before)
            for text in ('{"schema":1,"schema":2}', '{"value":NaN}', '{}'):
                path.write_text(text)
                result = run(path)
                self.assertEqual(result.returncode, 1)
                self.assertFalse(json.loads(result.stdout)["grantsAuthority"])
            link = Path(directory) / "link.json"
            link.symlink_to(path)
            self.assertEqual(run(link).returncode, 1)
            self.assertEqual(sorted(p.name for p in Path(directory).iterdir()), ["link.json", "snapshot.json"])


if __name__ == "__main__":
    unittest.main()
