#!/usr/bin/env python3
"""Real process contention and recovery of advisory continuity storage."""
import argparse
import json
import multiprocessing
import queue
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import work_continuity as continuity

REPOSITORY = "repository:github.com/example/continuity"


def fixture_event(ticket="ticket-001", session="writer-001"):
    digest = "a" * 64
    checkpoint = {
        "schema": continuity.CHECKPOINT_SCHEMA, "authority": "advisory-projection",
        "checkpointRef": "receipt:pending", "previousCheckpointRef": None, "sequence": 1,
        "repositoryRef": REPOSITORY, "ticket": ticket, "workstream": "governance",
        "intentRef": "artifact:fixture/intent/" + ticket, "intentSha256": digest,
        "scopeSha256": digest, "plan": {"ref": "artifact:fixture/plan", "sha256": digest},
        "slice": {"ref": "artifact:fixture/slice", "sha256": digest, "ordinal": 1, "total": 1},
        "targetBranch": "main", "branchRef": "ticket/" + ticket[7:] + "-fixture",
        "headSha": "a" * 40, "worktreeId": ticket + "--fixture", "phase": "publication",
        "authorizationRef": "authorization:fixture/no-execution", "lease": None,
        "remoteObservation": {"remoteName": "origin", "repositoryRef": REPOSITORY,
            "accountRef": "account:github/example", "observedAt": "2026-10-01T00:00:00Z",
            "receiptRef": "receipt:fixture/observation"},
        "workspace": {"state": "clean", "resumeSource": "commit",
            "statusSha256": continuity.EMPTY_SHA256, "snapshotRef": None,
            "snapshotSha256": None, "snapshotReceipt": None, "secretScanReceipt": None},
        "completedCriteria": [], "remainingCriteria": ["AC-01"], "evidenceRefs": [],
        "pendingEffects": [], "nextAction": {"kind": "wait", "criterion": "AC-01"},
        "recordedAt": "2026-10-01T00:00:00Z",
    }
    checkpoint["checkpointRef"] = "receipt:continuity." + ticket + ".1." + continuity.canonical_digest(
        {k: v for k, v in checkpoint.items() if k != "checkpointRef"})
    event = {"schema": continuity.EVENT_SCHEMA, "eventRef": "receipt:pending",
             "previousEventRef": None, "eventSequence": 1, "sessionId": session,
             "checkpoint": checkpoint}
    event["eventRef"] = "receipt:continuity-event." + session + ".1." + continuity.canonical_digest(
        {k: v for k, v in event.items() if k != "eventRef"})
    return continuity.validate_event(event)


def writer(root, event, first, ready, started, second_read, release, results, mode="append"):
    root = Path(root)
    continuity.repository_ref = lambda _: REPOSITORY
    continuity.storage_paths = lambda _: (root / "events.jsonl", root / "index.json", 128, 262144)
    original = continuity.append_event
    def controlled_append(path, value):
        (ready if first else second_read).set()
        if not release.wait(10):
            raise RuntimeError("fixture coordination timeout")
        original(path, value)
    if mode == "append":
        continuity.append_event = controlled_append
    elif mode == "rebuild":
        original_index = continuity.write_index
        def controlled_index(*args):
            ready.set()
            if not release.wait(10):
                raise RuntimeError("fixture coordination timeout")
            return original_index(*args)
        continuity.write_index = controlled_index
    started.set()
    try:
        operation = (continuity.rebuild_index(argparse.Namespace(root=root)) if mode == "rebuild"
                     else continuity.commit_event(root, event))
        results.put(operation["status"])
    except continuity.ContinuityError as error:
        results.put(error.code)


class ContinuityStorageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        # Production derives storage paths from a resolved root. Use the same
        # canonical root in the mock (Windows expands temporary 8.3 aliases).
        self.root = Path(self.temp.name).resolve()
        self.paths = (self.root / "events.jsonl", self.root / "index.json", 128, 262144)
        for name, value in (("repository_ref", REPOSITORY), ("storage_paths", self.paths)):
            mock = patch.object(continuity, name, return_value=value)
            mock.start()
            self.addCleanup(mock.stop)

    def concurrent(self, second_ticket):
        ctx = multiprocessing.get_context("spawn")
        ready, started, second_read, release = [ctx.Event() for _ in range(4)]
        first_started = ctx.Event()  # Retain the semaphore until spawn unpickles it.
        results = ctx.Queue()
        first = ctx.Process(target=writer, args=(str(self.root), fixture_event(), True,
            ready, first_started, second_read, release, results))
        second = ctx.Process(target=writer, args=(str(self.root),
            fixture_event(second_ticket, "writer-002"), False, ready, started,
            second_read, release, results))
        children = [first, second]
        try:
            first.start()
            self.assertTrue(ready.wait(5))
            second.start()
            self.assertTrue(started.wait(5))
            # Original code reaches append with stale state. A correct lock
            # holds the second writer before its stream read until release.
            second_read.wait(1)
            release.set()
            for child in children:
                child.join(10)
                self.assertFalse(child.is_alive())
                self.assertEqual(child.exitcode, 0)
            outcomes = [results.get(timeout=2) for _ in children]
        finally:
            release.set()
            for child in children:
                if child.is_alive():
                    child.terminate()
                    child.join(5)
            results.close()
        events, _ = continuity.event_state(continuity.iter_events(self.paths[0]), REPOSITORY)
        index = json.loads(self.paths[1].read_text())
        self.assert_index(index, events)
        return outcomes, events

    def assert_index(self, index, events):
        continuity.validate_index(index)
        expected = continuity.index_from_events(REPOSITORY, events, 128)
        self.assertEqual(index["entries"], expected["entries"])
        self.assertEqual(index["repositoryRef"], REPOSITORY)
        self.assertEqual(index["maxEntries"], 128)

    def test_stale_concurrent_checkpoint_cannot_corrupt_chain(self):
        outcomes, events = self.concurrent("ticket-001")
        self.assertCountEqual(outcomes, ["recorded", "GOV-CONTINUITY-002"])
        self.assertEqual(len(events), 1)

    def test_concurrent_tickets_keep_both_index_entries(self):
        outcomes, events = self.concurrent("ticket-002")
        self.assertEqual(outcomes, ["recorded", "recorded"])
        self.assertEqual(len(events), 2)

    def test_replay_repairs_index_after_interrupted_write(self):
        event = fixture_event()
        with patch.object(continuity, "write_index", side_effect=OSError("fixture interrupted index")):
            with self.assertRaises(OSError):
                continuity.commit_event(self.root, event)
        self.assertFalse(self.paths[1].exists())
        result = continuity.commit_event(self.root, event)
        self.assertEqual(result["status"], "already-recorded")
        events, _ = continuity.event_state(continuity.iter_events(self.paths[0]), REPOSITORY)
        self.assertEqual(len(events), 1)
        self.assert_index(json.loads(self.paths[1].read_text()), events)

    def test_bounded_index_failure_appends_no_event(self):
        with patch.object(continuity, "storage_paths", return_value=(*self.paths[:3], 1)):
            with self.assertRaises(continuity.ContinuityError):
                continuity.commit_event(self.root, fixture_event())
        self.assertFalse(self.paths[0].exists())
        self.assertFalse(self.paths[1].exists())

    def test_rebuild_and_replay_keep_monotonic_journal(self):
        event = fixture_event()
        continuity.commit_event(self.root, event)
        prefix = self.paths[0].read_bytes()
        self.paths[1].unlink()
        continuity.rebuild_index(argparse.Namespace(root=self.root))
        self.assertEqual(continuity.commit_event(self.root, event)["status"], "already-recorded")
        self.assertEqual(self.paths[0].read_bytes(), prefix)
        self.assertEqual(len(json.loads(self.paths[1].read_text())["entries"]), 1)

    def test_concurrent_rebuild_cannot_replace_a_newer_index(self):
        continuity.commit_event(self.root, fixture_event())
        ctx = multiprocessing.get_context("spawn")
        ready, started, second_read, release, first_started = [ctx.Event() for _ in range(5)]
        results = ctx.Queue()
        children = [
            ctx.Process(target=writer, args=(str(self.root), fixture_event(), True,
                ready, first_started, second_read, release, results, "rebuild")),
            ctx.Process(target=writer, args=(str(self.root), fixture_event("ticket-002", "writer-002"),
                False, ready, started, second_read, release, results, "uncontrolled")),
        ]
        outcomes = []
        try:
            children[0].start()
            self.assertTrue(ready.wait(5))
            children[1].start()
            self.assertTrue(started.wait(5))
            try:
                outcomes.append(results.get(timeout=1))
            except queue.Empty:
                pass
            release.set()
            for child in children:
                child.join(10)
                self.assertFalse(child.is_alive())
                self.assertEqual(child.exitcode, 0)
            while len(outcomes) < 2:
                outcomes.append(results.get(timeout=2))
        finally:
            release.set()
            for child in children:
                if child.is_alive():
                    child.terminate()
                    child.join(5)
            results.close()
        self.assertCountEqual(outcomes, ["rebuilt", "recorded"])
        events, _ = continuity.event_state(continuity.iter_events(self.paths[0]), REPOSITORY)
        self.assertEqual(len(events), 2)
        self.assert_index(json.loads(self.paths[1].read_text()), events)

    def test_invalid_event_digest_appends_nothing(self):
        event = fixture_event()
        event["checkpoint"]["remainingCriteria"].append("AC-02")
        with self.assertRaises(continuity.ContinuityError):
            continuity.commit_event(self.root, event)
        self.assertFalse(self.paths[0].exists())


if __name__ == "__main__":
    unittest.main()
