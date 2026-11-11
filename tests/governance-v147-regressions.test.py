#!/usr/bin/env python3
"""Deterministic regressions for v0.20.147 (#602 disjoint peer admission & #599 controller scaling)."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import fcntl
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import jsonschema

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import change_lease_check as lease_check
import controller_store_compaction as compaction
import ticket_recovery as recovery
import ticket_restoration as restoration
import work_start_check as start

_WT_SPEC = importlib.util.spec_from_file_location("work_start_fixtures", ROOT / "tests/work_start_test.py")
_WT_MOD = importlib.util.module_from_spec(_WT_SPEC)
assert _WT_SPEC.loader is not None
_WT_SPEC.loader.exec_module(_WT_MOD)

REPORT_SCHEMA = json.loads((ROOT / "governance/work-start-report.schema.json").read_text(encoding="utf-8"))
REPORT_VALIDATOR = jsonschema.Draft202012Validator(
    REPORT_SCHEMA, format_checker=jsonschema.Draft202012Validator.FORMAT_CHECKER
)


class DisjointPeerAdmissionRegressionTest(unittest.TestCase):
    """Issue #602: disjoint peer dirty progress must not starve work-start admission."""

    def setUp(self) -> None:
        self.fixture = _WT_MOD.WorkStartTest()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.root = self.fixture.root
        self.git = self.fixture.git
        self.remote_repo = self.fixture.remote()

    def test_continuous_disjoint_peer_writes_admit_coherently(self) -> None:
        peer = self.fixture.sibling(1, "ui")
        (peer / "ui").mkdir(exist_ok=True)
        (peer / "ui/a.txt").write_text("initial peer write\n", encoding="utf-8")
        original = start.dirty_observation
        peer_resolved = peer.resolve()
        peer_calls = 0

        def mutating_dirty_observation(path: Path):
            nonlocal peer_calls
            if Path(path).resolve() == peer_resolved:
                peer_calls += 1
                if peer_calls == 2:
                    (peer / "ui/a.txt").write_text("second peer write during stability check\n", encoding="utf-8")
                    (peer / "ui/new_component.tsx").write_text("export const x = 1;\n", encoding="utf-8")
                    self.git(peer, "add", "ui/a.txt")
            return original(path)

        with patch.object(start, "dirty_observation", side_effect=mutating_dirty_observation):
            report = start.inspect(self.root, "api", ["api/**"], observe_publication=True)

        REPORT_VALIDATOR.validate(report)
        self.assertEqual(report["route"], "NEW_TICKET_CANDIDATE")
        self.assertEqual(report["blockers"], [])
        peer_entry = next(item for item in report["worktrees"] if item["ticket"] == "ticket-001")
        expected_dirty, expected_digest, expected_all = original(peer)
        self.assertEqual(peer_entry["dirtyDigest"], expected_digest)
        self.assertEqual(peer_entry["dirtyPaths"], expected_dirty)
        self.assertEqual(peer_entry["allDirtyPaths"], expected_all)
        self.assertIn("ui/new_component.tsx", peer_entry["dirtyPaths"])

        pub_entry = next(item for item in report["publication"]["worktrees"] if item["path"] == str(peer_resolved))
        self.assertEqual(pub_entry["uncommittedPathCount"], len(expected_all))

        recomputed = dict(report)
        saved_obs_digest = recomputed["observationDigest"]
        recomputed["observationDigest"] = ""
        refs = start.git(self.root, "for-each-ref", "--format=%(refname) %(objectname)", "refs/heads", "refs/remotes")
        manifest = start.manifest_at(self.root)
        self.assertEqual(
            saved_obs_digest,
            start.digest({
                "refs": refs,
                "manifest": manifest,
                "report": recomputed,
                "ticketStorage": "files",
                "ticketInputDigest": start.digest({}),
            }),
        )

    def test_same_workstream_disjoint_subpaths_and_reuse_ticket_admit(self) -> None:
        manifest_path = self.root / ".governance/manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["coordination"]["maxActiveTicketsPerWorkstream"] = 2
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        self.git(self.root, "commit", "-am", "allow 2 active api tickets")
        head_sha = self.git(self.root, "rev-parse", "HEAD")
        self.git(self.root, "update-ref", "refs/remotes/origin/main", head_sha)

        peer = self.fixture.sibling(1, "api", paths=["api/v1/**", "project/ticket-001/**"])
        (peer / "api/v1").mkdir(parents=True, exist_ok=True)
        (peer / "api/v1/one.py").write_text("step 0\n", encoding="utf-8")
        selected = self.fixture.sibling(2, "api", paths=["api/v2/**", "project/ticket-002/**"])
        (selected / "api/v2").mkdir(parents=True, exist_ok=True)
        (selected / "api/v2/two.py").write_text("mine\n", encoding="utf-8")
        selected_digest = start.dirty_observation(selected)[1]

        original = start.dirty_observation
        peer_resolved = peer.resolve()
        seen_peer = 0

        def mutating(path: Path):
            nonlocal seen_peer
            if Path(path).resolve() == peer_resolved:
                seen_peer += 1
                if seen_peer in (2, 4):
                    (peer / "api/v1/one.py").write_text(f"step {seen_peer}\n", encoding="utf-8")
            return original(path)

        with patch.object(start, "dirty_observation", side_effect=mutating):
            reuse_report = start.inspect(
                selected, "api", ["api/v2/**"], ticket="ticket-002",
                expected_dirty_digest=selected_digest,
            )
            manifest["coordination"]["maxActiveTicketsPerWorkstream"] = 3
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            self.git(self.root, "commit", "-am", "allow 3 active api tickets")
            self.git(self.root, "update-ref", "refs/remotes/origin/main", self.git(self.root, "rev-parse", "HEAD"))
            new_report = start.inspect(self.root, "api", ["api/v3/**"])

        REPORT_VALIDATOR.validate(reuse_report)
        self.assertEqual(reuse_report["route"], "REUSE_EXISTING")
        REPORT_VALIDATOR.validate(new_report)
        self.assertEqual(new_report["route"], "NEW_TICKET_CANDIDATE")
        self.assertEqual(new_report["activeTicketCount"], 2)

    def test_selected_primary_overlapping_intent_status_carrier_and_head_mutations_fail_closed(self) -> None:
        peer = self.fixture.sibling(1, "ui")
        (peer / "ui").mkdir(exist_ok=True)
        (peer / "ui/a.txt").write_text("peer initial\n", encoding="utf-8")
        selected = self.fixture.sibling(2, "api")
        (selected / "api").mkdir(exist_ok=True)
        (selected / "api/a.txt").write_text("selected initial\n", encoding="utf-8")
        original = start.dirty_observation

        # 1. Selected checkout mutates during observation -> fail closed
        calls = 0

        def mutate_selected(path: Path):
            nonlocal calls
            if Path(path).resolve() == selected.resolve():
                calls += 1
                if calls == 2:
                    (selected / "api/a.txt").write_text("selected mutated\n", encoding="utf-8")
            return original(path)

        with patch.object(start, "dirty_observation", side_effect=mutate_selected):
            with self.assertRaises(start.ObservationError):
                start.inspect(selected, "api", ["api/**"], ticket="ticket-002")

        # 2. Primary checkout mutates disjoint file during observation -> fail closed
        calls = 0

        def mutate_primary(path: Path):
            nonlocal calls
            if Path(path).resolve() == self.root.resolve():
                calls += 1
                if calls == 2:
                    (self.root / "README.md").write_text("primary mutated\n", encoding="utf-8")
            return original(path)

        with patch.object(start, "dirty_observation", side_effect=mutate_primary):
            with self.assertRaises(start.ObservationError):
                start.inspect(self.root, "api", ["api/**"])
        (self.root / "README.md").unlink()

        # 3. Peer checkout acquires an overlapping dirty file -> fail closed
        calls = 0

        def mutate_peer_overlap(path: Path):
            nonlocal calls
            if Path(path).resolve() == peer.resolve():
                calls += 1
                if calls == 2:
                    (peer / "api/intrusion.txt").write_text("overlapping write\n", encoding="utf-8")
            return original(path)

        with patch.object(start, "dirty_observation", side_effect=mutate_peer_overlap):
            with self.assertRaises(start.ObservationError):
                start.inspect(self.root, "api", ["api/**"])
        (peer / "api/intrusion.txt").unlink()

        # 4. Peer checkout mutates intent.json during observation -> fail closed
        calls = 0
        saved_intent = (peer / "project/ticket-001/intent.json").read_text(encoding="utf-8")

        def mutate_peer_intent(path: Path):
            nonlocal calls
            if Path(path).resolve() == peer.resolve():
                calls += 1
                if calls == 2:
                    updated = json.loads(saved_intent)
                    updated["allowedPaths"].append("api/**")
                    (peer / "project/ticket-001/intent.json").write_text(json.dumps(updated), encoding="utf-8")
            return original(path)

        with patch.object(start, "dirty_observation", side_effect=mutate_peer_intent):
            with self.assertRaises(start.ObservationError):
                start.inspect(self.root, "api", ["api/**"])
        (peer / "project/ticket-001/intent.json").write_text(saved_intent, encoding="utf-8")

        # 5. Peer checkout mutates ticket activity status during observation -> fail closed
        calls = 0
        saved_readme = (peer / "project/ticket-001/README.md").read_text(encoding="utf-8")

        def mutate_peer_status(path: Path):
            nonlocal calls
            if Path(path).resolve() == peer.resolve():
                calls += 1
                if calls == 2:
                    (peer / "project/ticket-001/README.md").write_text(
                        saved_readme.replace("IN_PROGRESS", "BLOCKED"), encoding="utf-8"
                    )
            return original(path)

        with patch.object(start, "dirty_observation", side_effect=mutate_peer_status):
            with self.assertRaises(start.ObservationError):
                start.inspect(self.root, "api", ["api/**"])
        (peer / "project/ticket-001/README.md").write_text(saved_readme, encoding="utf-8")

        # 6. Peer checkout creates unassigned foreign ticket carrier -> fail closed
        calls = 0

        def mutate_foreign_carrier(path: Path):
            nonlocal calls
            if Path(path).resolve() == peer.resolve():
                calls += 1
                if calls == 2:
                    foreign = peer / "project/ticket-999"
                    foreign.mkdir(parents=True, exist_ok=True)
                    (foreign / "README.md").write_text("- **Status**: IN_PROGRESS\n", encoding="utf-8")
            return original(path)

        with patch.object(start, "dirty_observation", side_effect=mutate_foreign_carrier):
            with self.assertRaises(start.ObservationError):
                start.inspect(self.root, "api", ["api/**"])
        shutil.rmtree(peer / "project/ticket-999")

        # 7. Peer checkout commits (changing HEAD) during observation -> fail closed
        calls = 0

        def mutate_peer_head(path: Path):
            nonlocal calls
            if Path(path).resolve() == peer.resolve():
                calls += 1
                if calls == 2:
                    (peer / "ui/committed.txt").write_text("committed\n", encoding="utf-8")
                    self.git(peer, "add", "ui/committed.txt")
                    self.git(peer, "commit", "-m", "peer commit during inspect")
            return original(path)

        with patch.object(start, "dirty_observation", side_effect=mutate_peer_head):
            with self.assertRaises(start.ObservationError):
                start.inspect(self.root, "api", ["api/**"])


