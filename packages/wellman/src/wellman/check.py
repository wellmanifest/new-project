"""Thin runtime wrapper for the wellmanifest governance gate.

This module resolves and delegates to the canonical governance_check.py
from the adopted standard, distributed as part of this package.
"""
from __future__ import annotations

import runpy
import sys
from pathlib import Path


def _find_checker() -> Path:
    """Locate governance_check.py bundled with this package."""
    pkg_dir = Path(__file__).parent
    bundled = pkg_dir / "_bundled" / "governance_check.py"
    if bundled.is_file():
        return bundled
    # Fallback: look in the new-project scripts directory (dev mode)
    dev_path = Path(__file__).resolve().parents[4] / "scripts" / "governance_check.py"
    if dev_path.is_file():
        return dev_path
    raise FileNotFoundError(
        "governance_check.py not found. Reinstall wellman."
    )


def _checker_args(args: list[str]) -> list[str]:
    """Translate the documented ``wellman check [--json]`` form to checker flags."""
    if args[:1] == ["check"]:
        args = args[1:]
    translated: list[str] = []
    for arg in args:
        translated.extend(["--format", "json"] if arg == "--json" else [arg])
    return translated


def run_check(root: str | Path | None = None, args: list[str] | None = None) -> int:
    """Run the governance gate programmatically."""
    checker = _find_checker()
    argv = [str(checker)]
    if root:
        argv.extend(["--root", str(root)])
    if args:
        argv.extend(_checker_args(args))
    old_argv = sys.argv
    try:
        sys.argv = argv
        runpy.run_path(str(checker), run_name="__main__")
        return 0
    except SystemExit as e:
        return e.code if isinstance(e.code, int) else 1
    finally:
        sys.argv = old_argv


def main() -> None:
    """CLI entry point."""
    if sys.argv[1:] == ["--version"]:
        from wellman import __version__

        print(f"wellman {__version__}")
        return
    checker = _find_checker()
    sys.argv = [str(checker), *_checker_args(sys.argv[1:])]
    runpy.run_path(str(checker), run_name="__main__")
