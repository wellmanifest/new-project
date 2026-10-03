#!/usr/bin/env python3
"""Actual allocator effects and managed host/runtime boundary regressions."""
from contextlib import contextmanager
import importlib.util
import json
import os
import re
from pathlib import Path
import shutil
import shlex
import signal
import subprocess
import sys
import tempfile
import time
import unittest

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "allocation_fixture", ROOT / "tests/ticket-allocation-worktree.test.py")
allocation_fixture_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(allocation_fixture_module)


def fixture_bash():
    if os.name == "nt":
        git = shutil.which("git")
        if git:
            for directory in Path(git).resolve().parents:
                for relative in ("bin/bash.exe", "usr/bin/bash.exe"):
                    candidate = directory / relative
                    if candidate.is_file():
                        return str(candidate)
        raise RuntimeError("Git for Windows Bash is required for allocator fixtures")
    bash = shutil.which("bash")
    if not bash:
        raise RuntimeError("Bash is required for allocator fixtures")
    return bash


@contextmanager
def allocation_fixture():
    fixture = allocation_fixture_module.TicketAllocationWorktreeTest(
        "test_file_ticket_is_created_only_in_canonical_linked_worktree")
    original_git = fixture.git
    def portable_git(*args, check=True):
        if args == ("config", "core.excludesFile", os.devnull):
            # Git for Windows rejects NUL as an exclude file. A real empty
            # file also isolates the fixture from user-level ignore rules.
            excludes = Path(fixture.temp.name) / "empty-git-excludes"
            excludes.write_bytes(b"")
            original_git("config", "core.autocrlf", "false")
            args = ("config", "core.excludesFile", str(excludes))
        return original_git(*args, check=check)
    fixture.git = portable_git
    try:
        fixture.setUp()
    except subprocess.CalledProcessError as error:
        # This repository contains only controlled public test fixtures.
        # Surface Git's diagnostic without exposing production ticket data.
        fixture.doCleanups()
        raise AssertionError(error.stderr) from error
    tools = Path(fixture.temp.name) / "tools"
    tools.mkdir()
    python = shlex.quote(sys.executable.replace("\\", "/"))
    (tools / "python3").write_bytes(("#!/bin/sh\nexec " + python + ' "$@"\n').encode("utf-8"))
    (tools / "python3").chmod(0o755)
    bash = fixture_bash()
    def portable_allocate(*args):
        env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
        env["PATH"] = str(tools) + os.pathsep + str(Path(bash).parent) + os.pathsep + env["PATH"]
        env["PYTHONUTF8"] = "1"
        return subprocess.run([bash, "project/new-ticket.sh", "--title", "Canonical ticket", "--agent", "codex",
            "--workstream", "application", "--worktree-slug", "canonical-ticket", *args],
            cwd=fixture.root, env=env, text=True, encoding="utf-8", capture_output=True)
    fixture.allocate = portable_allocate
    try:
        yield fixture
    finally:
        fixture.doCleanups()


def pointer_program():
    source = (ROOT / "scripts/install-agent-hosts.sh").read_text(encoding="utf-8")
    return source.split('python3 - "$pointer" "$marker" <<\'PY\' || return 1\n', 1)[1].split("\nPY\n", 1)[0]


def update_pointer(path):
    return subprocess.run([sys.executable, "-", str(path),
        "wellmanifest/new-project host contract"], input=pointer_program(),
        text=True, capture_output=True)


