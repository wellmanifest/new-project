#!/usr/bin/env python3
"""Canonical scalar lease documents and actual portable CLI regressions."""
from copy import deepcopy
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("lease_safety_runtime", ROOT / "scripts/change_lease_check.py")
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)


def lease():
    return {"schema": runtime.LEASE_SCHEMA, "leaseId": "lease-fixture",
        "repositoryRef": "example/repository", "targetBranch": "main", "ticketId": "ticket-001",
        "workstream": "governance", "scopeHash": "1" * 64, "branchRef": "refs/heads/ticket/001-fixture",
        "worktreeId": "ticket-001--fixture", "ownerActor": "agent:fixture", "ownerSession": "session-fixture",
        "phase": "claimed", "leaseRevision": 1, "fencingToken": 1,
        "issuedAt": "2026-01-01T00:00:00Z", "expiresAt": "2099-01-01T00:00:00Z",
        "heartbeatAt": "2026-01-01T00:00:00Z", "headSha": None, "pullRequest": None,
        "validatorRunId": None, "publicationFrozen": False, "planHash": "2" * 64,
        "previousReceiptRef": None, "eventSequence": 1}


def request(value=None):
    value = value or lease()
    return {"schema": runtime.REQUEST_SCHEMA, "requestId": "request-1", "leaseId": value["leaseId"],
        "action": "begin-edit", "expectedRevision": value["leaseRevision"],
        "expectedFencingToken": value["fencingToken"], "expectedPhase": value["phase"],
        "requestedBy": "agent:fixture", "idempotencyKey": "request-1", "targetHeadSha": None,
        "replacementReceiptRef": None, "authorityRef": "authorization:fixture",
        "requestedAt": "2026-01-01T00:00:00Z"}


