#!/usr/bin/env python3
"""Real process contention and recovery of advisory continuity storage."""
import argparse
import errno
import json
import multiprocessing
import os
import subprocess
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

    def test_transaction_rejects_symlink_and_hardlink_locks(self):
        foreign = self.root / "foreign.lock"
        foreign.write_bytes(b"foreign lock must stay unchanged")
        lock = self.paths[0].with_name("events.jsonl.lock")
        self.symlink(lock, foreign)
        for kind in ("symlink", "hardlink"):
            with self.subTest(kind=kind):
                with self.assertRaises(continuity.ContinuityError) as error:
                    with continuity.storage_transaction(self.paths[0]):
                        self.fail("linked lock admitted")
                self.assertEqual(error.exception.code, "GOV-CONTINUITY-001")
                self.assertEqual(foreign.read_bytes(), b"foreign lock must stay unchanged")
            lock.unlink()
            if kind == "symlink":
                os.link(foreign, lock)

    @unittest.skipUnless(os.name == "posix", "POSIX lock substitution boundary")
    def test_parent_swap_cannot_enter_a_second_transaction(self):
        parent = self.root / "sessions"
        parent.mkdir()
        event = parent / "events.jsonl"
        alternative = self.root / "alternative"
        alternative.mkdir()
        real_open = os.open
        swapped = []
        def substitute(path, flags, *args, **kwargs):
            if Path(path).name == "events.jsonl.lock" and not swapped:
                parent.rename(self.root / "held-sessions")
                parent.symlink_to(alternative, target_is_directory=True)
                swapped.append(True)
            return real_open(path, flags, *args, **kwargs)
        with continuity.storage_transaction(event):
            with patch.object(continuity.os, "open", side_effect=substitute):
                with self.assertRaises(continuity.ContinuityError) as error:
                    with continuity.storage_transaction(event):
                        self.fail("second transaction entered through a substituted parent")
                self.assertEqual(error.exception.code, "GOV-CONTINUITY-001")
        self.assertEqual(swapped, [True])
        self.assertFalse((alternative / "events.jsonl.lock").exists())

    @unittest.skipUnless(os.name == "posix", "POSIX lock identity boundary")
    def test_lock_and_regular_parent_replacement_during_acquire_are_rejected(self):
        import fcntl
        real_flock = fcntl.flock
        for replacement in ("lock", "parent", "waiting-parent"):
            with self.subTest(replacement=replacement):
                parent = self.root / replacement
                parent.mkdir()
                event = parent / "events.jsonl"
                lock = parent / "events.jsonl.lock"
                swapped = []
                def substitute(descriptor, operation):
                    if operation & fcntl.LOCK_EX and not swapped:
                        swapped.append(True)
                        if replacement == "lock":
                            lock.rename(parent / "held.lock")
                            lock.write_bytes(b"replacement")
                        else:
                            parent.rename(self.root / (replacement + "-held"))
                            parent.mkdir()
                        if replacement == "waiting-parent":
                            raise BlockingIOError(errno.EAGAIN, "fixture contention")
                    return real_flock(descriptor, operation)
                with patch.object(fcntl, "flock", side_effect=substitute):
                    with self.assertRaises(continuity.ContinuityError) as error:
                        with continuity.storage_transaction(event):
                            self.fail("substituted lock namespace admitted")
                    self.assertEqual(error.exception.code, "GOV-CONTINUITY-001")
                self.assertEqual(swapped, [True])
                self.assertFalse(event.exists())

    @unittest.skipUnless(os.name == "posix", "POSIX safe-lock capability boundary")
    def test_missing_no_follow_fails_before_creating_lock(self):
        for capability in ("O_NOFOLLOW", "O_DIRECTORY"):
            with self.subTest(capability=capability):
                with patch.object(continuity.os, capability, None):
                    with self.assertRaises(continuity.ContinuityError):
                        with continuity.storage_transaction(self.paths[0]):
                            self.fail("unsafe lock capability admitted")
        self.assertFalse(self.paths[0].with_name("events.jsonl.lock").exists())

    def test_regular_lock_is_reused_after_transaction_body_failure(self):
        lock = self.paths[0].with_name("events.jsonl.lock")
        with self.assertRaisesRegex(OSError, "fixture interrupted transaction"):
            with continuity.storage_transaction(self.paths[0]):
                identity = (lock.stat().st_dev, lock.stat().st_ino)
                raise OSError("fixture interrupted transaction")
        with continuity.storage_transaction(self.paths[0]):
            self.assertEqual((lock.stat().st_dev, lock.stat().st_ino), identity)
        self.assertTrue(lock.is_file())

    def test_invalid_transaction_path_creates_nothing(self):
        for event in (Path("."), Path(self.root.anchor), self.root / ".." / "events.jsonl"):
            with self.subTest(event=event):
                with self.assertRaises(continuity.ContinuityError) as error:
                    with continuity.storage_transaction(event):
                        self.fail("unconfined transaction path admitted")
                self.assertEqual(error.exception.code, "GOV-CONTINUITY-001")
        self.assertEqual(list(self.root.iterdir()), [])

    @unittest.skipUnless(os.name == "nt", "Windows native held lock handles")
    def test_windows_transaction_holds_parent_and_lock_against_replacement(self):
        parent = self.root / "sessions"
        event = parent / "events.jsonl"
        with continuity.storage_transaction(event):
            for target in (parent, parent / "events.jsonl.lock"):
                with self.subTest(target=target):
                    with self.assertRaises(OSError):
                        target.rename(self.root / "replacement")

    @unittest.skipUnless(os.name == "nt", "Windows native transaction junction boundary")
    def test_windows_junction_cannot_redirect_transaction_lock(self):
        foreign = self.root / "foreign"
        foreign.mkdir()
        link = self.root / "sessions"
        result = subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(foreign)],
                                capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.addCleanup(lambda: link.rmdir() if link.exists() else None)
        with self.assertRaises(continuity.ContinuityError):
            with continuity.storage_transaction(link / "events.jsonl"):
                self.fail("junction lock admitted")
        self.assertFalse((foreign / "events.jsonl.lock").exists())


    def stream_target(self):
        target = self.root / "foreign.jsonl"
        target.write_bytes(continuity.canonical_bytes(fixture_event()) + b"\n")
        return target, target.read_bytes()

    def symlink(self, link, target, directory=False):
        try:
            link.symlink_to(target, target_is_directory=directory)
        except OSError:
            if os.name == "nt":
                self.skipTest("Windows symlink creation privilege is unavailable")
            raise

    def assert_stream_denied(self, path, target, original):
        for operation in (lambda: continuity.append_event(path, fixture_event()),
                          lambda: list(continuity.iter_events(path))):
            with self.subTest(operation=operation):
                with self.assertRaises(continuity.ContinuityError) as error:
                    operation()
                self.assertEqual(error.exception.code, "GOV-CONTINUITY-001")
                self.assertEqual(target.read_bytes(), original)

    def test_checkpoint_commit_cannot_append_through_a_linked_stream(self):
        target, original = self.stream_target()
        self.symlink(self.paths[0], target)
        with self.assertRaises(continuity.ContinuityError) as error:
            continuity.commit_event(self.root, fixture_event("ticket-002", "writer-002"))
        self.assertEqual(error.exception.code, "GOV-CONTINUITY-001")
        self.assertEqual(target.read_bytes(), original)
        self.assertFalse(self.paths[1].exists())

    def test_event_file_symlink_cannot_redirect_read_or_append(self):
        target, original = self.stream_target()
        self.symlink(self.paths[0], target)
        self.assert_stream_denied(self.paths[0], target, original)

    def test_event_hardlink_cannot_redirect_read_or_append(self):
        target, original = self.stream_target()
        os.link(target, self.paths[0])
        self.assert_stream_denied(self.paths[0], target, original)

    def test_parent_symlink_cannot_redirect_read_or_append(self):
        target = self.root / "foreign" / "events.jsonl"
        target.parent.mkdir()
        target.write_bytes(continuity.canonical_bytes(fixture_event()) + b"\n")
        original = target.read_bytes()
        link = self.root / "sessions"
        self.symlink(link, target.parent, directory=True)
        self.assert_stream_denied(link / target.name, target, original)

    def test_dangling_symlink_is_rejected_without_creating_foreign_file(self):
        target = self.root / "missing-foreign.jsonl"
        self.symlink(self.paths[0], target)
        with self.assertRaises(continuity.ContinuityError):
            continuity.append_event(self.paths[0], fixture_event())
        with self.assertRaises(continuity.ContinuityError):
            list(continuity.iter_events(self.paths[0]))
        self.assertFalse(target.exists())

    @unittest.skipUnless(os.name == "posix", "POSIX descriptor substitution boundary")
    def test_last_component_substitution_is_rejected_before_writing(self):
        target, original = self.stream_target()
        self.paths[0].write_bytes(b"")
        real_open = os.open
        swapped = []
        def substitute(path, flags, *args, **kwargs):
            if Path(path).name == self.paths[0].name and not swapped:
                self.paths[0].unlink()
                self.paths[0].symlink_to(target)
                swapped.append(True)
            return real_open(path, flags, *args, **kwargs)
        with patch.object(continuity.os, "open", side_effect=substitute):
            with self.assertRaises(continuity.ContinuityError):
                continuity.append_event(self.paths[0], fixture_event())
        self.assertEqual(swapped, [True])
        self.assertEqual(target.read_bytes(), original)

    @unittest.skipUnless(os.name == "posix", "POSIX safe-open capability boundary")
    def test_missing_no_follow_capability_fails_before_creating_stream(self):
        with patch.object(continuity.os, "O_NOFOLLOW", None):
            with self.assertRaises(continuity.ContinuityError):
                continuity.append_event(self.paths[0], fixture_event())
        self.assertFalse(self.paths[0].exists())

    @unittest.skipUnless(os.name == "nt", "Windows native junction boundary")
    def test_windows_junction_cannot_redirect_read_or_append(self):
        target = self.root / "foreign" / "events.jsonl"
        target.parent.mkdir()
        target.write_bytes(continuity.canonical_bytes(fixture_event()) + b"\n")
        link = self.root / "sessions"
        result = subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(target.parent)],
                                capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.addCleanup(lambda: link.rmdir() if link.exists() else None)
        self.assert_stream_denied(link / target.name, target, target.read_bytes())

    def test_regular_stream_preserves_exact_append_and_absent_read(self):
        absent = self.root / "absent" / "deeper" / "events.jsonl"
        self.assertEqual(list(continuity.iter_events(absent)), [])
        self.assertFalse(absent.parent.exists())
        events = [fixture_event(), fixture_event("ticket-002", "writer-002")]
        for event in events:
            continuity.append_event(self.paths[0], event)
        self.assertEqual(self.paths[0].read_bytes(), b"".join(
            continuity.canonical_bytes(event) + b"\n" for event in events))
        self.assertEqual(list(continuity.iter_events(self.paths[0])), events)
        with self.assertRaises(continuity.ContinuityError):
            continuity.append_event(self.root, fixture_event())


class CompactRoutineIntentContinuityTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)
        subprocess.run(["git", "-C", str(self.root), "init", "--quiet"], check=True)
        (self.root / ".governance").mkdir()
        (self.root / "project" / "ticket-001").mkdir(parents=True)

    def write_manifest(self, target_branches):
        manifest = {
            "schema": "new-project.governance/v2",
            "delivery": {"targetBranches": target_branches},
        }
        (self.root / ".governance" / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    def test_compact_routine_intent_resolves_unique_manifest_target_branch(self):
        self.write_manifest(["main"])
        intent = {
            "schema": "new-project.intent/v3",
            "ticket": "ticket-001",
            "summary": "compact routine intent",
            "workstream": "governance",
            "classification": {"kind": "FEATURE", "priority": "P2", "origin": "requested"},
            "allowedPaths": ["src/**"],
            "forbiddenPaths": [],
            "stacks": [],
            "dependsOn": [],
            "conflictsWith": [],
            "integrationTicket": None,
        }
        intent_raw = json.dumps(intent, indent=2).encode("utf-8")
        (self.root / "project" / "ticket-001" / "intent.json").write_bytes(intent_raw)
        import hashlib
        val, raw_digest, scope_digest, target_branch = continuity.intent_state(self.root, "ticket-001")
        self.assertEqual(target_branch, "main")
        self.assertEqual(raw_digest, hashlib.sha256(intent_raw).hexdigest())

    def test_full_delivery_intent_preserves_explicit_target_branch(self):
        self.write_manifest(["main"])
        intent = {
            "schema": "new-project.intent/v3",
            "ticket": "ticket-001",
            "summary": "full delivery intent",
            "workstream": "governance",
            "classification": {"kind": "FEATURE", "priority": "P2", "origin": "requested"},
            "allowedPaths": ["src/**"],
            "forbiddenPaths": [],
            "stacks": [],
            "dependsOn": [],
            "conflictsWith": [],
            "integrationTicket": None,
            "delivery": {
                "acceptedBaseSha": "0" * 40,
                "targetBranch": "release-1.0",
                "outcome": "deliver feature",
                "nonGoals": [],
            },
        }
        (self.root / "project" / "ticket-001" / "intent.json").write_text(json.dumps(intent), encoding="utf-8")
        val, raw_digest, scope_digest, target_branch = continuity.intent_state(self.root, "ticket-001")
        self.assertEqual(target_branch, "release-1.0")

    def test_compact_routine_intent_fails_closed_on_ambiguous_manifest_targets(self):
        self.write_manifest(["main", "develop"])
        intent = {
            "schema": "new-project.intent/v3",
            "ticket": "ticket-001",
            "summary": "compact routine intent",
            "workstream": "governance",
            "classification": {"kind": "FEATURE", "priority": "P2", "origin": "requested"},
            "allowedPaths": ["src/**"],
        }
        (self.root / "project" / "ticket-001" / "intent.json").write_text(json.dumps(intent), encoding="utf-8")
        with self.assertRaises(continuity.ContinuityError) as ctx:
            continuity.intent_state(self.root, "ticket-001")
        self.assertEqual(ctx.exception.code, "GOV-CONTINUITY-001")

    def test_compact_routine_intent_fails_closed_on_missing_manifest(self):
        intent = {
            "schema": "new-project.intent/v3",
            "ticket": "ticket-001",
            "summary": "compact routine intent",
            "workstream": "governance",
            "classification": {"kind": "FEATURE", "priority": "P2", "origin": "requested"},
            "allowedPaths": ["src/**"],
        }
        (self.root / "project" / "ticket-001" / "intent.json").write_text(json.dumps(intent), encoding="utf-8")
        with self.assertRaises(continuity.ContinuityError) as ctx:
            continuity.intent_state(self.root, "ticket-001")
        self.assertEqual(ctx.exception.code, "GOV-CONTINUITY-001")


if __name__ == "__main__":
    unittest.main()
