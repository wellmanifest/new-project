#!/usr/bin/env bash
# Verification for ticket-327: version parity validation in governance gate.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

python3 - <<'PY'
import sys
import tempfile
import json
import subprocess
from pathlib import Path

# Add scripts directory to sys.path
root = Path(".").resolve()
sys.path.insert(0, str(root / "scripts"))

from governance_check import check_version_parity, Report

def test_version_parity_pass():
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        (t / "VERSION").write_text("1.2.3\n", encoding="utf-8")
        (t / "pyproject.toml").write_text('[project]\nname="demo"\nversion="1.2.3"\n', encoding="utf-8")
        (t / "setup.py").write_text('version = "1.2.3"\n', encoding="utf-8")
        (t / "package.json").write_text(json.dumps({"name": "demo", "version": "1.2.3"}), encoding="utf-8")
        (t / "Cargo.toml").write_text('[package]\nname = "demo"\nversion = "1.2.3"\n', encoding="utf-8")
        pkg = t / "src" / "demo"
        pkg.mkdir(parents=True)
        (pkg / "__init__.py").write_text('__version__ = "1.2.3"\n', encoding="utf-8")

        report = Report(t)
        check_version_parity(t, {}, report)
        assert report.errors == 0, f"Expected 0 errors, got: {report.findings}"
        print("  ✓ test_version_parity_pass")

def test_pyproject_version_mismatch():
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        (t / "VERSION").write_text("1.2.3\n", encoding="utf-8")
        (t / "pyproject.toml").write_text('[project]\nname="demo"\nversion="1.2.4"\n', encoding="utf-8")

        report = Report(t)
        check_version_parity(t, {}, report)
        assert report.errors == 1, f"Expected 1 error, got: {report.findings}"
        assert report.findings[0].code == "GOV-VERSION-001"
        assert "pyproject.toml" in report.findings[0].message
        print("  ✓ test_pyproject_version_mismatch")

def test_setup_py_version_mismatch():
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        (t / "VERSION").write_text("2.2.51\n", encoding="utf-8")
        (t / "setup.py").write_text('setup(name="fixos", version="2.2.48")\n', encoding="utf-8")

        report = Report(t)
        check_version_parity(t, {}, report)
        assert report.errors == 1, f"Expected 1 error, got: {report.findings}"
        assert report.findings[0].code == "GOV-VERSION-001"
        assert "setup.py" in report.findings[0].message
        print("  ✓ test_setup_py_version_mismatch")

def test_package_json_mismatch():
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        (t / "VERSION").write_text("1.0.0\n", encoding="utf-8")
        (t / "package.json").write_text(json.dumps({"version": "0.9.0"}), encoding="utf-8")

        report = Report(t)
        check_version_parity(t, {}, report)
        assert report.errors == 1, f"Expected 1 error, got: {report.findings}"
        assert report.findings[0].code == "GOV-VERSION-001"
        assert "package.json" in report.findings[0].message
        print("  ✓ test_package_json_mismatch")

def test_cargo_toml_mismatch():
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        (t / "VERSION").write_text("0.5.0\n", encoding="utf-8")
        (t / "Cargo.toml").write_text('[package]\nname = "demo"\nversion = "0.5.1"\n', encoding="utf-8")

        report = Report(t)
        check_version_parity(t, {}, report)
        assert report.errors == 1, f"Expected 1 error, got: {report.findings}"
        assert report.findings[0].code == "GOV-VERSION-001"
        assert "Cargo.toml" in report.findings[0].message
        print("  ✓ test_cargo_toml_mismatch")

def test_init_py_version_mismatch():
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        (t / "VERSION").write_text("2.2.51\n", encoding="utf-8")
        pkg = t / "src" / "demo"
        pkg.mkdir(parents=True)
        (pkg / "__init__.py").write_text('__version__ = "2.2.49"\n', encoding="utf-8")

        report = Report(t)
        check_version_parity(t, {}, report)
        assert report.errors == 1, f"Expected 1 error, got: {report.findings}"
        assert report.findings[0].code == "GOV-VERSION-001"
        assert "__version__" in report.findings[0].message
        print("  ✓ test_init_py_version_mismatch")

def test_dynamic_init_py_ignored():
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        (t / "VERSION").write_text("2.2.51\n", encoding="utf-8")
        pkg = t / "src" / "demo"
        pkg.mkdir(parents=True)
        (pkg / "__init__.py").write_text('__version__ = _get_version()\n', encoding="utf-8")

        report = Report(t)
        check_version_parity(t, {}, report)
        assert report.errors == 0, f"Expected 0 errors, got: {report.findings}"
        print("  ✓ test_dynamic_init_py_ignored")

