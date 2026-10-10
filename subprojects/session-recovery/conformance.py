#!/usr/bin/env python3
"""
wellmanifest/session-recovery conformance tool.

Checks session stores, safely salvages corrupted SQLite/JSONL files,
emits verified salvage receipts, and validates workspace state rehydration envelopes.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Tuple


def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def check_sqlite_store(path: Path) -> Tuple[str, Optional[str], int]:
    """
    Checks SQLite store integrity.
    Returns (status, error_message, step_count).
    """
    if not path.is_file():
        return "CORRUPTED", f"File does not exist: {path}", 0

    try:
        conn = sqlite3.connect(str(path), timeout=5.0)
        cur = conn.cursor()
        cur.execute("PRAGMA quick_check;")
        res = cur.fetchone()
        if not res or res[0] != "ok":
            msg = res[0] if res else "empty result"
            conn.close()
            return "CORRUPTED", f"quick_check failed: {msg}", 0

        # Try counting steps if table exists
        step_count = 0
        try:
            cur.execute("SELECT count(*) FROM steps;")
            step_count = int(cur.fetchone()[0])
        except Exception:
            pass

        conn.close()
        return "HEALTHY", None, step_count
    except Exception as e:
        return "CORRUPTED", str(e), 0


def salvage_sqlite_store(source_path: Path, output_path: Path) -> Dict[str, Any]:
    """
    Safely salvages a corrupted SQLite store by generating a SQL dump and reconstructing it.
    Emits a wellmanifest.session-recovery-salvage/v1 receipt.
    """
    session_id = source_path.stem
    orig_sha256 = compute_sha256(source_path)

    # 1. Quarantine
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d_%H%M%S")
    quarantine_path = source_path.parent / f"{source_path.name}.corrupt.{timestamp}"
    shutil.copy2(source_path, quarantine_path)

    # 2. Dump SQL via sqlite3 CLI
    dump_proc = subprocess.run(
        ["sqlite3", str(source_path), ".dump"],
        capture_output=True,
        text=False
    )
    if dump_proc.returncode != 0 and not dump_proc.stdout:
        return {
            "schema": "wellmanifest.session-recovery-salvage/v1",
            "sessionId": session_id,
            "originalStorePath": str(source_path),
            "quarantinedPath": str(quarantine_path),
            "recoveredStorePath": str(output_path),
            "originalSha256": orig_sha256,
            "recoveredSha256": "0" * 64,
            "salvagedStepCount": 0,
            "diagnosticFinding": f"Failed to dump SQL: {dump_proc.stderr.decode('utf-8', errors='replace')}",
            "salvagedAt": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "status": "FAILED",
        }

    # 3. Rebuild in target location
    if output_path.exists():
        output_path.unlink()

    restore_proc = subprocess.run(
        ["sqlite3", str(output_path)],
        input=dump_proc.stdout,
        capture_output=True
    )

    # 4. Check integrity of reconstructed database
    status, diag, step_count = check_sqlite_store(output_path)
    if status != "HEALTHY":
        return {
            "schema": "wellmanifest.session-recovery-salvage/v1",
            "sessionId": session_id,
            "originalStorePath": str(source_path),
            "quarantinedPath": str(quarantine_path),
            "recoveredStorePath": str(output_path),
            "originalSha256": orig_sha256,
            "recoveredSha256": compute_sha256(output_path) if output_path.exists() else "0" * 64,
            "salvagedStepCount": step_count,
            "diagnosticFinding": f"Rebuilt database failed integrity check: {diag}",
            "salvagedAt": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "status": "FAILED",
        }

    recovered_sha256 = compute_sha256(output_path)
    return {
        "schema": "wellmanifest.session-recovery-salvage/v1",
        "sessionId": session_id,
        "originalStorePath": str(source_path),
        "quarantinedPath": str(quarantine_path),
        "recoveredStorePath": str(output_path),
        "originalSha256": orig_sha256,
        "recoveredSha256": recovered_sha256,
        "salvagedStepCount": step_count,
        "salvagedAt": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "status": "COMPLETED",
    }


def synthesize_rehydration_envelope(workspace_root: Path, ticket_id: str, session_id: str) -> Dict[str, Any]:
    """
    Synthesizes a workspace state rehydration envelope when session transcript is unavailable.
    """
    head_sha = "0000000000000000000000000000000000000000"
    target_branch = "main"
    try:
        proc = subprocess.run(
            ["git", "-C", str(workspace_root), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True
        )
        head_sha = proc.stdout.strip()
        bproc = subprocess.run(
            ["git", "-C", str(workspace_root), "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True
        )
        target_branch = bproc.stdout.strip()
    except Exception:
        pass

    ticket_dir = workspace_root / "project" / ticket_id
    intent_file = ticket_dir / "intent.json"
    intent_sha256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    if intent_file.is_file():
        intent_sha256 = compute_sha256(intent_file)

    prompt = (
        f"# SYSTEM_SESSION_REHYDRATION\n\n"
        f"The previous interactive conversational context for session `{session_id}` was lost or salvaged.\n"
        f"Your working context has been rehydrated from authoritative workspace state:\n\n"
        f"- **Workspace Root**: `{workspace_root}`\n"
        f"- **Branch / HEAD**: `{target_branch}` (`{head_sha}`)\n"
        f"- **Active Ticket**: `{ticket_id}` (intent digest `{intent_sha256}`)\n"
        f"- **Policy**: Memory is an advisory cache. Resume work by checking `intent.json`, active criteria, and `git status`."
    )

    return {
        "schema": "wellmanifest.session-recovery-rehydration/v1",
        "sessionId": session_id,
        "repositoryPath": str(workspace_root),
        "targetBranch": target_branch,
        "headSha": head_sha,
        "ticketId": ticket_id,
        "intentSha256": intent_sha256,
        "activePhase": "edit",
        "lastCheckpointRef": None,
        "rehydrationPrompt": prompt,
        "createdAt": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }


def main():
    parser = argparse.ArgumentParser(description="LLM Session Recovery Conformance Utility")
    sub = parser.add_subparsers(dest="cmd", required=True)

    check_p = sub.add_parser("check", help="Check integrity of a session database")
    check_p.add_argument("store", type=Path, help="Path to session database")

    salvage_p = sub.add_parser("salvage", help="Quarantine and salvage a corrupted SQLite session database")
    salvage_p.add_argument("store", type=Path, help="Path to corrupted database")
    salvage_p.add_argument("--out", type=Path, required=True, help="Destination path for recovered database")
    salvage_p.add_argument("--receipt", type=Path, help="Optional destination path for salvage receipt JSON")

    rehydrate_p = sub.add_parser("rehydrate", help="Generate rehydration envelope from workspace state")
    rehydrate_p.add_argument("--root", type=Path, default=Path.cwd(), help="Workspace root")
    rehydrate_p.add_argument("--ticket", required=True, help="Ticket ID (e.g. ticket-001)")
    rehydrate_p.add_argument("--session-id", default="salvaged-session", help="Session ID")

    args = parser.parse_args()

    if args.cmd == "check":
        status, diag, steps = check_sqlite_store(args.store)
        print(json.dumps({
            "storePath": str(args.store),
            "status": status,
            "stepCount": steps,
            "diagnostic": diag
        }, indent=2))
        sys.exit(0 if status == "HEALTHY" else 1)

    elif args.cmd == "salvage":
        receipt = salvage_sqlite_store(args.store, args.out)
        print(json.dumps(receipt, indent=2))
        if args.receipt:
            with open(args.receipt, "w") as f:
                json.dump(receipt, f, indent=2)
        sys.exit(0 if receipt.get("status") == "COMPLETED" else 1)

    elif args.cmd == "rehydrate":
        envelope = synthesize_rehydration_envelope(args.root, args.ticket, args.session_id)
        print(json.dumps(envelope, indent=2))
        sys.exit(0)


if __name__ == "__main__":
    main()
