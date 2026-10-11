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


PIP_FIXTURE = '''import json, os, pathlib, sys
assert sys.prefix != sys.base_prefix, "system interpreter must never install"
pathlib.Path(os.environ["INSTALL_RECEIPT"]).write_text(json.dumps({"prefix": sys.prefix, "args": sys.argv[1:]}))
if os.environ.get("INSTALL_FAIL") == "1":
    raise SystemExit(17)
launcher = pathlib.Path(sys.executable).parent / "wellman"
launcher.write_text("#!/bin/sh\\nprintf 'wellman fixture\\\\n'\\n")
launcher.chmod(0o700)
'''


@unittest.skipIf(os.name == "nt", "Ubuntu workflow installers use POSIX shell and venv paths")
class RuntimeIsolationTests(unittest.TestCase):
    def run_installer(self, workflow, *, fail=False, runner_temp=True):
        with tempfile.TemporaryDirectory(prefix="wellman install fixture ") as directory:
            root = Path(directory)
            (root / ".governance").mkdir()
            (root / ".governance/manifest.json").write_text(json.dumps({"standard": {"version": "0.20.93"}}))
            scratch = root / "job temp with spaces"
            scratch.mkdir()
            binaries = root / "bin"
            binaries.mkdir()
            driver = root / "python-driver.py"
            driver.write_text(
                "import pathlib, subprocess, sys\n"
                "args = sys.argv[1:]\n"
                "if args[:2] == ['-m', 'pip']:\n"
                "    raise SystemExit('externally-managed-environment')\n"
                "if args[:2] == ['-m', 'venv']:\n"
                f"    subprocess.run([{sys.executable!r}, '-m', 'venv', '--without-pip', *args[2:]], check=True)\n"
                "    executable = pathlib.Path(args[-1]) / 'bin/python'\n"
                "    site = subprocess.check_output([str(executable), '-c', 'import sysconfig; print(sysconfig.get_path(\"purelib\"))'], text=True).strip()\n"
                f"    (pathlib.Path(site) / 'pip.py').write_text({PIP_FIXTURE!r})\n"
                "else:\n"
                f"    raise SystemExit(subprocess.call([{sys.executable!r}, *args]))\n"
            )
            python = binaries / "python3"
            python.write_text(f"#!/bin/sh\nexec {shlex.quote(sys.executable)} {shlex.quote(str(driver))} \"$@\"\n")
            python.chmod(0o700)
            exported = root / "github path"
            exported.touch()
            receipt = root / "install.json"
            env = dict(os.environ, PATH=str(binaries) + os.pathsep + os.environ["PATH"],
                       GITHUB_PATH=str(exported), TMPDIR=str(scratch),
                       INSTALL_RECEIPT=str(receipt), INSTALL_FAIL="1" if fail else "0")
            env.pop("RUNNER_TEMP", None)
            if runner_temp:
                env["RUNNER_TEMP"] = str(scratch)
            result = subprocess.run(["bash", "-c", install_body(*WORKFLOWS[workflow])],
                                    cwd=root, env=env, text=True, capture_output=True, timeout=30)
            self.assertTrue(receipt.exists(), result.stdout + result.stderr)
            installed = json.loads(receipt.read_text())
            self.assertEqual(Path(installed["prefix"]).parent, scratch)
            self.assertEqual(installed["args"][-1],
                             "git+https://github.com/wellmanifest/new-project.git@v0.20.93#subdirectory=packages/wellman")
            if fail:
                self.assertEqual(result.returncode, 17, result.stdout + result.stderr)
                self.assertEqual(exported.read_text(), "")
            else:
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertEqual(exported.read_text().splitlines(), [installed["prefix"] + "/bin"])
                env["PATH"] = exported.read_text().strip() + os.pathsep + env["PATH"]
                next_step = subprocess.run(["wellman", "--version"], env=env, cwd=root,
                                           text=True, capture_output=True, timeout=10)
                self.assertEqual(next_step.returncode, 0, next_step.stderr)
                self.assertEqual(next_step.stdout.strip(), "wellman fixture")

    def test_install_and_next_step_use_virtual_environment(self):
        for workflow in WORKFLOWS:
            with self.subTest(workflow=workflow):
                self.run_installer(workflow)

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