def test_ignored_runtime_tree_is_skipped():
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        subprocess.run(["git", "init", "-q"], cwd=t, check=True)
        (t / "VERSION").write_text("1.2.3\n", encoding="utf-8")
        (t / ".gitignore").write_text(".run/\n", encoding="utf-8")
        pkg = t / "src" / "demo"
        pkg.mkdir(parents=True)
        (pkg / "__init__.py").write_text('__version__ = "1.2.3"\n', encoding="utf-8")
        vendor = t / ".run" / "venv" / "lib" / "site-packages" / "pip"
        vendor.mkdir(parents=True)
        (vendor / "__init__.py").write_text('__version__ = "25.3"\n', encoding="utf-8")

        report = Report(t)
        check_version_parity(t, {}, report)
        assert report.errors == 0, f"git-ignored runtime tree must not be scanned: {report.findings}"
        print("  ✓ test_ignored_runtime_tree_is_skipped")

def test_tracked_init_py_mismatch_still_detected_in_git_checkout():
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        subprocess.run(["git", "init", "-q"], cwd=t, check=True)
        (t / "VERSION").write_text("1.2.3\n", encoding="utf-8")
        pkg = t / "src" / "demo"
        pkg.mkdir(parents=True)
        (pkg / "__init__.py").write_text('__version__ = "9.9.9"\n', encoding="utf-8")

        report = Report(t)
        check_version_parity(t, {}, report)
        assert report.errors == 1, f"tracked package initializer must stay in scope: {report.findings}"
        assert report.findings[0].code == "GOV-VERSION-001"
        print("  ✓ test_tracked_init_py_mismatch_still_detected_in_git_checkout")

def test_nested_subpackage_manifest_parity_and_refusals():
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        subprocess.run(["git", "init", "-q"], cwd=t, check=True)
        (t / "VERSION").write_text("0.2.0a1\n", encoding="utf-8")
        (t / "pyproject.toml").write_text('[project]\nname = "main-pkg"\nversion = "0.2.0a1"\n', encoding="utf-8")
        root_pkg = t / "src" / "main_pkg"
        root_pkg.mkdir(parents=True)
        (root_pkg / "__init__.py").write_text('__version__ = "0.2.0a1"\n', encoding="utf-8")

        sub = t / "extensions" / "sub_pkg"
        sub_src = sub / "src" / "sub_pkg"
        sub_src.mkdir(parents=True)
        (sub / "pyproject.toml").write_text('[project]\nname = "sub-pkg"\nversion = "0.2.0"\n', encoding="utf-8")
        (sub_src / "__init__.py").write_text('__version__ = "0.2.0"\n', encoding="utf-8")

        report = Report(t)
        check_version_parity(t, {}, report)
        assert report.errors == 0, f"Matching nested subpackage must pass: {report.findings}"

        (sub_src / "__init__.py").write_text('__version__ = "0.1.9"\n', encoding="utf-8")
        report = Report(t)
        check_version_parity(t, {}, report)
        assert report.errors == 1 and report.findings[0].code == "GOV-VERSION-001", report.findings
        assert "extensions/sub_pkg/pyproject.toml" in report.findings[0].message

        # Tool-only nested pyproject.toml without version must fall back to root VERSION.
        (sub / "pyproject.toml").write_text('[tool.pytest.ini_options]\ntestpaths = ["tests"]\n', encoding="utf-8")
        (sub_src / "__init__.py").write_text('__version__ = "0.2.0a1"\n', encoding="utf-8")
        report = Report(t)
        check_version_parity(t, {}, report)
        assert report.errors == 0, f"Tool-only nested pyproject must fall back to VERSION: {report.findings}"

        # Symlinked nested pyproject.toml must fail closed.
        outside = Path(tmp) / "outside-pyproject.toml"
        outside.write_text('[project]\nname = "sub-pkg"\nversion = "9.9.9"\n', encoding="utf-8")
        (sub / "pyproject.toml").unlink()
        (sub / "pyproject.toml").symlink_to(outside)
        report = Report(t)
        check_version_parity(t, {}, report)
        assert report.errors == 1 and report.findings[0].code == "GOV-VERSION-001", report.findings
        print("  ✓ test_nested_subpackage_manifest_parity_and_refusals")

test_version_parity_pass()
test_pyproject_version_mismatch()
test_setup_py_version_mismatch()
test_package_json_mismatch()
test_cargo_toml_mismatch()
test_init_py_version_mismatch()
test_dynamic_init_py_ignored()
test_ignored_runtime_tree_is_skipped()
test_tracked_init_py_mismatch_still_detected_in_git_checkout()
test_nested_subpackage_manifest_parity_and_refusals()
print("All version-parity tests passed successfully.")
PY

echo "version-parity.test.sh OK"