class LeaseSafetyTests(unittest.TestCase):
    def setUp(self):
        self.lease = lease()
        self.request = request()
        self.receipt, errors = runtime.evaluate_transition(self.lease, self.request)
        self.assertEqual(errors, [])

    def test_booleans_are_never_integer_revisions_fences_or_pull_requests(self):
        for document, validator, keys in [
            (self.lease, runtime.validate_lease, ["leaseRevision", "fencingToken", "eventSequence", "pullRequest"]),
            (self.request, runtime.validate_request, ["expectedRevision", "expectedFencingToken"]),
            (self.receipt, runtime.validate_receipt, ["previousRevision", "leaseRevision", "previousFencingToken", "fencingToken", "pullRequest"]),
        ]:
            for key in keys:
                with self.subTest(schema=document["schema"], field=key):
                    changed = deepcopy(document)
                    changed[key] = True
                    self.assertTrue(validator(changed))

    def test_date_only_and_offset_free_timestamps_are_rejected(self):
        for document, validator, key in [
            (self.lease, runtime.validate_lease, "issuedAt"),
            (self.lease, runtime.validate_lease, "expiresAt"),
            (self.request, runtime.validate_request, "requestedAt"),
            (self.receipt, runtime.validate_receipt, "occurredAt"),
        ]:
            for value in ["2026-01-01", "2026-01-01T00:00:00", "2026-01-01 00:00:00Z"]:
                with self.subTest(schema=document["schema"], field=key, value=value):
                    changed = deepcopy(document)
                    changed[key] = value
                    self.assertTrue(validator(changed))

    def test_declared_string_bounds_patterns_and_nullable_types_are_enforced(self):
        for document, validator, key, value in [
            (self.lease, runtime.validate_lease, "ownerSession", "s" * 256),
            (self.lease, runtime.validate_lease, "repositoryRef", "invalid/repo/extra"),
            (self.lease, runtime.validate_lease, "validatorRunId", ""),
            (self.lease, runtime.validate_lease, "previousReceiptRef", True),
            (self.lease, runtime.validate_lease, "scopeHash", int("1" * 64)),
            (self.request, runtime.validate_request, "authorityRef", "a" * 513),
            (self.request, runtime.validate_request, "replacementReceiptRef", 17),
            (self.receipt, runtime.validate_receipt, "code", 17),
            (self.receipt, runtime.validate_receipt, "receiptRef", "r" * 513),
        ]:
            with self.subTest(schema=document["schema"], field=key):
                changed = deepcopy(document)
                changed[key] = value
                self.assertTrue(validator(changed))

    def test_explicit_offset_rfc3339_values_remain_supported(self):
        for value in ["2026-01-01T00:00:00Z", "2026-01-01t00:00:00z",
                      "2026-01-01T00:00:00.123+05:30", "2026-01-01T00:00:00-00:00"]:
            with self.subTest(value=value):
                changed = deepcopy(self.lease)
                changed["heartbeatAt"] = value
                self.assertEqual(runtime.validate_lease(changed), [])


    def test_malformed_transition_does_not_fabricate_a_receipt_or_crash(self):
        for value in [True, "1", None]:
            with self.subTest(value=value):
                changed = deepcopy(self.lease)
                changed["leaseRevision"] = value
                receipt, errors = runtime.evaluate_transition(changed, self.request)
                self.assertIsNone(receipt)
                self.assertTrue(errors)

    def rejected(self):
        rejected = deepcopy(self.receipt)
        rejected.update(requestId="request-2", previousRevision=2, leaseRevision=2,
            previousFencingToken=2, fencingToken=2, action="begin-validation", outcome="rejected",
            code="GOV-CHANGE-LEASE-002", phaseBefore="editing", phaseAfter="editing",
            receiptRef="receipt:fixture/2")
        return rejected

    def trace(self, receipts):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "events.jsonl"
            path.write_text("".join(json.dumps(item) + "\n" for item in receipts), encoding="utf-8")
            return runtime.validate_trace(path)

    def test_rejected_receipts_cannot_escape_or_advance_the_accepted_state(self):
        for mutation in [{"leaseId": "another-lease"}, {"previousRevision": 27, "leaseRevision": 27},
                         {"previousFencingToken": 37, "fencingToken": 37},
                         {"phaseBefore": "claimed", "phaseAfter": "claimed"}, {"leaseRevision": 3}]:
            with self.subTest(mutation=mutation):
                rejected = self.rejected()
                rejected.update(mutation)
                self.assertTrue(self.trace([self.receipt, rejected]))

    def test_rejected_receipt_cannot_advance_when_validated_individually(self):
        for mutation in [{"leaseRevision": 3}, {"fencingToken": 3}, {"phaseAfter": "validating"}]:
            with self.subTest(mutation=mutation):
                value = self.rejected()
                value.update(mutation)
                self.assertTrue(runtime.validate_receipt(value))

    def test_valid_rejection_preserves_state_for_the_next_accepted_transition(self):
        current = deepcopy(self.lease)
        current.update(leaseRevision=2, fencingToken=2, phase="editing")
        proposal = request(current)
        proposal.update(requestId="request-3", idempotencyKey="request-3", action="begin-validation")
        accepted, errors = runtime.evaluate_transition(current, proposal)
        self.assertEqual(errors, [])
        self.assertEqual(self.trace([self.receipt, self.rejected(), accepted]), [])

    def test_installed_transition_cli_returns_diagnostics_for_malformed_inputs(self):
        for layout, module, schema in [
            (".governance", ROOT / "scripts/change_lease_check.py",
             ROOT / "subprojects/change-lease/change-lease.schema.json"),
            ("_bundled", ROOT / "packages/wellman/src/wellman/_bundled/change_lease_check.py",
             ROOT / "packages/wellman/src/wellman/_bundled/change-lease.schema.json"),
        ]:
            with self.subTest(layout=layout), tempfile.TemporaryDirectory() as temporary:
                managed = Path(temporary) / layout
                managed.mkdir()
                shutil.copyfile(module, managed / "change_lease_check.py")
                shutil.copyfile(schema, managed / "change-lease.schema.json")
                lease_path, request_path = Path(temporary) / "lease.json", Path(temporary) / "request.json"
                request_path.write_text(json.dumps(self.request), encoding="utf-8")
                for revision in [True, "1", None]:
                    changed = deepcopy(self.lease)
                    changed["leaseRevision"] = revision
                    lease_path.write_text(json.dumps(changed), encoding="utf-8")
                    result = subprocess.run([sys.executable, str(managed / "change_lease_check.py"),
                        "--format", "json", "transition", "--lease", str(lease_path),
                        "--request", str(request_path)], text=True, capture_output=True)
                    self.assertEqual(result.returncode, 1, result.stderr)
                    response = json.loads(result.stdout)
                    self.assertEqual(response["status"], "failed")
                    self.assertNotIn("schema", response)
                    self.assertTrue(response["findings"])
                    self.assertEqual(result.stderr, "")

    @unittest.skipIf(os.name == "nt", "native allocation integration uses POSIX Bash")
    def test_native_local_allocator_emits_a_canonical_advisory_lease(self):
        fixture_spec = importlib.util.spec_from_file_location(
            "lease_allocator_fixture", ROOT / "tests/ticket-allocation-worktree.test.py")
        fixture_module = importlib.util.module_from_spec(fixture_spec)
        fixture_spec.loader.exec_module(fixture_module)
        fixture = fixture_module.TicketAllocationWorktreeTest()
        fixture.setUp()
        try:
            result = fixture.allocate()
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            value = json.loads((fixture.root /
                ".subactor/leases/ticket-001--canonical-ticket.json").read_text(encoding="utf-8"))
            self.assertRegex(value["repositoryRef"], r"^local/[0-9a-f]{64}$")
            self.assertEqual(runtime.validate_lease(value), [])
        finally:
            fixture.doCleanups()

    def test_installed_cli_rejects_boolean_revision(self):
        # Both adopter-managed and wheel-bundled layouts must work outside the
        # source tree. The package build must include its scalar schema.
        package_data = (ROOT / "packages/wellman/pyproject.toml").read_text(encoding="utf-8")
        self.assertIn('"_bundled/*.json"', package_data)
        for layout, module, schema in [
            (".governance", ROOT / "scripts/change_lease_check.py",
             ROOT / "subprojects/change-lease/change-lease.schema.json"),
            ("_bundled", ROOT / "packages/wellman/src/wellman/_bundled/change_lease_check.py",
             ROOT / "packages/wellman/src/wellman/_bundled/change-lease.schema.json"),
        ]:
            with self.subTest(layout=layout), tempfile.TemporaryDirectory() as temporary:
                managed = Path(temporary) / layout
                managed.mkdir()
                shutil.copyfile(module, managed / "change_lease_check.py")
                shutil.copyfile(schema, managed / "change-lease.schema.json")
                path = Path(temporary) / "lease.json"
                for revision, expected_status, expected_exit in [(1, "passed", 0), (True, "failed", 1)]:
                    changed = deepcopy(self.lease)
                    changed["leaseRevision"] = revision
                    path.write_text(json.dumps(changed), encoding="utf-8")
                    result = subprocess.run([sys.executable, str(managed / "change_lease_check.py"),
                        "--format", "json", "validate", str(path)], text=True, capture_output=True)
                    self.assertEqual(result.returncode, expected_exit, result.stderr)
                    self.assertEqual(json.loads(result.stdout)["status"], expected_status)


