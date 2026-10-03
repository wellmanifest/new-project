#!/usr/bin/env python3
"""Actual allocator effects and managed host/runtime boundary regressions."""
from contextlib import contextmanager
import importlib.util
import json
import os
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



if __name__ == "__main__":
    unittest.main()
