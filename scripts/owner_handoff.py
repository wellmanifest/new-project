#!/usr/bin/env python3
"""Explicit consented handoff for a local canonical worktree."""
from __future__ import annotations
import argparse
import fcntl
from datetime import datetime, timedelta, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys

SCHEMA = "new-project.owner-handoff/v1"
MAX_BYTES = 1024 * 1024
DIGEST = re.compile(r"[0-9a-f]{64}\Z")

def _canonical_errors(lease):
    spec = importlib.util.spec_from_file_location("_owner_change_lease", Path(__file__).with_name("change_lease_check.py"))
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module.validate_lease(lease)

def _digest(raw):
    return hashlib.sha256(raw).hexdigest()

def _encoded(value):
    return (json.dumps(value, sort_keys=True, indent=2) + "\n").encode()

def _read(path):
    if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_BYTES:
        raise ValueError("unsafe lease path")
    return path.read_bytes()

def _atomic(path, raw):
    spec = importlib.util.spec_from_file_location("_terminal_owner_release", Path(__file__).with_name("terminal_lease_release.py"))
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    with module.directory(path.parent) as (fd, verify):
        module.atomic_at(fd, path.name, raw)
        verify()

def _git(path, *args):
    return subprocess.run(["git", "-C", str(path), *args], capture_output=True, check=True, timeout=20).stdout.decode()

def _content_snapshot(path):
    names = _git(path, "ls-files", "-co", "--exclude-standard", "-z").encode()
    digest = hashlib.sha256()
    for name in filter(None, names.decode().split("\0")):
        candidate = path / name
        if candidate.is_symlink() or not candidate.is_file() or candidate.stat().st_size > MAX_BYTES:
            raise ValueError("unsafe dirty snapshot path")
        digest.update(name.encode() + b"\0" + candidate.read_bytes())
    return digest.hexdigest()

def _request(request):
    fields = {"schema", "requestId", "worktreeId", "ownerActor", "ownerSession", "consent", "expectedRevision", "expectedFencingToken", "expectedLeaseSha256", "expectedHeadSha256", "expectedDirtySha256", "targetOwnerActor", "targetOwnerSession", "ttlSeconds"}
    if not isinstance(request, dict) or set(request) != fields or request["schema"] != SCHEMA:
        raise ValueError("invalid handoff request")
    if request["consent"] is not True or request["ownerActor"] == request["targetOwnerActor"]:
        raise ValueError("explicit distinct owner consent required")
    for key in ("requestId", "worktreeId", "ownerActor", "ownerSession", "targetOwnerActor", "targetOwnerSession"):
        if not isinstance(request[key], str) or not 1 <= len(request[key]) <= 160:
            raise ValueError("invalid handoff identity")
    for key in ("expectedRevision", "expectedFencingToken", "ttlSeconds"):
        if type(request[key]) is not int or request[key] <= 0 or (key == "ttlSeconds" and request[key] > 7200):
            raise ValueError("invalid handoff bounds")
    for key in ("expectedLeaseSha256", "expectedHeadSha256", "expectedDirtySha256"):
        if not isinstance(request[key], str) or not DIGEST.fullmatch(request[key]):
            raise ValueError("invalid handoff digest")

