#!/usr/bin/env python3
"""Integration coverage for canonical file-backed ticket allocation."""

from __future__ import annotations

import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from adoption_upgrade_harmonization_test import AdoptionPlanFixture

ROOT = Path(__file__).resolve().parents[1]


class TicketAllocationWorktreeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="new-project-ticket-allocation-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "repository"
        self.root.mkdir()
        self.git("init", "-b", "main")
        self.git("config", "user.name", "Fixture")
        self.git("config", "user.email", "fixture@example.invalid")
        self.git("config", "core.excludesFile", os.devnull)
        (self.root / "project").mkdir()
        (self.root / ".governance").mkdir()
        shutil.copy2(ROOT / "project/new-ticket.sh", self.root / "project/new-ticket.sh")
        shutil.copy2(ROOT / "project/readme.sh", self.root / "project/readme.sh")
        shutil.copytree(ROOT / "template/files", self.root / "template/files")
        for name in ("manifest.default.json", "work-classification.dsl.json", "ticket-activity.json"):
            source = ROOT / "governance" / name
            target = self.root / ".governance" / ("manifest.json" if name == "manifest.default.json" else name)
            shutil.copy2(source, target)
        for name in ("ticket_activity.py", "ticket_input.py", "work_start_check.py", "worktree_overlap_check.py",
                     "ticket_storage.py", "governance_check.py", "repository_policy.py"):
            shutil.copy2(ROOT / "scripts" / name, self.root / ".governance" / name)
        shutil.copy2(ROOT / "subprojects/worktrees/conformance.py", self.root / ".governance/worktree_path_check.py")
        (self.root / ".gitignore").write_text("/.worktrees/\n/.subactor/leases/\n", encoding="utf-8")
        (self.root / "README.md").write_text("fixture\n", encoding="utf-8")
        self.git("add", ".")
        self.git("commit", "-m", "fixture baseline")

    def git(self, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
        return subprocess.run(["git", *args], cwd=self.root, check=check, text=True,
                              capture_output=True, env={key: value for key, value in os.environ.items()
                                                         if not key.startswith("GIT_")})

    def allocate(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["bash", "project/new-ticket.sh", "--title", "Canonical ticket", "--agent", "codex",
             "--writer-actor", "agent:codex", "--writer-session", "session-fixture",
             "--workstream", "application", "--worktree-slug", "canonical-ticket", *args],
            cwd=self.root, text=True, capture_output=True,
            env={key: value for key, value in os.environ.items() if not key.startswith("GIT_")},
        )

    def test_file_ticket_is_created_only_in_canonical_linked_worktree(self) -> None:
        result = self.allocate()
        self.assertEqual(result.returncode, 0, result.stderr)
        receipts = [json.loads(line) for line in result.stdout.splitlines()
                    if line.startswith('{')]
        self.assertEqual(len(receipts), 1, result.stdout)
        receipt = receipts[0]
        self.assertEqual(receipt['schema'], 'new-project.ticket-allocation-result/v1')
        self.assertEqual(receipt['ticket'], 'ticket-001')
        self.assertEqual(receipt['branch'], 'ticket/001-canonical-ticket')
        self.assertEqual(receipt['worktreePath'], str(self.root / '.worktrees/ticket-001--canonical-ticket'))
        self.assertEqual(receipt['leasePath'], str(self.root / '.subactor/leases/ticket-001--canonical-ticket.json'))
        self.assertEqual(receipt['storage'], 'files')
        self.assertEqual(receipt['kind'], 'delivery')
        self.assertFalse(receipt['executionAuthorized'])
        worktree = self.root / ".worktrees/ticket-001--canonical-ticket"
        self.assertTrue(worktree.is_dir())
        self.assertFalse((self.root / "project/ticket-001").exists())
        self.assertTrue((worktree / "project/ticket-001/README.md").is_file())
        intent = json.loads((worktree / "project/ticket-001/intent.json").read_text(encoding="utf-8"))
        self.assertEqual(intent["ticket"], "ticket-001")
        self.assertEqual(self.git("-C", str(worktree), "branch", "--show-current").stdout.strip(),
                         "ticket/001-canonical-ticket")
        registration = (worktree / ".git").read_text(encoding="utf-8")
        self.assertNotIn(str(self.root), registration)
        self.assertEqual((self.root / ".git/new-project-ticket-high-water").read_text().strip(), "1")
        lease = self.root / ".subactor/leases/ticket-001--canonical-ticket.json"
        self.assertTrue(lease.is_file())
        payload = json.loads(lease.read_text(encoding="utf-8"))
        self.assertEqual(payload["ownerActor"], "agent:codex")
        self.assertEqual(payload["ownerSession"], "session-fixture")
        self.assertEqual(payload["ticketId"], "ticket-001")
        self.assertEqual(payload["branchRef"], "refs/heads/ticket/001-canonical-ticket")
        self.assertEqual(payload["worktreeId"], "ticket-001--canonical-ticket")
        verified = subprocess.run([sys.executable, str(ROOT / "scripts/change_lease_check.py"),
                                   "validate", str(lease)], text=True, capture_output=True)
        self.assertEqual(verified.returncode, 0, verified.stderr)
        self.assertEqual(self.git("status", "--porcelain").stdout, "")

    def test_invalid_or_missing_identity_has_no_effect(self):
        before = self.git("status", "--porcelain").stdout
        for actor, session in (("", ""), ("agent:codex", "bad session"), ("bad\nactor", "session")):
            result = subprocess.run(["bash", "project/new-ticket.sh", "--workstream", "application"],
                cwd=self.root, text=True, capture_output=True,
                env={**{k: v for k, v in os.environ.items() if not k.startswith("GIT_")},
                     "NEW_PROJECT_WRITER_ACTOR": actor, "NEW_PROJECT_WRITER_SESSION": session})
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("GOV-CHANGE-LEASE-001", result.stderr)
            self.assertFalse((self.root / ".git/new-project-ticket-high-water").exists())
            self.assertFalse((self.root / ".worktrees").exists())
            self.assertEqual(self.git("status", "--porcelain").stdout, before)

    def test_symlinked_canonical_component_fails_before_ticket_reservation(self) -> None:
        outside = Path(self.temp.name) / "outside"
        outside.mkdir()
        (self.root / ".worktrees").symlink_to(outside, target_is_directory=True)
        result = self.allocate()
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn('new-project.ticket-allocation-result/v1', result.stdout)
        self.assertFalse((self.root / "project/ticket-001").exists())
        self.assertFalse((self.root / ".git/new-project-ticket-high-water").exists())
        self.assertFalse((outside / "ticket-001--canonical-ticket").exists())

    def dirty_primary(self) -> dict[str, bytes]:
        (self.root / "src").mkdir()
        (self.root / "src/other.py").write_text("original\n")
        self.git("add", "src/other.py")
        self.git("commit", "-m", "tracked unrelated source")
        (self.root / "src/other.py").write_text("staged change\n")
        self.git("add", "src/other.py")
        (self.root / "src/other.py").write_text("unstaged change\n")
        (self.root / ".planfile").mkdir()
        (self.root / ".planfile/current.yaml").write_text("operational: unchanged\n")
        return {name: (self.root / name).read_bytes()
                for name in ("src/other.py", ".planfile/current.yaml", ".git/index")}

    def test_scoped_allocation_preserves_unrelated_dirty_primary(self) -> None:
        before = self.dirty_primary()
        status = self.git("status", "--porcelain=v1", "--untracked-files=all").stdout
        head = self.git("rev-parse", "HEAD").stdout.strip()
        result = self.allocate("--path", "src/fix.py")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        for name, content in before.items():
            self.assertEqual((self.root / name).read_bytes(), content, name)
        self.assertEqual(self.git("status", "--porcelain=v1", "--untracked-files=all").stdout, status)
        self.assertEqual(self.git("rev-parse", "HEAD").stdout.strip(), head)
        self.assertEqual(self.git("branch", "--show-current").stdout.strip(), "main")
        worktree = self.root / ".worktrees/ticket-001--canonical-ticket"
        self.assertEqual(self.git("-C", str(worktree), "rev-parse", "HEAD").stdout.strip(), head)
        self.assertEqual((worktree / "src/other.py").read_text(), "original\n")
        self.assertFalse((worktree / ".planfile/current.yaml").exists())

    def test_exact_primary_alias_preserves_dirty_bytes_and_allocates_target(self) -> None:
        before = self.dirty_primary()
        head = self.git("rev-parse", "HEAD").stdout.strip()
        self.git("update-ref", "refs/remotes/origin/main", head)
        self.git("checkout", "-b", "maintenance-alias")
        result = self.allocate("--path", "src/fix.py")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.git("branch", "--show-current").stdout.strip(), "maintenance-alias")
        self.assertEqual(self.git("rev-parse", "HEAD").stdout.strip(), head)
        for name, content in before.items():
            self.assertEqual((self.root / name).read_bytes(), content, name)
        worktree = self.root / ".worktrees/ticket-001--canonical-ticket"
        self.assertEqual(self.git("-C", str(worktree), "rev-parse", "HEAD").stdout.strip(), head)
        self.assertEqual((worktree / "src/other.py").read_text(), "original\n")

    def test_nonmatching_primary_alias_is_refused_before_reservation(self) -> None:
        head = self.git("rev-parse", "HEAD").stdout.strip()
        other = self.git("commit-tree", "HEAD^{tree}", "-p", head, "-m", "Other observed commit").stdout.strip()
        self.git("checkout", "-b", "maintenance-alias")
        for local, remote, detached in ((head, None, False), (head, other, False),
                                        (other, head, False), (head, head, True)):
            with self.subTest(local=local, remote=remote, detached=detached):
                self.git("update-ref", "refs/heads/main", local)
                if remote:
                    self.git("update-ref", "refs/remotes/origin/main", remote)
                else:
                    self.git("update-ref", "-d", "refs/remotes/origin/main")
                if detached:
                    self.git("checkout", "--detach", head)
                result = self.allocate("--path", "src/fix.py")
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("GOV-TICKET-ALLOCATION-003", result.stderr)
                self.assertFalse((self.root / ".git/new-project-ticket-high-water").exists())
                self.assertEqual(self.git("branch", "--list", "ticket/*").stdout, "")

    @unittest.skipUnless(os.name == "posix", "executable interpreter fixture")
    def test_alias_target_race_is_refused_before_reservation(self) -> None:
        head = self.git("rev-parse", "HEAD").stdout.strip()
        other = self.git("commit-tree", "HEAD^{tree}", "-p", head, "-m", "Changed target").stdout.strip()
        self.git("update-ref", "refs/remotes/origin/main", head)
        self.git("checkout", "-b", "maintenance-alias")
        shim = Path(self.temp.name) / "shim"
        shim.mkdir()
        interpreter = shim / "python3"
        interpreter.write_text("#!" + sys.executable + "\n" + "\n".join([
            "import subprocess, sys",
            "args = sys.argv[1:]",
            "result = subprocess.run([" + repr(sys.executable) + ", *args])",
            "if len(args) >= 2 and args[0].endswith('worktree_path_check.py') and args[1] == 'validate':",
            "    subprocess.run(['git', 'update-ref', 'refs/remotes/origin/main', " + repr(other) + "], check=True)",
            "raise SystemExit(result.returncode)",
        ]) + "\n")
        interpreter.chmod(0o755)
        with patch.dict(os.environ, {"PATH": str(shim) + os.pathsep + os.environ["PATH"]}):
            result = self.allocate("--path", "src/fix.py")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("changed before ticket reservation", result.stderr)
        self.assertFalse((self.root / ".git/new-project-ticket-high-water").exists())
        self.assertEqual(self.git("branch", "--list", "ticket/*").stdout, "")
        self.assertEqual(self.git("branch", "--show-current").stdout.strip(), "maintenance-alias")

    def test_overlapping_dirty_primary_refused_without_reservation(self) -> None:
        before = self.dirty_primary()
        result = self.allocate("--path", "src/other.py")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("pending-delta", result.stdout + result.stderr)
        self.assertFalse((self.root / ".git/new-project-ticket-high-water").exists())
        self.assertEqual(self.git("branch", "--list", "ticket/*").stdout, "")
        for name, content in before.items():
            self.assertEqual((self.root / name).read_bytes(), content, name)

    def test_unscoped_dirty_primary_refused_without_reservation(self) -> None:
        (self.root / ".planfile").mkdir()
        (self.root / ".planfile/current.yaml").write_text("operational: unchanged\n")
        result = self.allocate()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("explicit", result.stderr)
        self.assertFalse((self.root / ".git/new-project-ticket-high-water").exists())
        self.assertEqual(self.git("branch", "--list", "ticket/*").stdout, "")
        self.assertEqual((self.root / ".planfile/current.yaml").read_text(), "operational: unchanged\n")

    def test_linked_checkout_request_still_materializes_only_in_primary_layout(self) -> None:
        first = self.allocate()
        self.assertEqual(first.returncode, 0, first.stderr)
        linked = self.root / ".worktrees/ticket-001--canonical-ticket"
        second = subprocess.run(
            ["bash", "project/new-ticket.sh", "--title", "Second ticket", "--agent", "codex",
             "--writer-actor", "agent:codex", "--writer-session", "session-fixture",
             "--workstream", "application", "--worktree-slug", "second-ticket"],
            cwd=linked, text=True, capture_output=True,
            env={key: value for key, value in os.environ.items() if not key.startswith("GIT_")},
        )
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertTrue((self.root / ".worktrees/ticket-002--second-ticket/project/ticket-002").is_dir())
        self.assertFalse((linked / "project/ticket-002").exists())
        self.assertFalse((self.root / "project/ticket-002").exists())
        self.assertEqual((self.root / ".git/new-project-ticket-high-water").read_text().strip(), "2")


