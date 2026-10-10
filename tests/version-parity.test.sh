#!/usr/bin/env bash
# Verification for ticket-327: version parity validation in governance gate.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

python3 - <<'PY'
import sys
import tempfile
import json
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

test_version_parity_pass()
test_pyproject_version_mismatch()
test_setup_py_version_mismatch()
test_package_json_mismatch()
test_cargo_toml_mismatch()
test_init_py_version_mismatch()
test_dynamic_init_py_ignored()
print("All version-parity tests passed successfully.")
PY

echo "version-parity.test.sh OK"
