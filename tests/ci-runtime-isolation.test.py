#!/usr/bin/env python3
"""Execute delivered installers with real venvs and an offline pip fixture."""
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = {
    "adopter": ("template/files/new-project-governance.workflow.yml", "Install wellman governance runtime"),
    "reusable": (".github/workflows/governance-gate-reusable.yml", "Install governance runtime"),
}


def install_body(path, step):
    lines = (ROOT / path).read_text().splitlines()
    start = next(i for i, line in enumerate(lines) if line.strip() == f"- name: {step}")
    start = next(i for i in range(start, len(lines)) if lines[i].strip() == "run: |") + 1
    body = []
    for line in lines[start:]:
        if line.strip() and not line.startswith("          "):
            break
        body.append(line[10:])
    return ("\n".join(body) + "\n").replace("${{ steps.version.outputs.standard }}", "0.20.93")


PIP_FIXTURE = '''import json, os, pathlib, site, sys
assert sys.prefix != sys.base_prefix, "system interpreter must never install"
pathlib.Path(os.environ["INSTALL_RECEIPT"]).write_text(json.dumps({"prefix": sys.prefix, "args": sys.argv[1:]}))
if os.environ.get("INSTALL_FAIL") == "1":
    raise SystemExit(17)
kind = os.environ.get("INSTALL_RUNTIME", "legacy")
choices = {
    "legacy": ("wellman", "wellman", "wellman.check:main"),
    "modern": ("wellmanifest-governance", "wellman-governance", "wellmanifest_governance_runtime.check:main"),
}
selected = list(choices) if kind == "ambiguous" else ([] if kind == "missing" else ["modern" if kind in {"malformed", "bad-version"} else kind])
for name in selected:
    distribution, command, entry = choices[name]
    if kind == "malformed":
        entry = "untrusted.module:main"
    metadata = pathlib.Path(site.getsitepackages()[0]) / (distribution.replace("-", "_") + "-1.0.dist-info")
    metadata.mkdir()
    metadata.joinpath("METADATA").write_text("Metadata-Version: 2.1\\nName: " + distribution + "\\nVersion: 1.0\\n")
    metadata.joinpath("entry_points.txt").write_text("[console_scripts]\\n" + command + " = " + entry + "\\n")
    launcher = pathlib.Path(sys.executable).parent / command
    launcher.write_text("#!/bin/sh\\nexit 13\\n" if kind == "bad-version" else "#!/bin/sh\\nprintf 'wellman fixture\\\\n'\\n")
    launcher.chmod(0o700)
'''


