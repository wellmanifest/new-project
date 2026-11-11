"""Actual CLI regressions for explicit migration of minimal Wellman scaffolds."""
import importlib.util
import contextlib
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/create_adoption_lock.py"
LEGACY = {
    "schema": "wellmanifest.manifest/v1",
    "standard": {"id": "profile:baseline", "version": "0.20.37"},
}


class LegacyScaffoldMigrationTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.target = self.root / "target"
        self.target.mkdir()
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=self.target, check=True)
        subprocess.run(["git", "remote", "add", "origin", "https://github.com/fixture/target.git"],
                       cwd=self.target, check=True)
        for name in ("README.md", "VERSION", "CHANGELOG.md", "TODO.md", "project/TICKETS.md"):
            path = self.target / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("target-owned prerequisite\n")
        self.manifest = self.target / ".governance/manifest.json"
        self.manifest.parent.mkdir()
        self.manifest.write_text(json.dumps(LEGACY, indent=4) + "\n")
        self.revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()

    def contents(self):
        return {str(p.relative_to(self.target)): p.read_bytes()
                for p in self.target.rglob("*") if p.is_file() and ".git" not in p.relative_to(self.target).parts}

    def run_adopter(self, *arguments):
        return subprocess.run([sys.executable, str(SCRIPT), "--target-root", str(self.target),
                               "--source-revision", self.revision, "--allow-unpublished-for-testing",
                               *arguments], capture_output=True, text=True, timeout=60)

    def committed_legacy_lock(self):
        names = ["AGENTS.md", "GEMINI.md", ".governance/manifest.json",
                 ".governance/standard-requirements.json", ".governance/standard-packs.json",
                 ".governance/docs.json", ".governance/local-ci-publication.json"]
        for relative in names:
            path = self.target / relative
            if not path.exists():
                path.write_text("{}\n" if path.suffix == ".json" else "# Legacy entry\n")
        document = {"schema": "new-project.lock/v1", "standard": {
            "id": "wellmanifest/new-project", "sourceRepository": "wellmanifest/new-project",
            "sourceRevision": "a" * 40, "version": "0.20.38", "publicationStatus": "published"},
            "managedFiles": {name: hashlib.sha256((self.target / name).read_bytes()).hexdigest() for name in names}}
        lock = self.target / ".governance/manifest.lock.json"
        lock.write_text(json.dumps(document))
        self.commit_target()
        return lock, document

    def commit_target(self):
        subprocess.run(["git", "add", "."], cwd=self.target, check=True)
        subprocess.run(["git", "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                        "commit", "-qm", "Fixture registration"], cwd=self.target, check=True)

    def test_committed_legacy_registration_migrates_and_preserves_target_contracts(self):
        self.committed_legacy_lock()
        before = self.contents()
        review = self.run_adopter("--check", "--migrate-wellman-scaffold")
        self.assertEqual(review.returncode, 1, review.stderr)
        self.assertIn("UPDATE .governance/manifest.json", review.stdout)
        self.assertEqual(before, self.contents())
        result = self.run_adopter("--upgrade", "--migrate-wellman-scaffold")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        for relative in [".governance/standard-requirements.json", ".governance/docs.json",
                         ".governance/local-ci-publication.json"]:
            self.assertEqual((self.target / relative).read_bytes(), before[relative])
        self.assertTrue((self.target / "project/new-ticket.sh").is_file())

    def test_legacy_registration_tampering_and_extensions_refuse_without_writes(self):
        lock, original = self.committed_legacy_lock()
        for change in ["dirty-file", "dirty-lock", "recomputed-digest", "extra-managed",
                       "missing-managed", "invalid-digest", "native-standard", "extra-standard",
                       "duplicate-key", "missing-file", "symlinked-file", "unpublished-registration"]:
            with self.subTest(change=change):
                subprocess.run(["git", "reset", "--hard", "-q", "HEAD"], cwd=self.target, check=True)
                doc = json.loads(json.dumps(original))
                path = self.target / "GEMINI.md"
                if change == "dirty-file":
                    path.write_text("changed\n")
                elif change == "dirty-lock":
                    doc["standard"]["version"] = "0.20.39"
                elif change == "recomputed-digest":
                    path.write_text("changed\n")
                    doc["managedFiles"]["GEMINI.md"] = hashlib.sha256(path.read_bytes()).hexdigest()
                elif change == "extra-managed":
                    doc["managedFiles"][".governance/native.py"] = "b" * 64
                elif change == "missing-managed":
                    del doc["managedFiles"]["GEMINI.md"]
                elif change == "invalid-digest":
                    doc["managedFiles"]["GEMINI.md"] = 12
                elif change == "native-standard":
                    doc["standard"]["id"] = "native-policy"
                elif change == "extra-standard":
                    doc["standard"]["writerAuthority"] = True
                elif change == "unpublished-registration":
                    doc["standard"]["publicationStatus"] = "unpublished-test"
                elif change == "missing-file":
                    path.unlink()
                elif change == "symlinked-file":
                    outside = self.root / "outside.md"
                    outside.write_bytes(path.read_bytes())
                    path.unlink()
                    path.symlink_to(outside)
                lock.write_text(json.dumps(doc))
                if change == "duplicate-key":
                    lock.write_text(lock.read_text().replace('"schema":', '"schema": "native", "schema":', 1))
                # Extended and malformed committed locks must also be refused.
                if change in {"extra-managed", "missing-managed", "invalid-digest", "native-standard", "extra-standard", "duplicate-key", "unpublished-registration"}:
                    self.commit_target()
                before = self.contents()
                result = self.run_adopter("--upgrade", "--migrate-wellman-scaffold")
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("refuses symlinked target paths" if change == "symlinked-file" else "refuses existing native adoption evidence", result.stderr)
                self.assertEqual(self.contents(), before)
                # Restore the known fixture revision without touching production Git.
                if change in {"extra-managed", "missing-managed", "invalid-digest", "native-standard", "extra-standard", "duplicate-key", "unpublished-registration"}:
                    subprocess.run(["git", "reset", "--hard", "-q", "HEAD~1"], cwd=self.target, check=True)

    def test_uncommitted_legacy_registration_is_not_a_migration_identity(self):
        lock, _ = self.committed_legacy_lock()
        subprocess.run(["git", "rm", "--cached", "-q", str(lock.relative_to(self.target))], cwd=self.target, check=True)
        self.commit_target_without_staging_lock()
        before = self.contents()
        result = self.run_adopter("--upgrade", "--migrate-wellman-scaffold")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(before, self.contents())

    def commit_target_without_staging_lock(self):
        subprocess.run(["git", "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                        "commit", "-qm", "Remove committed lock"], cwd=self.target, check=True)

    def test_registration_is_rechecked_immediately_before_installer_writes(self):
        self.committed_legacy_lock()
        spec = importlib.util.spec_from_file_location("legacy_recheck", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        validate = module.validate_wellman_scaffold
        calls = []

        def changed_before_write(*args):
            calls.append(args)
            if len(calls) == 2:
                raise SystemExit("registration changed before writes")
            return validate(*args)

        before = self.contents()
        args = [str(SCRIPT), "--target-root", str(self.target), "--source-revision", self.revision,
                "--upgrade", "--migrate-wellman-scaffold"]
        with patch.object(sys, "argv", args), patch.object(module, "verify_publication_evidence"), \
                patch.object(module, "validate_wellman_scaffold", side_effect=changed_before_write):
            with self.assertRaisesRegex(SystemExit, "registration changed before writes"):
                module.main()
        self.assertEqual(len(calls), 2)
        self.assertEqual(before, self.contents())

    def test_default_upgrade_still_refuses_incomplete_manifest(self):
        before = self.contents()
        result = self.run_adopter("--upgrade")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("does not extend", result.stderr)
        self.assertEqual(self.contents(), before)

    def test_explicit_review_then_apply_installs_pinned_native_adoption(self):
        before = self.contents()
        review = self.run_adopter("--check", "--migrate-wellman-scaffold")
        self.assertEqual(review.returncode, 1, review.stderr)
        self.assertIn("UPDATE .governance/manifest.json", review.stdout)
        self.assertEqual(self.contents(), before)
        result = self.run_adopter("--upgrade", "--migrate-wellman-scaffold")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        manifest = json.loads(self.manifest.read_text())
        lock = json.loads((self.manifest.parent / "manifest.lock.json").read_text())
        self.assertEqual(manifest["schema"], "new-project.governance/v2")
        self.assertIn("approvalEvidence", manifest)
        self.assertEqual(lock["standard"]["sourceRevision"], self.revision)
        self.assertEqual(lock["standard"]["publicationStatus"], "unpublished-test")
        self.assertTrue((self.target / "project/new-ticket.sh").is_file())
        for name in ("README.md", "VERSION", "CHANGELOG.md", "TODO.md", "project/TICKETS.md"):
            self.assertEqual((self.target / name).read_bytes(), before[name])

    def test_canonical_wellman_profile_scaffolds_migrate_cleanly(self):
        for profile in ("profile:runtime-service", "profile:domain-pack",
                        "profile:agent-executor", "profile:deployment",
                        "profile:embedded-fleet", "profile:full"):
            with self.subTest(profile=profile):
                subprocess.run(["git", "clean", "-fdq"], cwd=self.target, check=True)
                for name in ("README.md", "VERSION", "CHANGELOG.md", "TODO.md", "project/TICKETS.md"):
                    path = self.target / name
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text("target-owned prerequisite\n")
                self.manifest.parent.mkdir(parents=True, exist_ok=True)
                self.manifest.write_text(json.dumps({
                    "schema": "wellmanifest.manifest/v1",
                    "standard": {"id": profile, "version": "0.20.38"},
                }, indent=2) + "\n")
                before = self.contents()
                review = self.run_adopter("--check", "--migrate-wellman-scaffold")
                self.assertEqual(review.returncode, 1, review.stderr)
                self.assertIn("UPDATE .governance/manifest.json", review.stdout)
                self.assertEqual(self.contents(), before)
                result = self.run_adopter("--upgrade", "--migrate-wellman-scaffold")
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                manifest = json.loads(self.manifest.read_text())
                self.assertEqual(manifest["schema"], "new-project.governance/v2")
                (self.manifest.parent / "manifest.lock.json").unlink()
                (self.manifest.parent / "manifest.base.json").unlink()
                (self.manifest.parent / "package-manifest.json").unlink()

    def test_custom_and_native_manifests_cannot_use_migration(self):
        cases = [[], {**LEGACY, "coordination": {"policy": "keep"}},
                 {**LEGACY, "schema": "new-project.governance/v2"},
                 {**LEGACY, "standard": {"id": "wellmanifest/new-project", "version": "0.20.80"}},
                 {**LEGACY, "standard": {"id": "profile:unknown-custom", "version": "0.20.38"}},
                 {**LEGACY, "standard": {**LEGACY["standard"], "sourceRevision": "a" * 40}},
                 {**LEGACY, "standard": {**LEGACY["standard"], "version": 37}},
                 {**LEGACY, "standard": {**LEGACY["standard"], "version": ""}}]
        for document in cases:
            with self.subTest(document=document):
                self.manifest.write_text(json.dumps(document) + "\n")
                before = self.contents()
                result = self.run_adopter("--upgrade", "--migrate-wellman-scaffold")
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("minimal Wellman baseline", result.stderr)
                self.assertEqual(self.contents(), before)

    def test_native_adoption_evidence_prevents_migration(self):
        for name in ("manifest.lock.json", "manifest.base.json", "package-manifest.json"):
            with self.subTest(name=name):
                path = self.manifest.parent / name
                path.write_text("{}\n")
                before = self.contents()
                result = self.run_adopter("--upgrade", "--migrate-wellman-scaffold")
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("native adoption evidence", result.stderr)
                self.assertEqual(self.contents(), before)
                path.unlink()

    def test_missing_prerequisite_preserves_all_files(self):
        (self.target / "README.md").unlink()
        before = self.contents()
        result = self.run_adopter("--upgrade", "--migrate-wellman-scaffold")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("MISSING target prerequisite README.md", result.stdout)
        self.assertEqual(self.contents(), before)

    def test_migration_needs_explicit_review_or_upgrade(self):
        before = self.contents()
        result = self.run_adopter("--migrate-wellman-scaffold")
        self.assertEqual(result.returncode, 2)
        self.assertIn("--check or --upgrade", result.stderr)
        self.assertEqual(self.contents(), before)

    def test_fresh_bootstrap_refuses_existing_governance_without_writes(self):
        before = self.contents()
        result = self.run_adopter('--bootstrap-native-adoption', '--upgrade')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('requires absent governance', result.stderr)
        self.assertEqual(self.contents(), before)

    def test_fresh_bootstrap_refuses_deleted_committed_governance(self):
        subprocess.run(['git', 'add', '.'], cwd=self.target, check=True)
        subprocess.run(['git', '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid',
                        'commit', '-qm', 'Existing governance'], cwd=self.target, check=True)
        self.manifest.unlink()
        before = self.contents()
        result = self.run_adopter('--bootstrap-native-adoption', '--upgrade')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('cannot replace committed governance', result.stderr)
        self.assertEqual(self.contents(), before)

    def test_fresh_bootstrap_requires_committed_repository(self):
        self.manifest.unlink()
        before = self.contents()
        result = self.run_adopter('--bootstrap-native-adoption')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('requires a committed Git repository', result.stderr)
        self.assertEqual(self.contents(), before)

    def test_fresh_bootstrap_rejects_both_modes_before_writes(self):
        before = self.contents()
        result = self.run_adopter('--bootstrap-native-adoption', '--migrate-wellman-scaffold', '--check')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('mutually exclusive', result.stderr)
        self.assertEqual(self.contents(), before)

    def test_migration_keeps_publication_verification(self):
        spec = importlib.util.spec_from_file_location("legacy_adoption", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        before = self.contents()
        args = [str(SCRIPT), "--target-root", str(self.target), "--source-revision", self.revision,
                "--upgrade", "--migrate-wellman-scaffold"]
        with patch.object(sys, "argv", args), patch.object(
            module, "verify_publication_evidence", side_effect=SystemExit("publication-fixture-refusal")
        ) as verifier:
            with self.assertRaisesRegex(SystemExit, "publication-fixture-refusal"):
                module.main()
            verifier.assert_called_once()
        self.assertEqual(self.contents(), before)

    def test_duplicate_keys_cannot_hide_native_policy(self):
        self.manifest.write_text('{"schema":"new-project.governance/v2","schema":"wellmanifest.manifest/v1",'
                                 '"standard":{"id":"profile:baseline","version":"0.20.37"}}')
        before = self.contents()
        result = self.run_adopter("--upgrade", "--migrate-wellman-scaffold")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("minimal Wellman baseline", result.stderr)
        self.assertEqual(self.contents(), before)

    @unittest.skipIf(sys.platform == "win32", "symlink creation needs host privileges on Windows")
    def test_symlinked_targets_are_preserved(self):
        outside = self.root / "outside"
        outside.mkdir()
        sentinel = outside / "sentinel.txt"
        sentinel.write_text("outside target\n")
        (self.target / ".github").symlink_to(outside, target_is_directory=True)
        before = self.contents()
        result = self.run_adopter("--upgrade", "--migrate-wellman-scaffold")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("symlinked target", result.stderr)
        self.assertEqual(self.contents(), before)
        self.assertEqual(list(outside.iterdir()), [sentinel])


class BootstrapPrerequisitePlanTest(unittest.TestCase):
    contents = LegacyScaffoldMigrationTest.contents
    run_adopter = LegacyScaffoldMigrationTest.run_adopter
    commit_target = LegacyScaffoldMigrationTest.commit_target

    def setUp(self):
        LegacyScaffoldMigrationTest.setUp(self)
        self.seeds = {"VERSION": "0.1.0\n", "CHANGELOG.md": "# Changelog\n",
                      "TODO.md": "# TODO\n", "project/TICKETS.md": "# Tickets\n"}
        for name in self.seeds:
            (self.target / name).unlink()
        (self.target / "foreign.txt").write_text("original\n")
        self.commit_target()
        self.plan_path = self.root / "prerequisites.json"
        self.save_plan()

    def save_plan(self, change=None):
        plan = {"schema": "new-project.bootstrap-prerequisites-plan/v1",
                "baseSha": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=self.target, text=True).strip(),
                "files": [{"path": name, "content": content,
                           "sha256": hashlib.sha256(content.encode()).hexdigest()}
                          for name, content in self.seeds.items()]}
        if change:
            change(plan)
        self.plan_path.write_text(json.dumps(plan))

    def apply_plan(self, mode="--upgrade", kind="--migrate-wellman-scaffold"):
        return self.run_adopter(mode, kind, "--bootstrap-prerequisites-plan", str(self.plan_path))

    def test_review_is_read_only_and_install_receipt_binds_seed_bytes(self):
        before = self.contents()
        result = self.apply_plan("--check")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("CREATE VERSION", result.stdout)
        self.assertEqual(before, self.contents())
        result = self.apply_plan()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        receipt = json.loads((self.target / ".subactor/receipts/bootstrap-adoption.json").read_text())
        for name, content in self.seeds.items():
            self.assertEqual((self.target / name).read_text(), content)
            self.assertEqual(receipt["files"][name], hashlib.sha256(content.encode()).hexdigest())
        self.assertIs(receipt["grantsWriterAuthority"], False)
        self.assertIs(receipt["grantsPublicationAuthority"], False)

    def test_default_behavior_still_refuses_missing_prerequisites(self):
        before = self.contents()
        result = self.run_adopter("--upgrade", "--migrate-wellman-scaffold")
        self.assertEqual(result.returncode, 1)
        self.assertIn("MISSING target prerequisite VERSION", result.stdout)
        self.assertEqual(before, self.contents())

    def test_invalid_plans_make_no_target_writes(self):
        mutations = [lambda p: p.update(baseSha="a" * 40),
                     lambda p: p.update(extra="untrusted"),
                     lambda p: p["files"][0].update(path="../VERSION"),
                     lambda p: p["files"][0].update(path="src/worker.py"),
                     lambda p: p["files"][0].update(sha256="0" * 64),
                     lambda p: p["files"].append(p["files"][0]),
                     lambda p: p["files"][0].update(content="x" * 65537)]
        for index, mutation in enumerate(mutations):
            with self.subTest(index=index):
                self.save_plan(mutation)
                before = self.contents()
                result = self.apply_plan()
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(before, self.contents())

    def test_existing_and_deleted_committed_files_are_preserved(self):
        version = self.target / "VERSION"
        version.write_text("owner bytes\n")
        before = self.contents()
        self.assertNotEqual(self.apply_plan().returncode, 0)
        self.assertEqual(before, self.contents())
        self.commit_target()
        version.unlink()
        self.save_plan()
        before = self.contents()
        self.assertNotEqual(self.apply_plan().returncode, 0)
        self.assertEqual(before, self.contents())

    @unittest.skipIf(sys.platform == "win32", "symlink creation needs host privileges")
    def test_symlinked_seed_parent_is_preserved(self):
        (self.target / "project").rmdir()
        outside = self.root / "outside"
        outside.mkdir()
        (outside / "sentinel").write_text("keep\n")
        (self.target / "project").symlink_to(outside, target_is_directory=True)
        before = self.contents()
        self.assertNotEqual(self.apply_plan().returncode, 0)
        self.assertEqual(before, self.contents())
        self.assertFalse((outside / "TICKETS.md").exists())

    def test_plan_is_not_available_to_ordinary_upgrade(self):
        before = self.contents()
        result = self.run_adopter("--upgrade", "--bootstrap-prerequisites-plan", str(self.plan_path))
        self.assertEqual(result.returncode, 2)
        self.assertEqual(before, self.contents())

    def test_duplicate_json_keys_are_rejected(self):
        text = self.plan_path.read_text()
        self.plan_path.write_text(text.replace('"schema":', '"schema":"other", "schema":', 1))
        before = self.contents()
        self.assertNotEqual(self.apply_plan().returncode, 0)
        self.assertEqual(before, self.contents())

    def test_fresh_bootstrap_accepts_the_same_explicit_plan(self):
        self.manifest.unlink()
        self.commit_target()
        self.save_plan()
        result = self.apply_plan(kind="--bootstrap-native-adoption")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_real_first_allocator_keeps_seed_and_foreign_bytes_in_primary(self):
        spec = importlib.util.spec_from_file_location("prerequisite_adopter", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        arguments = ["--target-root", str(self.target), "--source-revision", self.revision,
                     "--migrate-wellman-scaffold", "--upgrade",
                     "--bootstrap-prerequisites-plan", str(self.plan_path)]
        # Publication alone is mocked in this fixture; the real allocator is not.
        with patch.object(module, "verify_publication_evidence"):
            self.assertEqual(module.main(arguments), 0)
        foreign = self.target / "foreign.txt"
        foreign.write_text("another owner\n")
        checksum = subprocess.check_output([sys.executable, "-B", "-c",
            "import sys;from pathlib import Path;sys.path.insert(0,'.governance');"
            "import work_start_check;print(work_start_check.dirty_observation(Path('.'))[1])"],
            cwd=self.target, text=True).strip()
        result = subprocess.run(["bash", "project/new-ticket.sh", "--title", "Seeded adoption",
            "--agent", "fixture", "--workstream", "governance", "--path", ".governance/**",
            "--worktree-slug", "seeded", "--bootstrap-adoption-digest", checksum],
            cwd=self.target, capture_output=True, text=True, timeout=60)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(foreign.read_text(), "another owner\n")
        checkout = self.target / ".worktrees/ticket-001--seeded"
        self.assertTrue((checkout / "project/ticket-001/intent.json").is_file())
        self.assertFalse((checkout / "VERSION").exists())

    def loaded_adopter(self):
        spec = importlib.util.spec_from_file_location("race_checked_adopter", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_all_seed_destinations_are_checked_before_any_creation(self):
        module = self.loaded_adopter()
        (self.target / "project").rmdir()
        (self.target / "VERSION").write_bytes(b"foreign version\n")
        before = self.contents()
        with self.assertRaises(SystemExit):
            module.create_bootstrap_prerequisites(self.target,
                {name: content.encode() for name, content in self.seeds.items()})
        self.assertEqual(before, self.contents())
        self.assertFalse((self.target / "project").exists())

    def test_late_conflict_reports_partial_seeds_without_managed_writes(self):
        module = self.loaded_adopter()
        before = self.contents()
        real_fdopen = module.os.fdopen
        changed = False

        @contextlib.contextmanager
        def concurrent_version(descriptor, mode, *args, **kwargs):
            nonlocal changed
            with real_fdopen(descriptor, mode, *args, **kwargs) as stream:
                yield stream
            if mode == "wb" and not changed:
                changed = True
                (self.target / "VERSION").write_bytes(b"concurrent owner\n")

        arguments = ["--target-root", str(self.target), "--source-revision", self.revision,
                     "--migrate-wellman-scaffold", "--upgrade",
                     "--bootstrap-prerequisites-plan", str(self.plan_path)]
        with patch.object(module, "verify_publication_evidence"), \
                patch.object(module.os, "fdopen", concurrent_version):
            with self.assertRaises(SystemExit) as failure:
                module.main(arguments)
        self.assertTrue(changed, "fixture must introduce the conflict during actual creation")
        self.assertIn("partial bootstrap prerequisites preserved", str(failure.exception))
        self.assertIn("CHANGELOG.md", str(failure.exception))
        self.assertIn("TODO.md", str(failure.exception))
        self.assertIn("reconcile", str(failure.exception))
        expected = dict(before)
        expected.update({"CHANGELOG.md": self.seeds["CHANGELOG.md"].encode(),
                         "TODO.md": self.seeds["TODO.md"].encode(),
                         "VERSION": b"concurrent owner\n"})
        self.assertEqual(expected, self.contents())
        self.assertFalse((self.target / ".subactor/receipts/bootstrap-adoption.json").exists())

    def test_plan_read_is_bounded_after_stale_size_observation(self):
        module = self.loaded_adopter()
        self.plan_path.write_bytes(self.plan_path.read_bytes() + b" " * module.MAX_RELEASE_METADATA_BYTES)
        real_stat = Path.stat

        def stale_size(path, *args, **kwargs):
            value = real_stat(path, *args, **kwargs)
            if path == self.plan_path:
                fields = list(value)
                fields[6] = 1  # File grew after the caller observed its metadata.
                return os.stat_result(fields)
            return value

        before = self.contents()
        with patch.object(Path, "stat", stale_size), self.assertRaises(SystemExit):
            module.bootstrap_prerequisite_payloads(self.target,
                {"requiredFiles": list(self.seeds)}, {}, self.plan_path)
        self.assertEqual(before, self.contents())

    @unittest.skipUnless(hasattr(os, "O_NOFOLLOW") and os.open in os.supports_dir_fd,
                         "directory descriptor race fixture requires POSIX primitives")
    def test_replaced_parent_never_receives_seed_or_managed_files(self):
        module = self.loaded_adopter()
        outside = self.root / "outside"
        outside.mkdir()
        original = self.target / "project-before-race"
        switched = False
        real_path_open, real_os_open = Path.open, os.open

        def replace_parent():
            nonlocal switched
            if not switched:
                (self.target / "project").rename(original)
                (self.target / "project").symlink_to(outside, target_is_directory=True)
                switched = True

        def raced_path_open(path, *args, **kwargs):
            mode = args[0] if args else kwargs.get("mode", "r")
            if path == self.target / "project/TICKETS.md" and mode == "xb":
                replace_parent()
            return real_path_open(path, *args, **kwargs)

        def raced_os_open(path, flags, *args, **kwargs):
            if path == "TICKETS.md" and flags & os.O_CREAT:
                replace_parent()
            return real_os_open(path, flags, *args, **kwargs)

        arguments = ["--target-root", str(self.target), "--source-revision", self.revision,
                     "--migrate-wellman-scaffold", "--upgrade",
                     "--bootstrap-prerequisites-plan", str(self.plan_path)]
        with patch.object(module, "verify_publication_evidence"), \
                patch.object(Path, "open", raced_path_open), \
                patch.object(module.os, "open", raced_os_open), \
                patch.object(module.os, "supports_dir_fd", os.supports_dir_fd | {raced_os_open}):
            with contextlib.suppress(SystemExit, OSError):
                module.main(arguments)
        self.assertTrue(switched, "fixture must replace the parent at actual leaf creation")
        self.assertEqual(list(outside.iterdir()), [], "a replaced parent must never redirect writes")

    def test_unsupported_descriptor_host_refuses_before_effects(self):
        module = self.loaded_adopter()
        before = self.contents()
        with patch.object(module.os, "supports_dir_fd", set()), self.assertRaises(SystemExit):
            module.bootstrap_prerequisite_payloads(self.target,
                {"requiredFiles": list(self.seeds)}, {}, self.plan_path)
        self.assertEqual(before, self.contents())


if __name__ == "__main__":
    unittest.main()