def _handoff_locked(root, request, *, apply=False, actor=None, session=None, authorization_fd=None):
    _request(request)
    root = Path(root).resolve()
    journal = root / ".subactor/receipts/owner-handoff" / (_digest(_encoded(request)) + ".json")
    lease_path = root / ".subactor/leases" / (request["worktreeId"] + ".json")
    raw = _read(lease_path)
    lease = json.loads(raw)
    if _canonical_errors(lease):
        raise ValueError("invalid canonical lease")
    if lease.get("ownerActor") != request["ownerActor"] or lease.get("ownerSession") != request["ownerSession"]:
        if journal.exists():
            saved = json.loads(_read(journal))
            if saved.get("request") == request and lease == saved.get("successor"):
                if apply and authorization_fd is None:
                    raise ValueError("protected authorization context required")
                return saved["result"]
        raise ValueError("lease owner mismatch")
    if lease.get("leaseRevision") != request["expectedRevision"] or lease.get("fencingToken") != request["expectedFencingToken"]:
        raise ValueError("lease fencing mismatch")
    if _digest(raw) != request["expectedLeaseSha256"]:
        raise ValueError("lease CAS mismatch")
    if lease.get("publicationFrozen") or lease.get("phase") in {"merged", "closed", "cancelled", "frozen"}:
        raise ValueError("frozen ownership cannot be handed off")
    if apply and (actor != request["ownerActor"] or session != request["ownerSession"]):
        raise ValueError("old-owner invocation context required")
    if apply:
        if authorization_fd is None:
            raise ValueError("protected authorization context required")
        authorization = json.loads(__import__("os").read(authorization_fd, MAX_BYTES + 1))
        if (authorization.get("schema") != "new-project.owner-handoff-authorization/v1"
                or authorization.get("ownerActor") != request["ownerActor"]
                or authorization.get("ownerSession") != request["ownerSession"]
                or authorization.get("requestDigest") != _digest(_encoded(request))
                or authorization.get("consent") is not True):
            raise ValueError("protected authorization mismatch")
        authorization_digest = _digest(_encoded(authorization))
    else:
        authorization_digest = None
    worktree = root / ".worktrees" / request["worktreeId"]
    if worktree.is_symlink() or not worktree.is_dir():
        raise ValueError("canonical worktree unavailable")
    head = _git(worktree, "rev-parse", "HEAD").strip()
    branch = _git(worktree, "symbolic-ref", "-q", "HEAD").strip()
    if branch != lease.get("branchRef"):
        raise ValueError("branch identity changed")
    dirty = _content_snapshot(worktree)
    if _digest(head.encode()) != request["expectedHeadSha256"]:
        raise ValueError("HEAD changed")
    if dirty != request["expectedDirtySha256"]:
        raise ValueError("dirty snapshot changed")
    if journal.exists():
        saved = json.loads(_read(journal))
        if saved.get("request") != request or saved.get("successor", {}).get("ownerActor") != request["targetOwnerActor"]:
            raise ValueError("handoff replay mismatch")
        if apply and authorization_fd is None:
            raise ValueError("protected authorization context required")
        return saved["result"]
    successor = dict(lease)
    successor.update(ownerActor=request["targetOwnerActor"], ownerSession=request["targetOwnerSession"], leaseRevision=lease["leaseRevision"] + 1, fencingToken=lease["fencingToken"] + 1, eventSequence=lease["eventSequence"] + 1, issuedAt=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), heartbeatAt=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), headSha=head, expiresAt=(datetime.now(timezone.utc) + timedelta(seconds=request["ttlSeconds"])).strftime("%Y-%m-%dT%H:%M:%SZ"), previousReceiptRef=str(journal))
    result = {"status": "handoff", "leaseRevision": successor["leaseRevision"], "fencingToken": successor["fencingToken"], "head": head, "branch": branch}
    if not apply:
        return {**result, "status": "planned", "grantsAuthority": False}
    record = {"schema": SCHEMA, "request": request, "authorizationSha256": authorization_digest, "originalLease": lease, "originalLeaseSha256": _digest(raw), "head": head, "dirtySha256": dirty, "successor": successor, "result": result}
    _atomic(journal, _encoded(record))
    if _digest(_read(lease_path)) != request["expectedLeaseSha256"]:
        raise ValueError("lease changed before replacement")
    _atomic(lease_path, _encoded(successor))
    return result

def handoff(root, request, *, apply=False, actor=None, session=None, authorization_fd=None):
    """Serialize observation, journal and replacement in the canonical slot."""
    root = Path(root).resolve()
    lock_dir = root / ".subactor" / "leases"
    lock_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
    lock = lock_dir / (request.get("worktreeId", "invalid") + ".lock")
    if lock.is_symlink():
        raise ValueError("unsafe lease lock")
    with lock.open("a+") as stream:
        fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
        return _handoff_locked(root, request, apply=apply, actor=actor, session=session, authorization_fd=authorization_fd)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--request", type=Path, required=True)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--actor")
    parser.add_argument("--session")
    parser.add_argument("--authorization-fd", type=int)
    args = parser.parse_args()
    print(json.dumps(handoff(args.root, json.loads(args.request.read_text()), apply=args.apply, actor=args.actor, session=args.session, authorization_fd=args.authorization_fd)))