class RuntimeSafetyTests(unittest.TestCase):
    def interrupted_allocator(self, interrupt, expected):
        with allocation_fixture() as fixture:
            control = Path(fixture.temp.name)
            wrapper = control / "bin"
            wrapper.mkdir()
            real_git = shutil.which("git")
            self.assertIsNotNone(real_git)
            script = wrapper / "git"
            script.write_text('''#!/bin/bash
if [[ -d "$TASK_SIGNAL_ROOT/.git/new-project-ticket-allocation.lock" ]] && mkdir "$TASK_SIGNAL_CONTROL/claimed" 2>/dev/null; then
  touch "$TASK_SIGNAL_CONTROL/ready"
  while [[ ! -e "$TASK_SIGNAL_CONTROL/release" ]]; do sleep 0.05; done
fi
exec "$TASK_SIGNAL_REAL_GIT" "$@"
''', encoding="utf-8")
            script.chmod(0o755)
            env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
            env.update({"PATH": str(wrapper) + os.pathsep + env["PATH"],
                "TASK_SIGNAL_ROOT": str(fixture.root),
                "TASK_SIGNAL_CONTROL": str(control), "TASK_SIGNAL_REAL_GIT": real_git})
            process = subprocess.Popen(["bash", "project/new-ticket.sh", "--title", "Signal fixture",
                "--agent", "codex", "--workstream", "application", "--worktree-slug", "signal-fixture"],
                cwd=fixture.root, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            try:
                deadline = time.monotonic() + 10
                while not (control / "ready").exists() and time.monotonic() < deadline:
                    self.assertIsNone(process.poll())
                    time.sleep(0.05)
                self.assertTrue((control / "ready").exists(), "allocator did not acquire its clone lock")
                process.send_signal(interrupt)
                time.sleep(0.1)
                (control / "release").touch()
                out, err = process.communicate(timeout=30)
                self.assertEqual(process.returncode, expected, out + err)
                self.assertFalse((fixture.root / ".git/new-project-ticket-high-water").exists())
                self.assertFalse((fixture.root / ".worktrees/ticket-001--signal-fixture").exists())
                self.assertFalse((fixture.root / ".git/new-project-ticket-allocation.lock").exists())
            finally:
                (control / "release").touch()
                if process.poll() is None:
                    process.terminate()
                    process.communicate(timeout=10)

    @unittest.skipUnless(os.name == "posix", "POSIX shell signal semantics")
    def test_allocator_terminates_after_sigterm(self):
        self.interrupted_allocator(signal.SIGTERM, 143)

    @unittest.skipUnless(os.name == "posix", "POSIX shell signal semantics")
    def test_allocator_terminates_after_sigint(self):
        self.interrupted_allocator(signal.SIGINT, 130)

    def test_control_titles_rejected_before_any_reservation(self):
        for code in (1, 9, 127):
            with self.subTest(code=code), allocation_fixture() as fixture:
                result = fixture.allocate("--title", "Control " + chr(code) + " title")
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertFalse((fixture.root / ".git/new-project-ticket-high-water").exists())
                self.assertEqual(fixture.git("branch", "--list", "ticket/*").stdout, "")
                self.assertFalse((fixture.root / ".worktrees/ticket-001--canonical-ticket").exists())

    def test_unicode_quotes_and_backslash_title_round_trip(self):
        with allocation_fixture() as fixture:
            title = 'Żółć Ελληνικά Україна "quoted" \\path'
            result = fixture.allocate("--title", title)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            root = fixture.root / ".worktrees/ticket-001--canonical-ticket/project/ticket-001"
            intent = json.loads((root / "intent.json").read_text(encoding="utf-8"))
            self.assertEqual(intent["summary"], title)
            self.assertIn(title, (root / "README.md").read_text(encoding="utf-8"))

    def invalid_pointer(self, text):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "GEMINI.md"
            original = text.encode("utf-8")
            path.write_bytes(original)
            result = update_pointer(path)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(path.read_bytes(), original)

    def test_malformed_managed_pointer_fails_without_rewriting_user_bytes(self):
        self.invalid_pointer("# User notes\nPreserve żółć.\n\n"
            "# wellmanifest/new-project host contract\n\nMalformed incomplete body.\n")

    def test_duplicate_managed_heading_fails_without_rewriting_user_bytes(self):
        self.invalid_pointer("# wellmanifest/new-project host contract\n\nWhen the current old contract.\n\n"
            "# User notes\nPreserve these.\n\n# wellmanifest/new-project host contract\n\n"
            "When the current second contract.\n")

    def test_valid_pointer_preserves_notes_and_updates_idempotently(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "CLAUDE.md"
            path.write_text("# User notes\nPreserve żółć.\n\n"
                "# wellmanifest/new-project host contract\n\nWhen the current old contract.\n\n"
                "# Extra notes\nPreserve extra notes.\n", encoding="utf-8")
            first = update_pointer(path)
            self.assertEqual(first.returncode, 0, first.stderr)
            content = path.read_bytes()
            text = path.read_text(encoding="utf-8")
            self.assertIn("# User notes\nPreserve żółć.", text)
            self.assertIn("# Extra notes\nPreserve extra notes.", text)
            self.assertIn(b"git worktree list", content)
            second = update_pointer(path)
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertEqual(path.read_bytes(), content)

    @unittest.skipUnless(shutil.which("node"), "Node required for actual runtime matching")
    def test_recursive_glob_matches_root_and_nested_without_broadening_simple_star(self):
        source = (ROOT / "scripts/runtime.sh").read_text(encoding="utf-8")
        start = source.index("function globToRegExp(")
        end = source.index("\nfunction pathAllowed(", start)
        cases = [("**/*.py", "root.py", True), ("**/*.py", "src/deep/root.py", True),
            ("src/**/*.py", "src/root.py", True), ("src/**/*.py", "src/deep/root.py", True),
            ("src/**/*.py", "other/root.py", False), ("*.py", "src/root.py", False),
            ("a[1].py", "a[1].py", True), ("a[1].py", "a1.py", False),
            ("dir/?/ф.py", "dir/é/ф.py", True)]
        program = source[start:end] + "\nconst cases = JSON.parse(process.argv[1]);\n" + \
            "console.log(JSON.stringify(cases.map(([pattern,path])=>globToRegExp(pattern).test(path))));"
        result = subprocess.run(["node", "--input-type=module", "--eval", program,
            json.dumps(cases)], text=True, capture_output=True, check=True)
        self.assertEqual(json.loads(result.stdout), [c[2] for c in cases])

    def test_scope_globs_follow_canonical_segment_semantics(self):
        def load(name, path):
            spec = importlib.util.spec_from_file_location(name, path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[name] = module
            spec.loader.exec_module(module)
            return module
        canonical = load("scope_canonical_fixture", ROOT / "scripts/governance_check.py")
        cases = [("src/*", "src/file.py", True), ("src/*", "src/private/file.py", False),
            ("*.py", "src/file.py", False), ("**/*.py", "file.py", True),
            ("src/**/*.py", "src/file.py", True), ("src/**/*.py", "src/private/file.py", True),
            ("src/?.py", "src/x.py", True), ("src/?.py", "src/a/b.py", False),
            ("src/[ab].py", "src/a.py", True), ("src/[ab].py", "src/c.py", False),
            ("src/żółw/*.py", "src/żółw/ф.py", True), ("src/żółw/*.py", "src/żółw/deep/ф.py", False),
            ("src/**", "src", True), ("src/**/file.py", "other/file.py", False)]
        for source in ("scripts/repository_policy.py", "scripts/remediation_intent.py", "packages/wellman/src/wellman/_bundled/repository_policy.py"):
            module = load("scope_" + source.replace("/", "_")[:-3], ROOT / source)
            for pattern, path, expected in cases:
                with self.subTest(module=source, pattern=pattern, path=path):
                    self.assertEqual(canonical.matches(path, [pattern]), expected)
                    self.assertEqual(module._matches(path, [pattern]), expected)

    def test_remediation_action_paths_retain_directory_boundaries(self):
        spec = importlib.util.spec_from_file_location("scope_remediation_actions", ROOT / "scripts/remediation_intent.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        for allowed, forbidden, expected in (
            (["src/*"], [], True), (["src/**"], [], False),
            (["src/**"], ["src/private/*"], False), (["src/**"], ["src/private/**"], True),
        ):
            errors = []
            module._validate_action_paths(["src/private/deep/file.py"], allowed, forbidden, "actions[0]", errors)
            with self.subTest(allowed=allowed, forbidden=forbidden):
                self.assertEqual(bool(errors), expected)



    def test_intent_branch_names_match_git_in_source_bundle_and_schema(self):
        checkers = []
        for index, relative in enumerate(("scripts/governance_check.py",
                "packages/wellman/src/wellman/_bundled/governance_check.py")):
            name = f"branch_boundary_runtime_{index}"
            spec = importlib.util.spec_from_file_location(name, ROOT / relative)
            checker = importlib.util.module_from_spec(spec)
            sys.modules[name] = checker
            spec.loader.exec_module(checker)
            checkers.append(checker.branch_name)
        schema = json.loads((ROOT / "governance/intent.schema.json").read_text())["$defs"]["branch"]
        self.assertEqual(schema["type"], "string")
        self.assertEqual(schema["minLength"], 1)
        pattern = re.compile(schema["pattern"])
        invalid = ("", "/", "HEAD", "-topic", ".topic", "topic/.hidden", "topic.lock",
                   "topic.lock/child", "topic/child.lock", "topic.", "topic/",
                   "topic//child", "topic..child", "topic@{child", "topic space",
                   "topic\tspace", "topic\nspace", "topic\x7fspace", "topic\x01space",
                   "topic~child", "topic^child", "topic:child", "topic?child",
                   "topic*child", "topic[child", "topic\\child")
        valid = ("main", "ticket/300-branch", "topic.Lock", "foo./bar",
                 "topic@name", "żółw/日本語", "comma,semi;plus+", "tag#one", "refs/heads/main", "unicode\u2028name", "emoji/😀")
        cases = [(value, False) for value in invalid] + [(value, True) for value in valid]
        javascript = subprocess.run(["node", "-e",
            "const x=JSON.parse(require('fs').readFileSync(0,'utf8'));"
            "process.stdout.write(JSON.stringify(x.names.map(v=>new RegExp(x.pattern).test(v))))"],
            input=json.dumps({"pattern": schema["pattern"], "names": [value for value, _ in cases] + ["@"]}),
            text=True, capture_output=True, check=True)
        self.assertEqual(json.loads(javascript.stdout), [expected for _, expected in cases] + [False])
        for value, expected in cases:
            with self.subTest(value=value):
                actual = subprocess.run(["git", "check-ref-format", "--branch", value],
                                        capture_output=True, check=False)
                self.assertEqual(actual.returncode == 0, expected)
                for checker in checkers:
                    self.assertEqual(checker(value), expected)
                self.assertEqual(pattern.fullmatch(value) is not None, expected)
        # Git permits the literal branch refs/heads/@, but standalone @ is
        # excluded by this contract because it is also the HEAD shorthand.
        self.assertEqual(subprocess.run(["git", "check-ref-format", "--branch", "@"],
                                        capture_output=True).returncode, 0)
        self.assertTrue(all(checker("@") is False for checker in checkers))
        self.assertIsNone(pattern.fullmatch("@"))
        for value in (None, 17, [], {}, True):
            with self.subTest(value=value):
                self.assertTrue(all(checker(value) is False for checker in checkers))



    def test_reserved_at_shorthand_can_resolve_differently_from_literal_branch(self):
        with tempfile.TemporaryDirectory(prefix="branch-at-ambiguity-") as temporary:
            root = Path(temporary)
            hooks = root / "empty-hooks"
            hooks.mkdir()
            env = dict(os.environ)
            env.update(GIT_CONFIG_NOSYSTEM="1", GIT_AUTHOR_NAME="Controlled fixture",
                       GIT_AUTHOR_EMAIL="fixture@example.invalid", GIT_COMMITTER_NAME="Controlled fixture",
                       GIT_COMMITTER_EMAIL="fixture@example.invalid")
            def git(*args):
                return subprocess.check_output(["git", "-C", str(root), "-c", "commit.gpgsign=false",
                    "-c", "core.hooksPath=" + str(hooks), *args], env=env, stderr=subprocess.PIPE).strip()
            git("init", "--quiet", "--initial-branch=main")
            git("commit", "--quiet", "--allow-empty", "-m", "First fixture")
            first = git("rev-parse", "HEAD")
            git("branch", "@", first.decode("ascii"))
            git("commit", "--quiet", "--allow-empty", "-m", "Second fixture")
            second = git("rev-parse", "HEAD")
            self.assertNotEqual(first, second)
            self.assertEqual(git("rev-parse", "--verify", "refs/heads/@"), first)
            self.assertEqual(git("rev-parse", "--verify", "@"), second)


    def test_physical_claim_identity_is_consistent_in_source_and_bundle(self):
        from copy import deepcopy
        pin = {"contract": "switch", "property": "pin-assignment", "signal": "forward",
               "before": "SDA", "after": "TX", "acceptance": ["Actuate switch on rig"]}
        keep = {"contract": "switch", "property": "none", "rationale": "Format only"}
        invalid = (
            [pin, dict(pin)], [pin, dict(pin, after="RX")],
            [pin, dict(pin, before="SCL")], [pin, dict(pin, acceptance=["Different check"])],
            [pin, keep], [keep, pin], [keep, dict(keep, rationale="Other explanation")],
        )
        valid = (
            [pin], [keep], [pin, dict(pin, property="active-level")],
            [pin, dict(pin, signal="reverse")], [pin, dict(pin, contract="other switch")],
            [pin, dict(keep, contract="other switch")],
            [pin, dict(pin, signal="forward ")], [pin, dict(pin, contract="switch ")],
        )
        for index, relative in enumerate(("scripts/governance_check.py",
                "packages/wellman/src/wellman/_bundled/governance_check.py")):
            name = f"physical_claim_runtime_{index}"
            spec = importlib.util.spec_from_file_location(name, ROOT / relative)
            checker = importlib.util.module_from_spec(spec)
            sys.modules[name] = checker
            spec.loader.exec_module(checker)
            for expected_valid, cases in ((False, invalid), (True, valid)):
                for changes in cases:
                    original = deepcopy(changes)
                    with self.subTest(runtime=relative, changes=changes):
                        self.assertEqual(checker.physical_changes_error(changes) is None, expected_valid)
                        self.assertEqual(changes, original)


    def test_catalog_execution_models_are_typed_before_strict_conformance(self):
        from copy import deepcopy
        spec = importlib.util.spec_from_file_location("catalog_model_boundary", ROOT / "scripts/standard_pack_check.py")
        checker = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(checker)
        baseline = {"schema": "wellmanifest.standard-pack-routing/v1", "packs": [],
                    "profiles": {"empty": {"requirements": []}},
                    "executionModels": {"reference-only": {"maximumLevel": "S0", "authorizesEffects": False}}}
        invalid = [
            ("", {"maximumLevel": "S0", "authorizesEffects": False}),
            (" ", {"maximumLevel": "S0", "authorizesEffects": False}),
            *(('reference-only', value) for value in (None, 17, True, [], "model", {})),
            *(('reference-only', {"maximumLevel": value, "authorizesEffects": False})
              for value in (None, 0, True, [], {}, "INVALID")),
            *(('reference-only', {"maximumLevel": "S0", "authorizesEffects": value})
              for value in (None, 0, 1, "yes", [], {})),
            ('reference-only', {"maximumLevel": "S0"}),
            ('reference-only', {"authorizesEffects": False}),
        ]
        valid = [("model ścieżka", {"maximumLevel": level, "authorizesEffects": effects,
                                  "description": "Preserved metadata"})
                 for level in checker.LEVELS for effects in (False, True)]
        valid.append((" model ", {"maximumLevel": "S2", "authorizesEffects": False}))
        with tempfile.TemporaryDirectory(prefix="catalog-model-boundary-") as temporary:
            root = Path(temporary)
            (root / "adoption.json").write_text(json.dumps({"schema": "wellmanifest.standard-adoption/v1",
                "mode": "enforce", "profile": "empty", "adoptions": []}), encoding="utf-8")
            for expected_valid, cases in ((False, invalid), (True, valid)):
                for name, model in cases:
                    catalog = deepcopy(baseline)
                    catalog["executionModels"] = {name: model}
                    original = deepcopy(catalog)
                    with self.subTest(kind="catalog", name=name, model=model):
                        self.assertEqual(not checker.catalog_findings(catalog), expected_valid)
                        self.assertEqual(catalog, original)
                    (root / "catalog.json").write_text(json.dumps(catalog), encoding="utf-8")
                    run = subprocess.run([sys.executable, str(ROOT / "scripts/standard_pack_check.py"),
                        "--root", str(root), "--catalog", "catalog.json", "--adoption", "adoption.json",
                        "--strict", "--format", "json"], capture_output=True, text=True, encoding="utf-8")
                    with self.subTest(kind="strict-cli", name=name, model=model):
                        self.assertEqual(run.returncode, 0 if expected_valid else 2, run.stderr)
                        payload = json.loads(run.stdout)
                        self.assertEqual(payload["ok"], expected_valid)
                        if not expected_valid:
                            self.assertTrue(all(item["code"] == "STD-PACK-CATALOG" for item in payload["findings"]))


    def test_adoption_artifacts_stay_in_the_canonical_checkout(self):
        import hashlib
        spec = importlib.util.spec_from_file_location("artifact_boundary_runtime", ROOT / "scripts/standard_pack_check.py")
        checker = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(checker)
        with tempfile.TemporaryDirectory(prefix="artifact-boundary-") as temporary:
            outer = Path(temporary)
            root = outer / "repository"
            root.mkdir()
            outside = outer / "outside.bin"
            data = b"Controlled public fixture; no production secrets."
            outside.write_bytes(data)
            (root / "inside.bin").write_bytes(data)
            digest = hashlib.sha256(data).hexdigest()
            catalog = {"schema": "wellmanifest.standard-pack-routing/v1",
                "packs": [{"id": "pack", "owns": ["fixture"]}],
                "profiles": {"empty": {"requirements": []}},
                "executionModels": {"fixture": {"maximumLevel": "S2", "authorizesEffects": False}}}
            (root / "catalog.json").write_text(json.dumps(catalog), encoding="utf-8")
            reads = []
            original_sha = checker.sha256
            def observed_sha(path):
                reads.append(path.resolve())
                return original_sha(path)
            checker.sha256 = observed_sha
            def check(target, valid):
                record = {"id": "pack", "level": "S2", "model": "fixture", "revision": "0" * 40,
                    "evidence": [{"level": level, "uri": "fixture://evidence/" + level, "sha256": "0" * 64}
                                 for level in ("S0", "S1", "S2")],
                    "artifacts": [{"target": target, "sha256": digest}]}
                findings = []
                reads.clear()
                with self.subTest(kind="artifact", target=target):
                    checker.adoption_artifact_findings(root, "pack", record, "S2", findings)
                    self.assertEqual(not findings, valid)
                    self.assertTrue(all(path.is_relative_to(root.resolve()) for path in reads))
                    if not valid:
                        self.assertEqual(reads, [])
                        self.assertEqual([item["code"] for item in findings], ["STD-ADOPTION-ARTIFACT"])
                (root / "adoption.json").write_text(json.dumps({"schema": "wellmanifest.standard-adoption/v1",
                    "mode": "enforce", "profile": "empty", "adoptions": [record]}), encoding="utf-8")
                run = subprocess.run([sys.executable, str(ROOT / "scripts/standard_pack_check.py"),
                    "--root", str(root), "--catalog", "catalog.json", "--adoption", "adoption.json",
                    "--strict", "--format", "json"], capture_output=True, text=True, encoding="utf-8")
                with self.subTest(kind="strict-cli", target=target):
                    self.assertEqual(run.returncode, 0 if valid else 1, run.stderr)
                    self.assertEqual(json.loads(run.stdout)["ok"], valid)
            check("inside.bin", True)
            check("./inside.bin", True)
            invalid = ("C:/fixture.bin", "C:relative.bin", "\\fixture.bin",
                       "\\\\fixture.invalid\\share\\fixture.bin", "folder\\..\\outside.bin",
                       "../outside.bin", str(outside.resolve()), "")
            if os.name != "nt":
                # Controlled POSIX filenames demonstrate that drive/root syntax
                # must be rejected portably rather than relying on missing files.
                (root / "C:").mkdir()
                for target in invalid[:5]:
                    (root / target).write_bytes(data)
            for target in invalid:
                check(target, False)
            with self.subTest(kind="symlink-confinement"):
                try:
                    (root / "escape.bin").symlink_to(outside)
                    (root / "confined.bin").symlink_to(root / "inside.bin")
                    directory = outer / "outside-directory"
                    directory.mkdir()
                    (directory / "file.bin").write_bytes(data)
                    (root / "linked-directory").symlink_to(directory, target_is_directory=True)
                except (OSError, NotImplementedError) as error:
                    self.skipTest(f"Symlink fixture unavailable: {error}")
                check("escape.bin", False)
                check("linked-directory/file.bin", False)
                check("confined.bin", True)


    def test_cached_output_errors_through_actual_source_and_bundle_cli(self):
        spec = importlib.util.spec_from_file_location("cached_output_cli_fixture", ROOT / "tests/governance-preflight-cache.test.py")
        fixture = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(fixture)
        case = fixture.CachedOutputTests("test_current_output_errors_are_combined_with_cached_results")
        case.test_current_output_errors_are_combined_with_cached_results()

    def test_ticket_suffix_boundaries_through_actual_git_activity(self):
        spec = importlib.util.spec_from_file_location(
            "ticket_suffix_git_fixture", ROOT / "tests/workspace_activity_test.py")
        fixture = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(fixture)
        case = fixture.WorkspaceActivityTests(
            "test_adjacent_suffixes_do_not_reserve_another_ticket")
        result = unittest.TestResult()
        case.run(result)
        self.assertEqual(result.testsRun, 1)
        self.assertFalse(result.skipped, result.skipped)
        self.assertTrue(result.wasSuccessful(), result.errors + result.failures)

    def test_pytest_base_through_actual_git_and_lifecycle(self):
        spec = importlib.util.spec_from_file_location(
            "pytest_base_runtime_fixture", ROOT / "tests/pytest_base_test.py")
        fixture = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(fixture)
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(fixture.PytestBaseTests)
        result = unittest.TestResult()
        suite.run(result)
        self.assertEqual(result.testsRun, 8)
        self.assertFalse(result.skipped, result.skipped)
        self.assertTrue(result.wasSuccessful(), result.errors + result.failures)

    def test_literal_git_paths_through_source_and_managed_installation(self):
        spec = importlib.util.spec_from_file_location(
            "literal_git_runtime_fixture", ROOT / "tests/workspace_activity_test.py")
        fixture = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(fixture)
        suite = unittest.TestSuite(fixture.WorkspaceActivityTests(name) for name in [
            "test_unicode_overlap_survives_different_git_quoting",
            "test_literal_git_paths_and_both_rename_endpoints"])
        result = unittest.TestResult()
        suite.run(result)
        self.assertEqual(result.testsRun, 2)
        self.assertFalse(result.skipped, result.skipped)
        self.assertTrue(result.wasSuccessful(), result.errors + result.failures)


if __name__ == "__main__":
    unittest.main()
