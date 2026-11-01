"""Exercise the real shell preamble with a caller Git repository above TMPDIR."""
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(os.name == "posix" and shutil.which("bash") and shutil.which("git"),
                     "POSIX shell fixture containment requires Bash and Git")
class GovernanceFixtureTempTest(unittest.TestCase):
    def snapshot(self, root):
        result = {}
        for path in root.rglob("*"):
            mode = path.lstat().st_mode
            content = (os.readlink(path) if path.is_symlink() else
                       hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None)
            result[str(path.relative_to(root))] = (mode, content)
        return result

    def check_containment(self, relative):
        script = (ROOT / "tests/governance-scripts.test.sh").read_text()
        marker = 'python3 "$repo_root/tests/ticket-allocation-worktree.test.py"'
        self.assertIn(marker, script)
        preamble = script.split(marker, 1)[0]
        preamble = preamble.replace('python3 "$repo_root/tests/governance_fixture_temp_test.py"\n', '')
        lines = preamble.splitlines()
        self.assertEqual(sum(line.startswith("repo_root=") for line in lines), 1)
        preamble = "\n".join('repo_root="$1"' if line.startswith("repo_root=") else line
                             for line in lines)
        probe = preamble + '\nprintf "PRIVATE_ROOT=%s\\n" "$fixture_cache"\nmkdir "$fixture_cache/nonrepo"\ngit -C "$fixture_cache/nonrepo" rev-parse --show-toplevel\n'
        env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
        env.update(LC_ALL="C", GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull)
        with tempfile.TemporaryDirectory(prefix="governance-caller-") as directory:
            parent = Path(directory)
            subprocess.run(["git", "init", "--quiet", "-b", "main", str(parent)],
                           env=env, check=True)
            (parent / "sentinel.txt").write_text("preserve caller data\n")
            (parent / "temps").mkdir()
            before = self.snapshot(parent)
            env["TMPDIR"] = "temps" if relative else str(parent / "temps")
            result = subprocess.run(["bash", "-c", probe, "fixture-preamble", str(ROOT)],
                                    cwd=parent, env=env, capture_output=True, text=True, timeout=20)
            self.assertNotEqual(result.returncode, 0, "Git escaped the fixture root: " + result.stdout)
            self.assertIn("not a git repository", result.stderr)
            lines = result.stdout.splitlines()
            self.assertEqual(len(lines), 1)
            self.assertTrue(lines[0].startswith("PRIVATE_ROOT="))
            private = Path(lines[0].removeprefix("PRIVATE_ROOT="))
            self.assertTrue(private.is_absolute())
            self.assertFalse(private.exists(), "private fixture root leaked")
            self.assertEqual(self.snapshot(parent), before, "caller files or Git metadata changed")

    def test_absolute_tmpdir_preserves_caller_and_git_boundary(self):
        self.check_containment(False)

    def test_relative_tmpdir_preserves_caller_and_git_boundary(self):
        self.check_containment(True)


if __name__ == "__main__":
    unittest.main()