class WriterSafetyTests(unittest.TestCase):
    def setUp(self):
        import hashlib
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve() / "repo"
        self.root.mkdir()
        def git(*args):
            import os
            env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
            subprocess.run(["git", "-C", str(self.root), *args], env=env, check=True,
                           capture_output=True)
        git("init", "-b", "main")
        git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
            "commit", "--allow-empty", "-m", "seed")
        self.worktree = self.root / ".worktrees/ticket-001--fixture"
        git("worktree", "add", "-b", "ticket/001-fixture", str(self.worktree))
        self.value = lease()
        self.value["repositoryRef"] = "local/" + hashlib.sha256(str(self.root).encode()).hexdigest()
        self.path = self.root / ".subactor/leases/ticket-001--fixture.json"
        self.path.parent.mkdir(parents=True)
        self.save()

    def save(self):
        self.path.write_text(json.dumps(self.value))

    def check(self, actor="agent:fixture", session="session-fixture", revision="1", fencing="1"):
        return runtime.check_writer(self.worktree, self.value["branchRef"], "commit",
                                    actor, session, revision, fencing)

    def test_owner_and_all_identity_and_cas_failures(self):
        self.assertEqual(self.check(), [])
        for values in ({"actor": ""}, {"session": ""}, {"session": "other-session"},
                       {"actor": "agent:other"}, {"fencing": "2"}, {"revision": "2"},
                       {"revision": "true"}, {"session": "bad\nsession"}):
            with self.subTest(values=values):
                self.assertTrue(self.check(**values))

    def test_invalid_expired_released_frozen_and_wrong_bindings(self):
        original = deepcopy(self.value)
        for update in ({"expiresAt": "2020-01-01T00:00:00Z"},
                       {"issuedAt": "2099-01-01T00:00:00Z"},
                       {"phase": "released", "headSha": "a" * 40},
                       {"phase": "publication_frozen", "publicationFrozen": True, "headSha": "a" * 40},
                       {"phase": "expired"}, {"repositoryRef": "other/repository"},
                       {"ticketId": "ticket-002"}, {"worktreeId": "ticket-002--fixture"},
                       {"leaseRevision": True}):
            with self.subTest(update=update):
                self.value = {**original, **update}
                self.save()
                self.assertTrue(self.check())
        for raw in ("[]", "{", "x" * 65537):
            self.path.write_text(raw)
            self.assertTrue(self.check())
        self.path.unlink()
        self.assertTrue(self.check())

    def test_symlinks_including_parent_are_rejected(self):
        saved = self.path.with_name("saved.json")
        self.path.rename(saved)
        try:
            self.path.symlink_to(saved)
        except (OSError, NotImplementedError):
            saved.rename(self.path)
            if os.name == "nt":
                return
            raise
        self.assertTrue(self.check())
        self.path.unlink()
        saved.rename(self.path)
        parent = self.path.parent
        moved = parent.with_name("saved")
        parent.rename(moved)
        try:
            parent.symlink_to(moved, target_is_directory=True)
        except (OSError, NotImplementedError):
            moved.rename(parent)
            if os.name == "nt":
                return
            raise
        self.assertTrue(self.check())

    def test_local_handoff_does_not_grant_authority(self):
        (self.worktree / "handoff.json").write_text(json.dumps({"accepted": True, "ownerSession": "successor"}))
        self.assertTrue(self.check(session="successor"))
        # Simulate the independent controller updating its canonical projection.
        # The checker never applies this transition or accepts the local file.
        self.value.update(ownerSession="successor", leaseRevision=2, fencingToken=2,
                          eventSequence=2, previousReceiptRef="receipt://controller/handoff")
        self.save()
        self.assertTrue(self.check())
        self.assertTrue(self.check(session="successor"))
        self.assertEqual(self.check(session="successor", revision="2", fencing="2"), [])


if __name__ == "__main__":
    unittest.main()
