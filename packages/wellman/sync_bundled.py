#!/usr/bin/env python3
"""Copy the governance checker and its sibling modules into ``_bundled``.

``governance_check.py`` loads helper modules from its own directory, so the
package must ship the complete closure byte-for-byte. ``--check`` reports drift
without writing and is run by ``tests/wellman-package.test.sh``.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parent
SCRIPTS = PACKAGE_ROOT.parents[1] / "scripts"
BUNDLED = PACKAGE_ROOT / "src" / "wellman" / "_bundled"

# Transitive closure of modules governance_check.py loads next to itself.
MODULES = (
    "agent_host_check.py",
    "change_lease_check.py",
    "check_required_checks.py",
    "decision_record.py",
    "governance_check.py",
    "repository_policy.py",
    "snapshot_migration.py",
    "ticket_activity.py",
    "ticket_input.py",
)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="report drift without writing")
    args = parser.parse_args(argv)
    drift = []
    for name in MODULES:
        source = (SCRIPTS / name).read_bytes()
        target = BUNDLED / name
        if target.is_file() and target.read_bytes() == source:
            continue
        drift.append(name)
        if not args.check:
            target.write_bytes(source)
    extra = sorted(
        p.name for p in BUNDLED.glob("*.py") if p.name != "__init__.py" and p.name not in MODULES
    )
    if args.check and (drift or extra):
        for name in drift:
            print(f"WELLMAN-BUNDLE-DRIFT: _bundled/{name} differs from scripts/{name}", file=sys.stderr)
        for name in extra:
            print(f"WELLMAN-BUNDLE-EXTRA: _bundled/{name} is not a declared module", file=sys.stderr)
        print("remediation: python3 packages/wellman/sync_bundled.py", file=sys.stderr)
        return 1
    if not args.check:
        print(f"synchronized {len(drift)} of {len(MODULES)} bundled modules")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