@unittest.skipIf(os.name == "nt", "Ubuntu workflow installers use POSIX shell and venv paths")
class RuntimeIsolationTests(unittest.TestCase):
    def run_installer(self, workflow, *, fail=False, runner_temp=True, case="base", nested=False, runtime="legacy"):
        with tempfile.TemporaryDirectory(prefix="wellman install fixture ") as directory:
            root = Path(directory)
            (root / ".governance").mkdir()
            (root / ".governance/manifest.json").write_text(json.dumps({"standard": {"version": "0.20.93"}}))
            target = root / "nested product" if nested else root
            (target / ".governance").mkdir(parents=True, exist_ok=True)
            revision = "a" * 40
            lock = {"schema": "new-project.lock/v1", "standard": {
                "id": "wellmanifest/new-project", "sourceRepository": "wellmanifest/new-project",
                "sourceRevision": revision, "publicationStatus": "published"}}
            if case == "tag": lock["standard"]["sourceRevision"] = "v0.20.96"
            if case == "identity": lock["standard"]["sourceRepository"] = "other/source"
            if case == "unpublished": lock["standard"]["publicationStatus"] = "unpublished-test"
            if case == "boolean": lock["standard"]["sourceRevision"] = True
            if case == "short": lock["standard"]["sourceRevision"] = "abcd1234"
            lockpath = target / ".governance/manifest.lock.json"
            lockpath.write_text(json.dumps(lock))
            if case == "duplicate":
                lockpath.write_text('{"schema":"ignored",' + json.dumps(lock)[1:])
            if case == "malformed": lockpath.write_text("not JSON")
            if case in {"missing", "protected", "bad-protected"}: lockpath.unlink()
            def git(*args):
                return subprocess.check_output(["git", *args], cwd=root, text=True).strip()
            git("init", "-q", "-b", "main")
            git("config", "user.name", "CI fixture")
            git("config", "user.email", "ci@example.invalid")
            git("config", "commit.gpgsign", "false")
            git("add", ".")
            git("commit", "-qm", "trusted base")
            base = git("rev-parse", "HEAD")
            # The candidate must not redirect acquisition, even through a valid lock.
            lock["standard"]["sourceRevision"] = "b" * 40
            lockpath.write_text(json.dumps(lock))
            (target / ".governance/manifest.json").write_text('{"standard":{"version":"999.0.0"}}')
            scratch = root / "job temp with spaces"
            scratch.mkdir()
            binaries = root / "bin"
            binaries.mkdir()
            driver = root / "python-driver.py"
            driver.write_text(
                "import pathlib, subprocess, sys\n"
                "args = sys.argv[1:]\n"
                "isolated = args[:1] == ['-I']\n"
                "if isolated: args = args[1:]\n"
                "if args[:2] == ['-m', 'pip']:\n"
                "    raise SystemExit('externally-managed-environment')\n"
                "if args[:2] == ['-m', 'venv']:\n"
                "    assert isolated, 'candidate modules must not shadow venv'\n"
                f"    subprocess.run([{sys.executable!r}, '-I', '-m', 'venv', '--without-pip', *args[2:]], check=True)\n"
                "    executable = pathlib.Path(args[-1]) / 'bin/python'\n"
                "    site = subprocess.check_output([str(executable), '-c', 'import sysconfig; print(sysconfig.get_path(\"purelib\"))'], text=True).strip()\n"
                f"    (pathlib.Path(site) / 'pip.py').write_text({PIP_FIXTURE!r})\n"
                "else:\n"
                f"    raise SystemExit(subprocess.call([{sys.executable!r}, *(['-I'] if isolated else []), *args]))\n"
            )
            python = binaries / "python3"
            python.write_text(f"#!/bin/sh\nexec {shlex.quote(sys.executable)} {shlex.quote(str(driver))} \"$@\"\n")
            python.chmod(0o700)
            # Candidate Python modules must not execute before the trusted gate.
            for module in ("json.py", "venv.py", "pip.py"):
                (root / module).write_text("raise RuntimeError('candidate module executed')\n")
            exported = root / "github path"
            exported.touch()
            receipt = root / "install.json"
            env = dict(os.environ, PATH=str(binaries) + os.pathsep + os.environ["PATH"],
                       GITHUB_PATH=str(exported), TMPDIR=str(scratch),
                       INSTALL_RECEIPT=str(receipt), INSTALL_FAIL="1" if fail else "0", INSTALL_RUNTIME=runtime)
            env.update(GOVERNANCE_ROOT=str(target), BASE_SHA=base, EVENT_NAME="pull_request",
                       BASE_REF="main", EVENT_SHA=base, EVENT_REF="refs/heads/main", DEFAULT_BRANCH="main",
                       PROTECTED_RUNTIME_SHA="")
            if case == "protected": env["PROTECTED_RUNTIME_SHA"] = "c" * 40
            if case == "bad-protected": env["PROTECTED_RUNTIME_SHA"] = "v0.20.96"
            if case == "untrusted-base": env["BASE_REF"] = "feature"
            if case == "missing-base-ref": env["BASE_REF"] = ""
            if case == "no-base": env["BASE_SHA"] = ""
            if case == "bad-base": env["BASE_SHA"] = "main"
            if case == "unknown-base": env["BASE_SHA"] = "d" * 40
            if case in {"schedule", "nondefault"}:
                env.update(EVENT_NAME="schedule", BASE_SHA="")
                if case == "nondefault": env["EVENT_REF"] = "refs/heads/feature"
            env.pop("RUNNER_TEMP", None)
            if runner_temp:
                env["RUNNER_TEMP"] = str(scratch)
            result = subprocess.run(["bash", "-c", install_body(*WORKFLOWS[workflow])],
                                    cwd=root, env=env, text=True, capture_output=True, timeout=30)
            if case in {"tag", "identity", "unpublished", "missing", "bad-protected",
                        "no-base", "bad-base", "unknown-base", "nondefault",
                        "boolean", "short", "duplicate", "malformed", "untrusted-base", "missing-base-ref"}:
                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertFalse(receipt.exists(), "rejected pin must not reach pip")
                self.assertEqual(exported.read_text(), "")
                self.assertFalse(list(scratch.glob("wellman-governance.*")))
                return
            self.assertTrue(receipt.exists(), result.stdout + result.stderr)
            installed = json.loads(receipt.read_text())
            self.assertEqual(Path(installed["prefix"]).parent, scratch)
            self.assertEqual(installed["args"][-1],
                             "git+https://github.com/wellmanifest/new-project.git@" +
                             ("c" * 40 if case == "protected" else revision) + "#subdirectory=packages/wellman")
            if runtime in {"missing", "ambiguous", "malformed", "bad-version"}:
                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertEqual(exported.read_text(), "")
                return
            if fail:
                self.assertEqual(result.returncode, 17, result.stdout + result.stderr)
                self.assertEqual(exported.read_text(), "")
            else:
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertEqual(exported.read_text().splitlines(), [installed["prefix"] + "/bin"])
                env["PATH"] = exported.read_text().strip() + os.pathsep + env["PATH"]
                command = "wellman-governance" if runtime == "modern" else "wellman"
                next_step = subprocess.run([command, "--version"], env=env, cwd=root,
                                           text=True, capture_output=True, timeout=10)
                self.assertEqual(next_step.returncode, 0, next_step.stderr)
                self.assertEqual(next_step.stdout.strip(), "wellman fixture")

    def test_untrusted_or_missing_pins_refuse_before_install(self):
        for workflow in WORKFLOWS:
            for case in ("tag", "identity", "unpublished", "missing", "bad-protected",
                         "no-base", "bad-base", "unknown-base", "nondefault",
                         "boolean", "short", "duplicate", "malformed", "untrusted-base", "missing-base-ref"):
                with self.subTest(workflow=workflow, case=case):
                    self.run_installer(workflow, case=case)

    def test_protected_initial_pin_and_trusted_default_branch(self):
        for workflow in WORKFLOWS:
            for case in ("protected", "schedule"):
                with self.subTest(workflow=workflow, case=case):
                    self.run_installer(workflow, case=case)

    def test_nested_target_uses_its_trusted_base_lock(self):
        for workflow in WORKFLOWS:
            with self.subTest(workflow=workflow):
                self.run_installer(workflow, nested=True)

    def test_install_and_next_step_use_virtual_environment(self):
        for workflow in WORKFLOWS:
            with self.subTest(workflow=workflow):
                self.run_installer(workflow)

    def test_adopter_accepts_modern_runtime(self):
        self.run_installer("adopter", runtime="modern")

    def test_adopter_rejects_untrusted_runtime_identity_before_export(self):
        for runtime in ("missing", "ambiguous", "malformed", "bad-version"):
            with self.subTest(runtime=runtime):
                self.run_installer("adopter", runtime=runtime)

    def test_failed_install_stops_without_exporting_runtime(self):
        for workflow in WORKFLOWS:
            with self.subTest(workflow=workflow):
                self.run_installer(workflow, fail=True)

    def test_missing_runner_temp_uses_temporary_directory(self):
        for workflow in WORKFLOWS:
            with self.subTest(workflow=workflow):
                self.run_installer(workflow, runner_temp=False)


if __name__ == "__main__":
    unittest.main()