def _build_large_controller_state(
    *,
    now: datetime,
    active_resource: str,
    active_lease: dict,
    historical_count: int = 3200,
) -> dict:
    """Construct a valid >4.5 MiB controller lease store document."""
    leases: dict[str, dict] = {}
    acquisitions: dict[str, dict] = {}
    requests: dict[str, dict] = {}
    evidence: dict[str, dict] = {}
    identities: dict[str, dict] = {}

    old_base = now - timedelta(days=30)
    for idx in range(1, historical_count + 1):
        lid = f"lease-hist-{idx:05d}"
        stamp = (old_base + timedelta(minutes=idx)).isoformat()
        phase = ("released", "closed", "cancelled")[idx % 3]
        leases[lid] = {
            "schema": "wellmanifest.change-lease/v1",
            "leaseId": lid,
            "repositoryRef": "example/project",
            "targetBranch": "main",
            "ticketId": f"ticket-{idx:04d}",
            "workstream": "api",
            "scopeHash": f"{idx:064x}",
            "branchRef": f"refs/heads/ticket/{idx:04d}-historical-work-item-padding",
            "worktreeId": f"ticket-{idx:04d}--historical-work-item-padding",
            "ownerActor": "agent:historical-worker",
            "ownerSession": f"session-historical-{idx:05d}-" + ("a" * 48),
            "phase": phase,
            "leaseRevision": 4,
            "fencingToken": idx,
            "issuedAt": stamp,
            "expiresAt": stamp,
            "heartbeatAt": stamp,
            "headSha": "b" * 40,
            "pullRequest": idx,
            "validatorRunId": f"validator-run-{idx:05d}",
            "publicationFrozen": False,
            "planHash": "c" * 64,
            "previousReceiptRef": f"receipt-prev-{idx:05d}",
            "eventSequence": 4,
        }
        acquisitions[f"acq-hist-{idx:05d}"] = {
            "fingerprint": "d" * 64,
            "leaseId": lid,
            "receiptRef": f"receipt-acq-{idx:05d}",
        }
        requests[f"idem-hist-{idx:05d}"] = {
            "schema": "wellmanifest.change-lease-receipt/v1",
            "requestId": f"req-hist-{idx:05d}",
            "leaseId": lid,
            "previousRevision": 3,
            "leaseRevision": 4,
            "previousFencingToken": idx,
            "fencingToken": idx,
            "action": "release" if phase == "released" else "close",
            "outcome": "applied",
            "code": "OK",
            "phaseBefore": "closed" if phase == "released" else "merged",
            "phaseAfter": phase,
            "headSha": "b" * 40,
            "pullRequest": idx,
            "receiptRef": f"receipt-final-{idx:05d}",
            "occurredAt": stamp,
        }
        identities[lid] = {"tokenHash": "e" * 64, "actor": "agent:historical-worker"}

    # Add an expired lease whose previousReceiptRef points to an old editing receipt
    expired_stamp = (now - timedelta(days=20)).isoformat()
    expired_lid = "lease-expired-preserved"
    leases[expired_lid] = {
        "schema": "wellmanifest.change-lease/v1",
        "leaseId": expired_lid,
        "repositoryRef": "example/other",
        "targetBranch": "main",
        "ticketId": "ticket-9001",
        "workstream": "ui",
        "scopeHash": "1" * 64,
        "branchRef": "refs/heads/ticket/9001-expired",
        "worktreeId": "ticket-9001--expired",
        "ownerActor": "agent:stalled",
        "ownerSession": "session-stalled",
        "phase": "expired",
        "leaseRevision": 3,
        "fencingToken": historical_count + 1,
        "issuedAt": expired_stamp,
        "expiresAt": expired_stamp,
        "heartbeatAt": expired_stamp,
        "headSha": "2" * 40,
        "pullRequest": None,
        "validatorRunId": None,
        "publicationFrozen": False,
        "planHash": "3" * 64,
        "previousReceiptRef": "receipt-editing-before-expiry",
        "eventSequence": 3,
    }
    requests["idem-editing-before-expiry"] = {
        "schema": "wellmanifest.change-lease-receipt/v1",
        "requestId": "req-editing-before-expiry",
        "leaseId": "lease-superseded-ancestry",
        "previousRevision": 1,
        "leaseRevision": 2,
        "previousFencingToken": historical_count + 1,
        "fencingToken": historical_count + 1,
        "action": "begin-edit",
        "outcome": "applied",
        "code": "OK",
        "phaseBefore": "claimed",
        "phaseAfter": "editing",
        "headSha": "2" * 40,
        "pullRequest": None,
        "receiptRef": "receipt-editing-before-expiry",
        "occurredAt": expired_stamp,
    }

    # Add a merged (non-closed) lease from 20 days ago — must also be preserved
    merged_lid = "lease-merged-awaiting-close"
    leases[merged_lid] = {
        **leases[expired_lid],
        "leaseId": merged_lid,
        "repositoryRef": "example/merged",
        "ticketId": "ticket-9002",
        "branchRef": "refs/heads/ticket/9002-merged",
        "worktreeId": "ticket-9002--merged",
        "phase": "merged",
        "fencingToken": historical_count + 2,
        "previousReceiptRef": None,
    }

    # Active lease on example/project
    leases[active_lease["leaseId"]] = active_lease
    identities[active_lease["leaseId"]] = {"tokenHash": "f" * 64, "actor": active_lease["ownerActor"]}
    evidence["ev-recent"] = {
        "leaseId": active_lease["leaseId"],
        "recordedAt": now.isoformat(),
        "kind": "heartbeat",
    }
    evidence["ev-ancient"] = {
        "leaseId": "lease-hist-00001",
        "recordedAt": old_base.isoformat(),
        "kind": "takeover",
    }

    other_res = start.digest({"repositoryRef": "example/other", "targetBranch": "main"})
    return {
        "schema": "subactor.repository-change-lease-store/v1",
        "nextFencingToken": historical_count + 10,
        "leases": leases,
        "active": {
            active_resource: active_lease["leaseId"],
            other_res: expired_lid,
        },
        "acquisitions": acquisitions,
        "requests": requests,
        "evidence": evidence,
        "identities": identities,
    }