ALLOCATOR = ROOT / "project/new-ticket.sh"
SOURCE = ALLOCATOR.read_text()
LEASE_WRITER = SOURCE.split('from datetime import datetime, timedelta, timezone\n', 1)[1].split('\nPY\n', 1)[0]
LEASE_WRITER = 'from datetime import datetime, timedelta, timezone\n' + LEASE_WRITER


@unittest.skipUnless(hasattr(os, "O_NOFOLLOW") and hasattr(os, "O_DIRECTORY"),
                     "POSIX directory-descriptor fixture")
class LeaseRaceTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='allocator-lease-race-')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name) / 'repository'
        self.root.mkdir()
        self.intent = self.root / 'intent.json'
        self.intent.write_text(json.dumps({'allowedPaths': ['src/fix.py']}))
        self.lease = self.root / '.subactor/leases/ticket-001--fixture.json'
        self.outside = Path(temporary.name) / 'outside'
        self.outside.mkdir()
        self.arguments = ['allocator-lease-writer', str(self.intent), str(self.lease),
                          'ticket-001', 'application', 'ticket/001-fixture', 'fixture',
                          'fixture/repository', 'main', 'a' * 40, 'agent:fixture', 'session-fixture',
                          '2026-10-11T21:00:00Z']

    def execute(self):
        with patch.object(sys, 'argv', self.arguments):
            exec(compile(LEASE_WRITER, str(ALLOCATOR), 'exec'), {})

    def captured_execution(self):
        try:
            self.execute()
        except (OSError, SystemExit) as error:
            return error
        return None

    def test_normal_write_creates_private_valid_lease(self):
        self.execute()
        data = json.loads(self.lease.read_text())
        self.assertEqual(data['ticketId'], 'ticket-001')
        self.assertEqual(data['fencingToken'], 1)
        self.assertEqual(stat.S_IMODE(self.lease.stat().st_mode), 0o600)

    def test_existing_lease_is_never_overwritten(self):
        self.lease.parent.mkdir(parents=True)
        self.lease.write_bytes(b'original lease')
        self.assertIsNotNone(self.captured_execution())
        self.assertEqual(self.lease.read_bytes(), b'original lease')

    def test_existing_parent_symlink_creates_nothing_outside(self):
        (self.root / '.subactor').symlink_to(self.outside, target_is_directory=True)
        self.assertIsNotNone(self.captured_execution())
        self.assertEqual(list(self.outside.iterdir()), [])

    def test_parent_replacement_before_final_open_cannot_redirect_write(self):
        self.lease.parent.mkdir(parents=True)
        saved = self.lease.parent.with_name('leases-original')
        original_open = os.open
        attacked = []

        def racing_open(path, flags, *args, **kwargs):
            if flags & os.O_CREAT:
                self.lease.parent.rename(saved)
                self.lease.parent.symlink_to(self.outside, target_is_directory=True)
                attacked.append(True)
            return original_open(path, flags, *args, **kwargs)

        supported = (os.supports_dir_fd - {original_open}) | {racing_open}
        with patch.object(os, 'open', racing_open), patch.object(os, 'supports_dir_fd', supported):
            self.execute()
        self.assertEqual(attacked, [True])
        self.assertFalse((self.outside / self.lease.name).exists())
        self.assertTrue((saved / self.lease.name).is_file())

    def test_new_directory_replaced_before_traversal_is_rejected(self):
        (self.root / '.subactor').mkdir()
        saved = self.lease.parent.with_name('leases-original')
        original_mkdir = os.mkdir
        attacked = []

        def racing_mkdir(path, *args, **kwargs):
            result = original_mkdir(path, *args, **kwargs)
            if os.fspath(path) in {'leases', str(self.lease.parent)}:
                self.lease.parent.rename(saved)
                self.lease.parent.symlink_to(self.outside, target_is_directory=True)
                attacked.append(True)
            return result

        supported = (os.supports_dir_fd - {original_mkdir}) | {racing_mkdir}
        with patch.object(os, 'mkdir', racing_mkdir), patch.object(os, 'supports_dir_fd', supported):
            self.assertIsNotNone(self.captured_execution())
        self.assertEqual(attacked, [True])
        self.assertEqual(list(self.outside.iterdir()), [])

    def test_unsupported_host_fails_before_ticket_reservation(self):
        fixture = TicketAllocationWorktreeTest()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        shim = self.root / "shim"
        shim.mkdir()
        interpreter = shim / "python3"
        interpreter.write_text("#!" + sys.executable + "\n" + "\n".join([
            "import os, sys",
            "if sys.argv[1:] == ['-']:",
            "    code = sys.stdin.read()",
            "    if 'race-resistant lease creation is unsupported on this host' in code:",
            "        os.supports_dir_fd = set()",
            "    exec(compile(code, '<injected-host-capabilities>', 'exec'), {'__name__': '__main__'})",
            "else:",
            "    os.execv(sys.executable, [sys.executable, *sys.argv[1:]])",
        ]) + "\n")
        interpreter.chmod(0o755)
        before = fixture.git("status", "--porcelain").stdout
        with patch.dict(os.environ, {"PATH": str(shim) + os.pathsep + os.environ["PATH"]}):
            result = fixture.allocate()
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("race-resistant lease creation is unsupported", result.stderr)
        self.assertFalse((fixture.root / ".git/new-project-ticket-high-water").exists())
        self.assertEqual(fixture.git("branch", "--list", "ticket/*").stdout, "")
        self.assertFalse((fixture.root / ".subactor").exists())
        self.assertEqual(fixture.git("status", "--porcelain").stdout, before)

    def test_unsupported_directory_api_fails_before_lease_side_effects(self):
        with patch.object(os, 'supports_dir_fd', set()):
            self.assertIsNotNone(self.captured_execution())
        self.assertFalse((self.root / '.subactor').exists())



