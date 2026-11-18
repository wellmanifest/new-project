import importlib.util
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


SPEC = importlib.util.spec_from_file_location("owner_handoff", "scripts/owner_handoff.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class OwnerHandoffRequestTest(unittest.TestCase):
    def request(self):
        return {
            "schema": MODULE.SCHEMA, "requestId": "r", "worktreeId": "ticket-456--explicit-owner-handoff",
            "ownerActor": "old", "ownerSession": "old-session", "consent": True,
            "expectedRevision": 1, "expectedFencingToken": 1, "expectedLeaseSha256": "a" * 64,
            "expectedHeadSha256": "b" * 64, "expectedDirtySha256": "c" * 64,
            "targetOwnerActor": "new", "targetOwnerSession": "new-session", "ttlSeconds": 600,
        }

    def test_closed_request_requires_explicit_distinct_consent(self):
        request = self.request()
        MODULE._request(request)
        for field, value in (("consent", False), ("targetOwnerActor", "old"), ("ttlSeconds", 7201),
                             ("expectedRevision", True)):
            changed = dict(request, **{field: value})
            with self.subTest(field=field), self.assertRaises(ValueError):
                MODULE._request(changed)

    def test_unknown_or_missing_fields_fail_closed(self):
        request = self.request()
        with self.assertRaises(ValueError):
            MODULE._request(dict(request, extra=True))
        request.pop("expectedDirtySha256")
        with self.assertRaises(ValueError):
            MODULE._request(request)

    def test_real_git_plan_apply_and_exact_replay(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            subprocess.run(["git", "init", "-q", str(root / "seed")], check=True)
            seed = root / "seed"
            subprocess.run(["git", "-C", str(seed), "config", "user.email", "test@example.invalid"], check=True)
            subprocess.run(["git", "-C", str(seed), "config", "user.name", "Test"], check=True)
            (seed / "README").write_text("x\n")
            subprocess.run(["git", "-C", str(seed), "add", "README"], check=True)
            subprocess.run(["git", "-C", str(seed), "commit", "-qm", "base"], check=True)
            worktree = root / ".worktrees" / "ticket-456--explicit-owner-handoff"
            worktree.parent.mkdir()
            subprocess.run(["git", "-C", str(seed), "clone", "-q", ".", str(worktree)], check=True)
            head = subprocess.check_output(["git", "-C", str(worktree), "rev-parse", "HEAD"], text=True).strip()
            branch = subprocess.check_output(["git", "-C", str(worktree), "symbolic-ref", "-q", "HEAD"], text=True).strip()
            dirty = MODULE._content_snapshot(worktree)
            lease = {"schema": "wellmanifest.change-lease/v1", "leaseId": "allocation", "repositoryRef": "wellmanifest/new-project", "targetBranch": "main", "ticketId": "ticket-456", "workstream": "governance", "scopeHash": "a" * 64, "planHash": "b" * 64, "branchRef": branch, "worktreeId": "ticket-456--explicit-owner-handoff", "ownerActor": "old", "ownerSession": "old-session", "leaseRevision": 1, "fencingToken": 1, "eventSequence": 1, "phase": "claimed", "publicationFrozen": False, "issuedAt": "2026-11-18T02:30:20Z", "expiresAt": "2026-11-18T04:30:20Z", "heartbeatAt": "2026-11-18T02:30:20Z", "headSha": head, "pullRequest": None, "validatorRunId": None, "previousReceiptRef": None}
            lease_path = root / ".subactor" / "leases" / (lease["worktreeId"] + ".json")
            lease_path.parent.mkdir(parents=True)
            raw = (json.dumps(lease, sort_keys=True, indent=2) + "\n").encode()
            lease_path.write_bytes(raw)
            request = {"schema": MODULE.SCHEMA, "requestId": "real", "worktreeId": lease["worktreeId"], "ownerActor": "old", "ownerSession": "old-session", "consent": True, "expectedRevision": 1, "expectedFencingToken": 1, "expectedLeaseSha256": hashlib.sha256(raw).hexdigest(), "expectedHeadSha256": hashlib.sha256(head.encode()).hexdigest(), "expectedDirtySha256": dirty, "targetOwnerActor": "new", "targetOwnerSession": "new-session", "ttlSeconds": 600}
            self.assertEqual(MODULE.handoff(root, request)["status"], "planned")
            with self.assertRaises(ValueError):
                MODULE.handoff(root, request, apply=True, actor="wrong", session="old-session")
            authorization = {"schema": "new-project.owner-handoff-authorization/v1", "ownerActor": "old", "ownerSession": "old-session", "consent": True, "requestDigest": hashlib.sha256((json.dumps(request, sort_keys=True, indent=2) + "\n").encode()).hexdigest()}
            read_fd, write_fd = os.pipe()
            os.write(write_fd, json.dumps(authorization).encode())
            os.close(write_fd)
            result = MODULE.handoff(root, request, apply=True, actor="old", session="old-session", authorization_fd=read_fd)
            os.close(read_fd)
            self.assertEqual(result["leaseRevision"], 2)
            self.assertEqual(MODULE.handoff(root, request), result)
            self.assertEqual(json.loads(lease_path.read_text())["ownerActor"], "new")


if __name__ == "__main__":
    unittest.main()