class LargeControllerStoreAndCompactionRegressionTest(unittest.TestCase):
    """Issue #599: >4 MiB controller observation, recovery/restoration, and safe compaction."""

    def setUp(self) -> None:
        self.fixture = _WT_MOD.WorkStartTest()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.primary = self.fixture.root
        self.git = self.fixture.git
        self.git(self.primary, "remote", "add", "origin", "https://github.com/example/project.git")
        self.now = datetime.now(timezone.utc)
        self.store = Path(self.fixture.temp.name) / "external-controller"
        self.store.mkdir()
        (self.store / ".lock").touch(mode=0o600)
        self.resource = start.digest({"repositoryRef": "example/project", "targetBranch": "main"})
        self.allowed_paths = ["project/ticket-001/**", "api/**"]
        self.active_lease = {
            "schema": "wellmanifest.change-lease/v1",
            "leaseId": "lease-live-001",
            "repositoryRef": "example/project",
            "targetBranch": "main",
            "ticketId": "ticket-001",
            "workstream": "api",
            "scopeHash": start.digest(self.allowed_paths),
            "branchRef": "refs/heads/ticket/001-fixture",
            "worktreeId": "ticket-001--fixture",
            "ownerActor": "agent:live-writer",
            "ownerSession": "secret-live-session-token",
            "phase": "editing",
            "leaseRevision": 2,
            "fencingToken": 3205,
            "issuedAt": self.now.isoformat(),
            "expiresAt": (self.now + timedelta(minutes=30)).isoformat(),
            "heartbeatAt": self.now.isoformat(),
            "headSha": self.fixture.base,
            "pullRequest": None,
            "validatorRunId": None,
            "publicationFrozen": False,
            "planHash": "9" * 64,
            "previousReceiptRef": None,
            "eventSequence": 2,
        }
        self.large_doc = _build_large_controller_state(
            now=self.now,
            active_resource=self.resource,
            active_lease=self.active_lease,
        )

    def test_streaming_observation_recovery_and_restoration_over_4mib(self) -> None:
        # Both sorted ("active" before "leases") and unsorted ("leases" before "active") >4.5 MiB layouts
        sorted_bytes = (json.dumps(self.large_doc, indent=2, sort_keys=True) + "\n").encode("utf-8")
        unsorted_bytes = json.dumps(self.large_doc, sort_keys=False).encode("utf-8")
        self.assertGreater(len(sorted_bytes), 4 * 1024 * 1024 + 512 * 1024)
        self.assertGreater(len(unsorted_bytes), 4 * 1024 * 1024 + 256 * 1024)

        self.fixture.sibling(1, "api")
        for label, raw in (("sorted", sorted_bytes), ("unsorted", unsorted_bytes)):
            with self.subTest(layout=label):
                (self.store / "state.json").write_bytes(raw)
                expected_sha = hashlib.sha256(raw).hexdigest()

                obs_other = start.inspect(
                    self.primary, "ui", (), controller=(self.store, "example/project")
                )
                REPORT_VALIDATOR.validate(obs_other)
                er_other = obs_other["editingResource"]
                self.assertEqual(er_other["state"], "HELD_BY_OTHER")
                self.assertEqual(er_other["stateDigest"], expected_sha)
                self.assertEqual(er_other["holder"]["leaseId"], "lease-live-001")
                self.assertNotIn("secret-live-session-token", json.dumps(obs_other))

                obs_self = start.inspect(
                    self.primary, "api", (), "ticket-001", controller=(self.store, "example/project")
                )
                REPORT_VALIDATOR.validate(obs_self)
                self.assertEqual(obs_self["editingResource"]["state"], "HELD_BY_TICKET")

                # Validate recovery & restoration lease helpers on the >4.5 MiB store
                intent = {
                    "ticket": "ticket-001",
                    "workstream": "api",
                    "allowedPaths": self.allowed_paths,
                    "delivery": {"targetBranch": "main"},
                }
                req = {
                    "leaseId": "lease-live-001",
                    "leaseRevision": 2,
                    "fencingToken": 3205,
                    "ownerActor": "agent:live-writer",
                    "ownerSession": "secret-live-session-token",
                    "ticket": "ticket-001",
                    "worktreeId": "ticket-001--fixture",
                }
                validated = recovery.validate_lease(
                    self.store, req, intent, "example/project",
                    "refs/heads/ticket/001-fixture", "ticket-001--fixture",
                )
                self.assertEqual(validated["fencingToken"], 3205)

                record = {
                    "targetBranch": "main",
                    "branchRef": "refs/heads/ticket/001-fixture",
                    "workstream": "api",
                }
                restored_lease = restoration.controller(
                    self.store, req, record, intent, "example/project"
                )
                self.assertEqual(restored_lease["leaseId"], "lease-live-001")
                self.assertEqual((self.store / "state.json").read_bytes(), raw)

    def test_streaming_parser_rejects_duplicate_keys_trailing_garbage_and_oversize(self) -> None:
        # Duplicate key inside skipped top-level map
        dup_raw = (
            b'{"schema":"subactor.repository-change-lease-store/v1",'
            b'"active":{},"leases":{},"acquisitions":{"k":1,"k":2}}'
        )
        (self.store / "state.json").write_bytes(dup_raw)
        obs = start.controller_observation(self.store, "example/project", "main")
        self.assertEqual((obs["state"], obs["reason"]), ("UNAVAILABLE", "controller-state-invalid"))

        # Trailing garbage past a 64 KiB chunk boundary
        padded = (
            b'{"schema":"subactor.repository-change-lease-store/v1","active":{},"leases":{}}'
            + (b" " * 70000)
            + b"TRAILING"
        )
        (self.store / "state.json").write_bytes(padded)
        obs_trail = start.controller_observation(self.store, "example/project", "main")
        self.assertEqual((obs_trail["state"], obs_trail["reason"]), ("UNAVAILABLE", "controller-state-invalid"))

        # Oversized beyond explicit ceiling -> controller-state-unreadable
        with self.assertRaises(start.ObservationError):
            start.read_controller_projection(self.store, max_bytes=1024)

    def test_controller_store_compaction_plan_cas_lock_archive_and_invariants(self) -> None:
        raw = (json.dumps(self.large_doc, indent=2, sort_keys=True) + "\n").encode("utf-8")
        (self.store / "state.json").write_bytes(raw)
        pre_sha = hashlib.sha256(raw).hexdigest()

        # 1. Read-only plan mode never mutates state.json or creates archive/
        plan = compaction.compact_store(
            self.store,
            apply=False,
            min_recent_leases=10,
            min_recent_acquisitions=10,
            min_recent_requests=10,
            now=self.now,
            root=self.primary,
        )
        self.assertFalse(plan["applied"])
        self.assertFalse(plan["grantsAuthority"])
        self.assertEqual(plan["preStateSha256"], pre_sha)
        self.assertGreater(plan["preBytes"], 4 * 1024 * 1024)
        self.assertLess(plan["postBytes"], 256 * 1024)
        self.assertEqual((self.store / "state.json").read_bytes(), raw)
        self.assertFalse((self.store / "archive").exists())

        # 2. Apply without actor or with stale CAS fails closed
        with self.assertRaises(compaction.CompactionError):
            compaction.compact_store(self.store, apply=True, expected_state_sha256=pre_sha, now=self.now)
        with self.assertRaises(compaction.CompactionError):
            compaction.compact_store(
                self.store, apply=True, operator_actor="controller:ops",
                expected_state_sha256="0" * 64, now=self.now,
            )

        # 3. Apply while .lock is held by another open descriptor fails closed
        with (self.store / ".lock").open("r+b") as held_lock:
            fcntl.flock(held_lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            try:
                cli_busy = subprocess.run(
                    [
                        sys.executable, str(ROOT / "scripts/controller_store_compaction.py"),
                        "--store", str(self.store),
                        "--apply",
                        "--operator-actor", "controller:ops",
                        "--expected-state-sha256", pre_sha,
                    ],
                    capture_output=True, text=True, check=False,
                )
            finally:
                fcntl.flock(held_lock.fileno(), fcntl.LOCK_UN)
        self.assertEqual(cli_busy.returncode, 1)
        self.assertEqual(json.loads(cli_busy.stdout)["reason"], "controller_lock_busy")
        self.assertEqual((self.store / "state.json").read_bytes(), raw)

        # 4. Store inside candidate checkout is rejected when --root is passed
        inside_checkout = self.primary / "bad-store"
        inside_checkout.mkdir()
        (inside_checkout / "state.json").write_bytes(b"{}")
        with self.assertRaises(compaction.CompactionError) as ctx:
            compaction.compact_store(inside_checkout, apply=False, root=self.primary)
        self.assertEqual(ctx.exception.args[0], "store_inside_candidate_checkout")
        shutil.rmtree(inside_checkout)

        # 5. Authenticated apply succeeds, writes verified archive, and preserves every invariant
        cli_apply = subprocess.run(
            [
                sys.executable, str(ROOT / "scripts/controller_store_compaction.py"),
                "--store", str(self.store),
                "--root", str(self.primary),
                "--min-recent-leases", "10",
                "--min-recent-acquisitions", "10",
                "--min-recent-requests", "10",
                "--expected-state-sha256", pre_sha,
                "--operator-actor", "controller:ops",
                "--apply",
            ],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(cli_apply.returncode, 0, cli_apply.stderr or cli_apply.stdout)
        applied = json.loads(cli_apply.stdout)
        self.assertTrue(applied["applied"])
        self.assertFalse(applied["grantsAuthority"])
        self.assertLess(applied["postBytes"], 256 * 1024)
        self.assertEqual(applied["nextFencingToken"], 3210)

        post_raw = (self.store / "state.json").read_bytes()
        self.assertEqual(hashlib.sha256(post_raw).hexdigest(), applied["postStateSha256"])
        compacted_state = json.loads(post_raw.decode("utf-8"))

        # Monotonic fencing token, active map, live/expired/merged leases, and expiry receipt preserved
        self.assertEqual(compacted_state["nextFencingToken"], 3210)
        self.assertEqual(compacted_state["active"], self.large_doc["active"])
        self.assertIn("lease-live-001", compacted_state["leases"])
        self.assertIn("lease-expired-preserved", compacted_state["leases"])
        self.assertIn("lease-merged-awaiting-close", compacted_state["leases"])
        self.assertEqual(len(compacted_state["leases"]), 13)  # 3 non-prunable + 10 min_recent_leases
        self.assertIn("idem-editing-before-expiry", compacted_state["requests"])
        self.assertIn("ev-recent", compacted_state["evidence"])
        self.assertNotIn("ev-ancient", compacted_state["evidence"])

        for lease in compacted_state["leases"].values():
            self.assertEqual(lease_check.validate_lease(lease), [])

        archive_path = self.store / applied["archiveRelPath"]
        self.assertTrue(archive_path.is_file())
        self.assertEqual(archive_path.stat().st_mode & 0o777, 0o600)
        archive_raw = archive_path.read_bytes()
        self.assertEqual(hashlib.sha256(archive_raw).hexdigest(), applied["archiveSha256"])
        archive_doc = json.loads(archive_raw.decode("utf-8"))
        self.assertEqual(archive_doc["preStateSha256"], pre_sha)
        self.assertEqual(archive_doc["postStateSha256"], applied["postStateSha256"])
        self.assertEqual(len(archive_doc["pruned"]["leases"]), 3190)

        # Post-compaction work-start controller observation succeeds and matches postStateSha256
        obs_after = start.controller_observation(self.store, "example/project", "main", "ticket-001")
        self.assertEqual(obs_after["state"], "HELD_BY_TICKET")
        self.assertEqual(obs_after["stateDigest"], applied["postStateSha256"])

        # 6. Crash after _write_archive before _atomic_replace_state recovers cleanly on retry
        crash_store = Path(self.fixture.temp.name) / "crash-recovery-controller"
        crash_store.mkdir()
        (crash_store / "state.json").write_bytes(raw)
        with patch.object(compaction, "_atomic_replace_state", side_effect=OSError("simulated crash")):
            with self.assertRaises(OSError):
                compaction.compact_store(
                    crash_store,
                    apply=True,
                    operator_actor="controller:ops",
                    expected_state_sha256=pre_sha,
                    min_recent_leases=10,
                    min_recent_acquisitions=10,
                    min_recent_requests=10,
                    now=self.now,
                )
        self.assertEqual((crash_store / "state.json").read_bytes(), raw)
        self.assertEqual(len(list((crash_store / "archive").glob("compaction-*.json"))), 1)

        recovered = compaction.compact_store(
            crash_store,
            apply=True,
            operator_actor="controller:ops-retry",
            expected_state_sha256=pre_sha,
            min_recent_leases=10,
            min_recent_acquisitions=10,
            min_recent_requests=10,
            now=self.now + timedelta(seconds=15),
        )
        self.assertTrue(recovered["applied"])
        self.assertEqual(recovered["postStateSha256"], applied["postStateSha256"])
        self.assertEqual(
            hashlib.sha256((crash_store / "state.json").read_bytes()).hexdigest(),
            recovered["postStateSha256"],
        )


if __name__ == "__main__":
    unittest.main()
