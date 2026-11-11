"""Regressions for v0.20.146 governance hardening and merge-driver auto-wiring (ticket-427)."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / "scripts"))


def _load_module(name: str, relative: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _git(cwd: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(
        GIT_AUTHOR_NAME="v146-fixture",
        GIT_AUTHOR_EMAIL="v146@example.invalid",
        GIT_COMMITTER_NAME="v146-fixture",
        GIT_COMMITTER_EMAIL="v146@example.invalid",
    )
    return subprocess.run(
        ["git", "-C", str(cwd), *args],
        env=env,
        capture_output=True,
        text=True,
        check=check,
    )


class GovernanceV146RegressionsTest(unittest.TestCase):
    def test_item1_ticket_recovery_controller_lock_contextmanager(self):
        import ticket_recovery

        with tempfile.TemporaryDirectory() as td:
            store = Path(td)
            (store / ".lock").write_bytes(b"")
            entered = False
            with ticket_recovery.controller_lock(store):
                entered = True
                with self.assertRaises(BlockingIOError):
                    with ticket_recovery.controller_lock(store):
                        pass
            self.assertTrue(entered)

    def test_item2_windows_stream_descriptor_uses_wronly_with_append(self):
        import ctypes
        import work_continuity

        fake_api = MagicMock()
        fake_api.CreateFileW.return_value = 42

        def fake_get_info(handle, info_ptr):
            # First two calls are directories (C:\ and C:\repo), third is regular file
            is_dir = fake_get_info.calls < 2
            fake_get_info.calls += 1
            info_ptr._obj.attributes = 0x10 if is_dir else 0x80
            info_ptr._obj.links = 1
            return True

        fake_get_info.calls = 0
        fake_api.GetFileInformationByHandle.side_effect = fake_get_info
        fake_msvcrt = MagicMock()
        captured_flags: list[int] = []

        def fake_open_osfhandle(handle: int, flags: int) -> int:
            captured_flags.append(flags)
            r_fd, w_fd = os.pipe()
            os.close(r_fd)
            return w_fd

        fake_msvcrt.open_osfhandle.side_effect = fake_open_osfhandle

        class FakeWinPath:
            anchor = "C:\\"
            parts = ("C:\\", "repo", "events.jsonl")

            def __str__(self) -> str:
                return "C:\\repo\\events.jsonl"

        with patch.dict(sys.modules, {"msvcrt": fake_msvcrt}), \
                patch.object(ctypes, "WinDLL", return_value=fake_api, create=True), \
                patch.object(work_continuity.os, "O_BINARY", 0x8000, create=True), \
                patch.object(work_continuity.os, "O_NOINHERIT", 0x0080, create=True):
            with work_continuity._windows_stream_descriptor(FakeWinPath(), append=True, readwrite=False) as fd:  # type: ignore[arg-type]
                self.assertIsInstance(fd, int)
        self.assertEqual(len(captured_flags), 1)
        self.assertEqual(captured_flags[0] & (os.O_WRONLY | os.O_APPEND), os.O_WRONLY | os.O_APPEND)
        self.assertNotEqual(captured_flags[0] & os.O_WRONLY, 0)

    def test_item3_reusable_workflows_schema_regexes_match_literal_dots(self):
        schema = json.loads((ROOT / "governance/reusable-workflows.schema.json").read_text(encoding="utf-8"))
        item_props = schema["properties"]["workflows"]["items"]["properties"]
        uses_re = re.compile(item_props["uses"]["pattern"])
        source_re = re.compile(item_props["sourceFile"]["pattern"])
        sha = "a" * 40
        self.assertIsNotNone(uses_re.fullmatch(f"wellmanifest/new-project/.github/workflows/ci.yml@{sha}"))
        self.assertIsNone(uses_re.fullmatch(f"wellmanifest/new-project/xgithub/workflows/ci.yml@{sha}"))
        self.assertIsNone(uses_re.fullmatch(f"wellmanifest/new-project/\\.github/workflows/ci.yml@{sha}"))
        self.assertIsNotNone(source_re.fullmatch(".github/reusable-workflows/ci.yaml"))
        self.assertIsNone(source_re.fullmatch("xgithub/reusable-workflows/ci.yaml"))
        self.assertIsNone(source_re.fullmatch("\\.github/reusable-workflows/ci.yaml"))

    def test_item4_branch_lifecycle_require_ref_rejects_single_at(self):
        import branch_lifecycle_check as blc

        with self.assertRaises(blc.SnapshotError):
            blc.require_ref("@", "ref")
        with self.assertRaises(blc.SnapshotError):
            blc.require_ref("HEAD", "ref")
        self.assertEqual(blc.require_ref("ticket/427-harden", "ref"), "ticket/427-harden")

    def test_item5a_check_history_order_validates_historical_intent_schema(self):
        for idx, rel_mod in enumerate(
            (
                "scripts/governance_check.py",
                "packages/wellman/src/wellman/_bundled/governance_check.py",
            )
        ):
            mod = _load_module(f"gov_v146_hist_{idx}", rel_mod)
            with tempfile.TemporaryDirectory() as td:
                repo = Path(td)
                _git(repo, "init", "-q", "-b", "main")
                _git(repo, "config", "commit.gpgsign", "false")
                (repo / "app.py").write_text("x = 1\n", encoding="utf-8")
                _git(repo, "add", ".")
                _git(repo, "commit", "-qm", "base")
                base = _git(repo, "rev-parse", "HEAD").stdout.strip()

                # First material commit has syntactically valid JSON `{}` in intent.json,
                # which fails validate_intent_value and must emit GOV-INTENT-003.
                (repo / "project/ticket-001").mkdir(parents=True)
                (repo / "project/ticket-001/intent.json").write_text("{}\n", encoding="utf-8")
                (repo / "app.py").write_text("x = 2\n", encoding="utf-8")
                _git(repo, "add", ".")
                _git(repo, "commit", "-qm", "material with invalid historical intent")
                bad_commit = _git(repo, "rev-parse", "HEAD").stdout.strip()

                valid_intent = {
                    "schema": "new-project.intent/v3",
                    "ticket": "ticket-001",
                    "summary": "Later repaired intent",
                    "workstream": "governance",
                    "classification": {"kind": "BUG", "priority": "P1", "origin": "health"},
                    "allowedPaths": ["project/ticket-001/**", "app.py"],
                    "forbiddenPaths": ["project/ticket-*/user-*.md"],
                    "stacks": [],
                    "dependsOn": [],
                    "conflictsWith": [],
                    "integrationTicket": None,
                }
                (repo / "project/ticket-001/intent.json").write_text(json.dumps(valid_intent), encoding="utf-8")
                _git(repo, "add", ".")
                _git(repo, "commit", "-qm", "repair intent later")

                report = mod.Report(repo)
                mod.check_history_order(
                    repo, base, "HEAD", "ticket-001", "project", "intent.json", ["project/**"], report
                )
                codes = [f.code for f in report.findings]
                self.assertEqual(codes, ["GOV-INTENT-003"], rel_mod)
                self.assertEqual(report.findings[0].evidence["firstImplementationCommit"], bad_commit)

    def test_item5b_version_parity_rejects_symlink_init_and_bounds_size(self):
        for idx, rel_mod in enumerate(
            (
                "scripts/governance_check.py",
                "packages/wellman/src/wellman/_bundled/governance_check.py",
            )
        ):
            mod = _load_module(f"gov_v146_ver_{idx}", rel_mod)
            with tempfile.TemporaryDirectory() as outer_td:
                outer = Path(outer_td)
                outside_secret = outer / "outside_init.py"
                outside_secret.write_text('__version__ = "9.9.9"\n', encoding="utf-8")

                repo = outer / "repo"
                (repo / "src/pkg").mkdir(parents=True)
                (repo / "VERSION").write_text("1.0.0\n", encoding="utf-8")
                os.symlink(outside_secret, repo / "src/pkg/__init__.py")

                report = mod.Report(repo)
                mod.check_version_parity(repo, {}, report)
                self.assertEqual([f.code for f in report.findings], ["GOV-VERSION-001"], rel_mod)
                self.assertIn("Symlinked", report.findings[0].message)

                # Replace symlink with oversized (>1 MiB) regular file: must not read unbounded content.
                (repo / "src/pkg/__init__.py").unlink()
                (repo / "src/pkg/__init__.py").write_bytes(b"# " + (b"x" * (1024 * 1024 + 64)) + b'\n__version__ = "9.9.9"\n')
                report2 = mod.Report(repo)
                mod.check_version_parity(repo, {}, report2)
                self.assertEqual(report2.findings, [], rel_mod)

    def test_item5c_legacy_base_requires_absent_base_package_manifest(self):
        for idx, rel_mod in enumerate(
            (
                "scripts/governance_check.py",
                "packages/wellman/src/wellman/_bundled/governance_check.py",
            )
        ):
            mod = _load_module(f"gov_v146_legacy_{idx}", rel_mod)
            with tempfile.TemporaryDirectory() as td:
                repo = Path(td)
                _git(repo, "init", "-q", "-b", "main")
                _git(repo, "config", "commit.gpgsign", "false")
                from_rev = "1" * 40
                to_rev = "2" * 40
                pkg_manifest = {
                    "schema": "new-project.package-manifest/v1",
                    "files": [
                        {"source": "a.py", "target": ".governance/a.py", "strategy": "managed", "executable": False},
                        {"source": "b.py", "target": ".governance/b.py", "strategy": "managed", "executable": False},
                    ],
                }
                # Base has a package-manifest declaring both a.py and b.py as managed,
                # but base lock only lists a.py (strict subset) -> must be rejected!
                gov_dir = repo / ".governance"
                gov_dir.mkdir(parents=True)
                (gov_dir / "package-manifest.json").write_text(json.dumps(pkg_manifest), encoding="utf-8")
                partial_base_lock = {
                    "schema": "new-project.lock/v1",
                    "standard": {
                        "id": "wellmanifest/new-project",
                        "version": "0.20.145",
                        "sourceRepository": "wellmanifest/new-project",
                        "sourceRevision": from_rev,
                        "publicationStatus": "published",
                    },
                    "managedFiles": {".governance/a.py": "a" * 64},
                }
                (gov_dir / "manifest.lock.json").write_text(json.dumps(partial_base_lock), encoding="utf-8")
                _git(repo, "add", ".")
                _git(repo, "commit", "-qm", "base with partial lock")
                base_sha = _git(repo, "rev-parse", "HEAD").stdout.strip()

                full_head_lock = {
                    "schema": "new-project.lock/v1",
                    "standard": {
                        "id": "wellmanifest/new-project",
                        "version": "0.20.146",
                        "sourceRepository": "wellmanifest/new-project",
                        "sourceRevision": to_rev,
                        "publicationStatus": "published",
                    },
                    "managedFiles": {
                        ".governance/a.py": "a" * 64,
                        ".governance/b.py": "b" * 64,
                    },
                }
                (gov_dir / "manifest.lock.json").write_text(json.dumps(full_head_lock), encoding="utf-8")

                adoption = {"fromRevision": from_rev, "toRevision": to_rev}
                with self.assertRaisesRegex(ValueError, "base package targets and lock targets differ"):
                    mod.load_standard_adoption_evidence(repo, base_sha, adoption)

    def test_item6_policy_dsl_variable_default_types_and_duplicate_document_fences(self):
        import policy_dsl_check as dsl

        header = "DOCUMENT TEST\nVERSION 1\nMODE STRICT\n"
        valid_cases = (
            'VARIABLE S TYPE STRING FROM ENV DEFAULT "ok"',
            "VARIABLE I TYPE INTEGER FROM ENV DEFAULT 42",
            "VARIABLE N TYPE NUMBER FROM ENV DEFAULT 3.5",
            "VARIABLE B TYPE BOOLEAN FROM ENV DEFAULT FALSE",
            'VARIABLE U TYPE URL FROM ENV DEFAULT "https://example.com/x"',
            'VARIABLE P TYPE PATH FROM ENV DEFAULT "scripts/check.py"',
        )
        for decl in valid_cases:
            ir = dsl.parse(header + decl + "\n")
            dsl.validate_ir(ir)

        invalid_cases = (
            'VARIABLE I TYPE INTEGER FROM ENV DEFAULT "42"',
            "VARIABLE I TYPE INTEGER FROM ENV DEFAULT 3.5",
            "VARIABLE I TYPE INTEGER FROM ENV DEFAULT TRUE",
            'VARIABLE B TYPE BOOLEAN FROM ENV DEFAULT "false"',
            "VARIABLE B TYPE BOOLEAN FROM ENV DEFAULT 1",
            "VARIABLE N TYPE NUMBER FROM ENV DEFAULT TRUE",
            'VARIABLE U TYPE URL FROM ENV DEFAULT "not-a-url"',
            'VARIABLE P TYPE PATH FROM ENV DEFAULT ""',
            "VARIABLE P TYPE PATH FROM ENV DEFAULT 10",
        )
        for decl in invalid_cases:
            with self.subTest(decl=decl):
                with self.assertRaises(dsl.PolicyError) as ctx:
                    dsl.parse(header + decl + "\n")
                self.assertEqual(ctx.exception.code, "POLICY-SEMANTIC-001")

        # Duplicate embedded Policy DSL DOCUMENT fences must fail closed.
        dup_md = (
            "# Policy\n\n```dsl\nDOCUMENT FIRST\nVERSION 1\nMODE STRICT\n```\n\n"
            "```dsl\nDOCUMENT SECOND\nSCHEMA \"wellmanifest.policy/v1\"\nVERSION 1\nMODE STRICT\n```\n"
        )
        with self.assertRaises(dsl.PolicyError) as dup_ctx:
            dsl.extract_markdown(dup_md)
        self.assertEqual(dup_ctx.exception.code, "POLICY-SYNTAX-001")

        # Independent non-policy embedded DOCUMENT fences remain allowed.
        indep_md = (
            "# Policy\n\n```dsl\nDOCUMENT FIRST\nVERSION 1\nMODE STRICT\n```\n\n"
            "```dsl\nDOCUMENT OTHER\nSCHEMA \"other.contract/v1\"\n```\n"
        )
        extracted = dsl.extract_markdown(indep_md)
        self.assertIn("DOCUMENT FIRST", extracted)
        self.assertNotIn("DOCUMENT OTHER", extracted)

    def test_item7_remediation_intent_criterion_coverage_is_case_insensitive(self):
        import remediation_intent

        doc = {
            "acceptanceCriteria": [
                {"id": "AC-01", "statement": "Preserve Exact Lease Fencing"},
            ]
        }
        findings: list[dict[str, object]] = []
        remediation_intent._analyze_criterion_coverage(
            doc,
            {"plan": "Step 1: preserve EXACT lease FENCING across restarts."},
            findings,
        )
        self.assertEqual(findings, [])

    def test_item8_standard_pack_external_evidence_rejects_windows_drive_letters(self):
        import standard_pack_check as spc

        self.assertIsNone(spc.EXTERNAL_EVIDENCE.match(r"C:\secret\file.txt"))
        self.assertIsNone(spc.EXTERNAL_EVIDENCE.match("D:/secret/file.txt"))
        self.assertIsNotNone(spc.EXTERNAL_EVIDENCE.match("https://example.com/proof"))
        with tempfile.TemporaryDirectory() as td:
            self.assertFalse(
                spc.evidence_proves(Path(td), {"uri": r"C:\secret\file.txt", "sha256": "0" * 64})
            )

    def test_item9_bootstrap_owned_paths_detects_end_of_check_mutation(self):
        import work_start_check as wsc

        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            _git(repo, "init", "-q", "-b", "main")
            _git(repo, "config", "commit.gpgsign", "false")
            (repo / "README.md").write_text("hello\n", encoding="utf-8")
            _git(repo, "add", "README.md")
            _git(repo, "commit", "-qm", "init")
            head = _git(repo, "rev-parse", "HEAD").stdout.strip()
            common = _git(repo, "rev-parse", "--path-format=absolute", "--git-common-dir").stdout.strip()

            gov = repo / ".governance"
            gov.mkdir()
            target_file = gov / "sample.txt"
            target_bytes = b"managed-content\n"
            target_sha = hashlib.sha256(target_bytes).hexdigest()
            target_file.write_bytes(target_bytes)

            pkg = {
                "schema": "new-project.package-manifest/v1",
                "files": [
                    {"source": "sample.txt", "target": ".governance/sample.txt", "strategy": "managed", "executable": False},
                    {"source": "package-manifest.json", "target": ".governance/package-manifest.json", "strategy": "managed", "executable": False},
                ],
            }
            pkg_bytes = json.dumps(pkg).encode("utf-8")
            pkg_sha = hashlib.sha256(pkg_bytes).hexdigest()
            (gov / "package-manifest.json").write_bytes(pkg_bytes)

            rev = "a" * 40
            lock = {
                "schema": "new-project.lock/v1",
                "standard": {
                    "id": "wellmanifest/new-project",
                    "version": "0.20.146",
                    "sourceRepository": "wellmanifest/new-project",
                    "sourceRevision": rev,
                    "publicationStatus": "published",
                },
                "managedFiles": {
                    ".governance/sample.txt": target_sha,
                    ".governance/package-manifest.json": pkg_sha,
                },
            }
            lock_bytes = json.dumps(lock).encode("utf-8")
            lock_sha = hashlib.sha256(lock_bytes).hexdigest()
            (gov / "manifest.lock.json").write_bytes(lock_bytes)

            receipt_dir = repo / ".subactor/receipts"
            receipt_dir.mkdir(parents=True)
            receipt = {
                "schema": "new-project.bootstrap-adoption/v1",
                "baseSha": head,
                "commonGitDir": common,
                "bootstrapKind": "fresh",
                "sourceRevision": rev,
                "grantsWriterAuthority": False,
                "grantsPublicationAuthority": False,
                "files": {
                    ".governance/sample.txt": target_sha,
                    ".governance/package-manifest.json": pkg_sha,
                    ".governance/manifest.lock.json": lock_sha,
                },
            }
            (receipt_dir / "bootstrap-adoption.json").write_text(json.dumps(receipt), encoding="utf-8")
            (repo / ".gitignore").write_text(".subactor/\n", encoding="utf-8")
            gitignore_sha = hashlib.sha256((repo / ".gitignore").read_bytes()).hexdigest()
            receipt["files"][".gitignore"] = gitignore_sha
            (receipt_dir / "bootstrap-adoption.json").write_text(json.dumps(receipt), encoding="utf-8")

            _, expected_digest, _ = wsc.dirty_observation(repo)
            manifest = {"requiredFiles": ["README.md"]}
            self.assertIn(".governance/sample.txt", wsc.bootstrap_owned_paths(repo, manifest, expected_digest))

            # Simulate file mutation right during the end-of-proof worktrees() check.
            orig_worktrees = wsc.worktrees
            calls = 0

            def mutating_worktrees(r):
                nonlocal calls
                calls += 1
                res = orig_worktrees(r)
                if calls == 2:
                    target_file.write_bytes(b"tampered\n")
                return res

            with patch.object(wsc, "worktrees", side_effect=mutating_worktrees):
                with self.assertRaisesRegex(wsc.ObservationError, "Bootstrap changed during admission"):
                    wsc.bootstrap_owned_paths(repo, manifest, expected_digest)

    def test_item10_ticket_restoration_write_new_stages_in_destination_parent(self):
        import ticket_restoration

        mkstemp_dirs: list[Path] = []
        orig_mkstemp = tempfile.mkstemp

        def spy_mkstemp(*args, **kwargs):
            mkstemp_dirs.append(Path(kwargs["dir"]))
            return orig_mkstemp(*args, **kwargs)

        with tempfile.TemporaryDirectory() as common_td, tempfile.TemporaryDirectory() as dest_td:
            dest = Path(dest_td) / "README.md"
            with patch.object(ticket_restoration.tempfile, "mkstemp", side_effect=spy_mkstemp):
                ticket_restoration.write_new(Path(common_td), dest, "# Restored\n")
            self.assertEqual(dest.read_text(encoding="utf-8"), "# Restored\n")
            self.assertEqual(mkstemp_dirs, [dest.parent])
            self.assertEqual(list(dest.parent.iterdir()), [dest])

    def test_item11_idle_takeover_rechecks_activity_under_lock_before_replace(self):
        runtime = _load_module("idle_v146_runtime", "scripts/idle_takeover.py")
        with tempfile.TemporaryDirectory() as td:
            primary = Path(td).resolve() / "repo"
            primary.mkdir()
            _git(primary, "init", "-q", "-b", "main")
            _git(primary, "config", "commit.gpgsign", "false")
            _git(primary, "remote", "add", "origin", "git@github.com:example/fixture.git")
            (primary / "README.md").write_text("fixture\n", encoding="utf-8")
            _git(primary, "add", "README.md")
            _git(primary, "commit", "-qm", "base")

            wt_id = "ticket-001--fixture"
            branch = "ticket/001-fixture"
            wt = primary / ".worktrees" / wt_id
            _git(primary, "worktree", "add", "-q", "-b", branch, str(wt))
            (wt / "work.txt").write_text("work\n", encoding="utf-8")
            _git(wt, "add", "work.txt")
            _git(wt, "commit", "-qm", "work")

            issued = datetime.now(timezone.utc) - timedelta(hours=1)
            now = datetime.now(timezone.utc) + timedelta(minutes=20)
            lease_path = primary / ".subactor/leases" / f"{wt_id}.json"
            lease_path.parent.mkdir(parents=True, exist_ok=True)
            lease = {
                "schema": "wellmanifest.change-lease/v1",
                "leaseId": "allocation-ticket-001-fixture",
                "repositoryRef": "example/fixture",
                "targetBranch": "main",
                "ticketId": "ticket-001",
                "workstream": "governance",
                "scopeHash": "1" * 64,
                "branchRef": f"refs/heads/{branch}",
                "worktreeId": wt_id,
                "ownerActor": "agent:previous",
                "ownerSession": "session-previous",
                "phase": "claimed",
                "leaseRevision": 1,
                "fencingToken": 1,
                "issuedAt": runtime.stamp(issued),
                "expiresAt": runtime.stamp(issued + timedelta(hours=2)),
                "heartbeatAt": runtime.stamp(issued),
                "headSha": None,
                "pullRequest": None,
                "validatorRunId": None,
                "publicationFrozen": False,
                "planHash": "2" * 64,
                "previousReceiptRef": None,
                "eventSequence": 1,
            }
            lease_path.write_text(json.dumps(lease), encoding="utf-8")
            gov = primary / ".governance"
            gov.mkdir()
            (gov / "manifest.json").write_text(
                json.dumps({"coordination": {"idleTakeover": {"enabled": True, "idleMinutes": 15, "leaseMinutes": 120}}}),
                encoding="utf-8",
            )

            # Simulate worker resuming dirty-file activity during prepare I/O without touching lease_path bytes!
            orig_write_atomic = runtime.write_atomic

            def concurrent_activity_on_prepare(path: Path, data: bytes) -> None:
                orig_write_atomic(path, data)
                if path.name.endswith(".prepared.json"):
                    dirty = wt / "resumed.txt"
                    dirty.write_text("worker resumed\n", encoding="utf-8")
                    fresh_ts = now.timestamp()
                    os.utime(dirty, (fresh_ts, fresh_ts))

            with patch.object(runtime, "write_atomic", side_effect=concurrent_activity_on_prepare):
                with self.assertRaises(PermissionError):
                    runtime.takeover(primary, "ticket-001", "agent:next", "session-next", now)
            self.assertEqual(json.loads(lease_path.read_text(encoding="utf-8"))["ownerActor"], "agent:previous")

    def test_item12_new_ticket_default_writer_session_has_pid_and_random_hex_suffix(self):
        new_ticket = (ROOT / "project/new-ticket.sh").read_text(encoding="utf-8")
        self.assertIn("secrets.token_hex", new_ticket)
        out1 = subprocess.check_output(
            ["bash", "-c", 'echo "allocation-$(date -u +"%Y-%m-%dT%H:%M:%SZ")-$$-$(python3 -c \'import secrets; print(secrets.token_hex(4))\')"'],
            text=True,
        ).strip()
        out2 = subprocess.check_output(
            ["bash", "-c", 'echo "allocation-$(date -u +"%Y-%m-%dT%H:%M:%SZ")-$$-$(python3 -c \'import secrets; print(secrets.token_hex(4))\')"'],
            text=True,
        ).strip()
        self.assertNotEqual(out1, out2)
        self.assertRegex(out1, r"^allocation-[0-9T:\-]+Z-[0-9]+-[0-9a-f]{8}$")

    def test_item13_install_agent_hosts_autowires_ticket_index_merge_drivers_idempotently(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td)
            _git(target, "init", "-q", "-b", "main")
            _git(target, "config", "commit.gpgsign", "false")
            _git(target, "config", "core.autocrlf", "false")
            shutil.copytree(ROOT / ".githooks", target / ".githooks")
            (target / ".governance").mkdir()
            shutil.copy2(ROOT / "scripts/ticket_index_merge_driver.py", target / ".governance/ticket_index_merge_driver.py")
            subprocess.run(
                [
                    "bash",
                    str(ROOT / "scripts/install-agent-hosts.sh"),
                    "--source",
                    str(ROOT),
                    "--target",
                    str(target),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            # Re-run in-place to verify idempotency.
            (target / "scripts").mkdir(exist_ok=True)
            shutil.copy2(ROOT / "scripts/install-agent-hosts.sh", target / "scripts/install-agent-hosts.sh")
            subprocess.run(["bash", "scripts/install-agent-hosts.sh"], cwd=target, check=True, capture_output=True, text=True)

            for key in ("ticket-index", "wellmanifest-ticket-index"):
                drv = _git(target, "config", "--local", "--get", f"merge.{key}.driver").stdout.strip()
                self.assertEqual(drv, "python3 .governance/ticket_index_merge_driver.py %O %A %B")

            # Verify a real 3-way Git merge of project/TICKETS.md with `merge=ticket-index` succeeds cleanly!
            (target / ".gitattributes").write_text("project/TICKETS.md merge=ticket-index\n", encoding="utf-8")
            (target / "project").mkdir()
            base_table = (
                "# Tickets\n\n<!-- AUTO:TICKET_INDEX:START -->\n"
                "| Ticket ID | Spec |\n| :--- | :--- |\n"
                "| **ticket-001** | a |\n"
                "<!-- AUTO:TICKET_INDEX:END -->\n"
            )
            (target / "project/TICKETS.md").write_text(base_table, encoding="utf-8")
            _git(target, "add", ".")
            _git(target, "commit", "--no-verify", "-qm", "base")

            _git(target, "checkout", "-qb", "worker-b")
            (target / "project/TICKETS.md").write_text(
                base_table.replace("<!-- AUTO:TICKET_INDEX:END -->", "| **ticket-003** | c |\n<!-- AUTO:TICKET_INDEX:END -->"),
                encoding="utf-8",
            )
            _git(target, "commit", "--no-verify", "-qam", "worker-b append")

            _git(target, "checkout", "-q", "main")
            (target / "project/TICKETS.md").write_text(
                base_table.replace("<!-- AUTO:TICKET_INDEX:END -->", "| **ticket-002** | b |\n<!-- AUTO:TICKET_INDEX:END -->"),
                encoding="utf-8",
            )
            _git(target, "commit", "--no-verify", "-qam", "worker-a append")

            merge_res = _git(target, "merge", "--no-verify", "--no-edit", "worker-b", check=False)
            self.assertEqual(merge_res.returncode, 0, merge_res.stderr)
            merged = (target / "project/TICKETS.md").read_text(encoding="utf-8")
            self.assertIn("**ticket-002**", merged)
            self.assertIn("**ticket-003**", merged)
            self.assertLess(merged.index("**ticket-002**"), merged.index("**ticket-003**"))


if __name__ == "__main__":
    unittest.main()