class NativeStandardAdoptionPlanTest(AdoptionPlanFixture, unittest.TestCase):
    def allocate_plan(self, *arguments):
        return self.command(self.target, "bash", str(self.source / "project/new-ticket.sh"),
            "--title", "Upgrade immutable standard", "--agent", "fixture",
            "--writer-actor", "agent:fixture", "--writer-session", "session-fixture",
            "--workstream", "governance", "--worktree-slug", "immutable-upgrade",
            "--standard-adoption-plan", str(self.plan_path), *arguments,
            env=self.publication_environment(), check=False)

    def test_published_plan_allocates_from_exact_primary_alias(self):
        self.command(self.target, "git", "checkout", "-b", "maintenance-alias")
        before = (self.target / ".git/index").read_bytes()
        self.test_exact_plan_allocates_complete_intent_before_reservation_hashes()
        self.assertEqual(self.command(self.target, "git", "branch", "--show-current").stdout.strip(),
                         "maintenance-alias")
        self.assertEqual((self.target / ".git/index").read_bytes(), before)

    def test_exact_plan_allocates_complete_intent_before_reservation_hashes(self):
        import hashlib

        from jsonschema import Draft202012Validator

        plan = self.export()
        before = self.command(self.target, "git", "status", "--porcelain").stdout
        result = self.allocate_plan()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        receipt = next(json.loads(line) for line in result.stdout.splitlines()
                       if line.startswith('{') and 'ticket-allocation-result' in line)
        self.assertFalse(receipt['executionAuthorized'])
        worktree = Path(receipt['worktreePath'])
        intent = json.loads((worktree / 'project/ticket-001/intent.json').read_text())
        self.assertEqual(intent['allowedPaths'][3:], plan['allowedPaths'])
        self.assertEqual(intent['delivery'], plan['delivery'])
        Draft202012Validator(json.loads((ROOT / 'governance/intent.schema.json').read_text())).validate(intent)
        lease = json.loads(Path(receipt['leasePath']).read_text())
        def canonical(value):
            return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()
        self.assertEqual(lease['planHash'], hashlib.sha256(canonical(intent)).hexdigest())
        self.assertEqual(lease['scopeHash'], hashlib.sha256(canonical(intent['allowedPaths'])).hexdigest())
        self.assertEqual(lease['phase'], 'claimed')
        self.assertEqual(self.command(self.target, 'git', 'status', '--porcelain').stdout, before)
        self.assertFalse((self.target / '.gitattributes').exists())
        self.assertFalse((worktree / '.gitattributes').exists())
        self.assertIn('.github/workflows/new-project-branch-hygiene.yml', intent['allowedPaths'])

    def historical_package_fixture(self, *, local_ownership=False):
        import contextlib
        import io

        # Actual historical adopter regression, distinct from synthetic gaps.
        revision = 'b6ba9c21a65a6a5648ecf904b64c3b75295e136f'
        self.target = self.case / 'historical-adopter'
        self.command(self.case, 'git', 'init', '--quiet', '-b', 'main', str(self.target))
        for key, value in (('user.name', 'Fixture'), ('user.email', 'fixture@example.invalid'),
                           ('core.excludesFile', os.devnull)):
            self.command(self.target, 'git', 'config', key, value)
        for name in ('README.md', 'VERSION', 'CHANGELOG.md', 'TODO.md', 'project/TICKETS.md'):
            path = self.target / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('0.1.0\n' if name == 'VERSION' else '# Fixture\n')
        with patch.object(self.adopter, 'verify_publication_evidence'), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(self.adopter.main(['--target-root', str(self.target),
                '--source-revision', revision, '--upgrade']), 0)
        if local_ownership:
            # The real old adopter retains its independently configured,
            # orthogonal ownership. The package pin does not own these fields.
            template = json.loads((self.template / '.governance/manifest.json').read_text())
            path = self.target / '.governance/manifest.json'
            manifest = json.loads(path.read_text())
            manifest['coordination']['workstreams'] = template['coordination']['workstreams']
            manifest['coordination']['integration'] = template['coordination']['integration']
            path.write_text(json.dumps(manifest, indent=2) + '\n')
        self.command(self.target, 'git', 'config', 'core.hooksPath', os.devnull)
        self.command(self.target, 'git', 'add', '.')
        self.command(self.target, 'git', 'commit', '--quiet', '-m', 'Real historical package fixture')
        self.plan_path = self.target / '.subactor/receipts/allocation-plan.json'
        self.plan_path.parent.mkdir(parents=True, exist_ok=True)

    def test_real_published_02032_package_with_local_owners_allocates_full_upgrade(self):
        self.historical_package_fixture(local_ownership=True)
        self.test_exact_plan_allocates_complete_intent_before_reservation_hashes()

    def test_historical_explicit_integration_requirements_are_not_bypassed(self):
        self.historical_package_fixture()
        with self.assertRaisesRegex(SystemExit, 'cannot transfer target-owned path'):
            self.export()
        self.assertFalse((self.target / '.git/new-project-ticket-high-water').exists())

    def test_caller_cannot_expand_or_narrow_derived_scope(self):
        self.export()
        result = self.allocate_plan('--path', 'src/foreign.py')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('exact derived adoption scope', result.stderr)
        self.assertFalse((self.target / '.git/new-project-ticket-high-water').exists())
        self.assertEqual(self.command(self.target, 'git', 'branch', '--list', 'ticket/*').stdout, '')

    def test_native_rejects_stale_target_before_identity_effect(self):
        self.export()
        (self.target / 'foreign.txt').write_text('another writer\n')
        result = self.allocate_plan()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('target state is stale', result.stderr)
        self.assertFalse((self.target / '.git/new-project-ticket-high-water').exists())
        self.assertFalse((self.target / '.worktrees').exists())

    def test_sqlite_route_does_not_fall_back_to_file_allocation(self):
        self.export()
        result = self.allocate_plan('--storage', 'sqlite')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('exclusive local file allocation', result.stderr)
        self.assertFalse((self.target / '.git/new-project-ticket-high-water').exists())


if __name__ == "__main__":
    unittest.main()
