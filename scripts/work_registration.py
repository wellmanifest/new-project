#!/usr/bin/env python3
"""Read-only registration consistency check; never installation or Git authority."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
SCHEMA_PATH = Path(__file__).resolve().parent.parent / "governance/work-registration.schema.json"
ACTIVE = {"editing", "publication"}
TERMINAL = {"merged", "cancelled"}
TRANSITIONS = {
    "queued": {"queued", "blocked", "editing", "cancelled"},
    "blocked": {"blocked", "queued", "editing", "cancelled"},
    "editing": {"editing", "blocked", "publication", "cancelled"},
    "publication": {"publication", "editing", "blocked", "merged", "cancelled"},
    "merged": {"merged"},
    "cancelled": {"cancelled"},
}


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=True, allow_nan=False).encode()).hexdigest()


def effect_key(repository, request, effect):
    return digest([repository, request, effect])


def reject_constant(value):
    raise ValueError("Non-finite JSON number")


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON object key")
        result[key] = value
    return result


def load(path):
    if path.is_symlink():
        raise ValueError("Symlinked input is not accepted")
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object,
                      parse_constant=reject_constant)


def shape_errors(value, shape, definitions, path="$"):
    """Evaluate only the keywords used by this bundled closed schema."""
    if "$ref" in shape:
        return shape_errors(value, definitions[shape["$ref"].split("/")[-1]], definitions, path)
    if "anyOf" in shape:
        return [] if any(not shape_errors(value, s, definitions, path) for s in shape["anyOf"]) else [path]
    if "const" in shape and value != shape["const"]:
        return [path]
    if "enum" in shape and value not in shape["enum"]:
        return [path]
    kind = shape.get("type")
    types = {"object": dict, "array": list, "string": str, "integer": int,
             "boolean": bool, "null": type(None)}
    if kind and type(value) is not types[kind]:
        return [path]
    if kind == "object":
        if set(value) != set(shape["required"]):
            return [path]
        return [e for key, spec in shape["properties"].items()
                for e in shape_errors(value[key], spec, definitions, path + "." + key)]
    if kind == "array":
        return [e for i, item in enumerate(value)
                for e in shape_errors(item, shape["items"], definitions, f"{path}[{i}]")]
    if kind == "string":
        if not shape.get("minLength", 0) <= len(value) <= shape.get("maxLength", len(value)):
            return [path]
        if "pattern" in shape and re.fullmatch(shape["pattern"], value) is None:
            return [path]
    if kind == "integer" and value < shape.get("minimum", value):
        return [path]
    return []


def relative_path(value):
    return (isinstance(value, str) and bool(value) and not value.startswith("/")
            and not any(c in value for c in "\\:\x00\n\r")
            and all(part not in {"", ".", ".."} for part in value.split("/")))


def request_findings(request, effects, inventory, add):
    rid, state = request["id"], request["state"]
    binding, pr = request["binding"], request["pr"]
    pending = {e["effect"] for e in effects if e["requestId"] == rid}
    for field, effect in (("issue", "ensure-issue"), ("planfileTicket", "ensure-planfile-ticket")):
        if request[field] is None and effect not in pending:
            add("REG-BINDING", rid, f"Missing {field} and durable recovery effect")
        if request[field] is None and state in ACTIVE | TERMINAL:
            add("REG-PHASE", rid, f"{state} requires a resolved {field}")
    if state == "queued" and binding is not None:
        add("REG-PHASE", rid, "Queued intake cannot reserve a worktree or lease")
    if state in ACTIVE | {"merged"} and binding is None:
        add("REG-BINDING", rid, "Implementation requires a ticket/worktree binding")
    if bool(request["terminalReceipt"]) != (state in TERMINAL):
        add("REG-PHASE", rid, "Terminal state requires its external receipt exclusively")
    if binding is None:
        if pr is not None:
            add("REG-BINDING", rid, "PR has no material implementation binding")
        return
    number = binding["ticket"].removeprefix("ticket-")
    match = re.fullmatch(r"ticket/" + number + r"-([a-z0-9]+(?:-[a-z0-9]+)*)", binding["branch"])
    expected = f".worktrees/{binding['ticket']}--{match[1]}" if match else None
    if binding["worktree"] != expected:
        add("REG-LAYOUT", rid, "Ticket, branch and Worktrees v5 path do not agree")
    lease_phase = "publication_frozen" if state == "publication" else "editing" if state == "editing" else "released"
    if binding["lease"]["phase"] != lease_phase:
        add("REG-PHASE", rid, "Lease phase disagrees with workflow; waiting releases editing reservation")
    if state in ACTIVE:
        observed = next((w for w in inventory if w["path"] == binding["worktree"]), None)
        if observed is None or observed["branch"] != binding["branch"]:
            add("REG-INVENTORY", rid, "Active worktree is missing or has another branch")
    head = binding["materialHead"]
    if head is None and pr is not None:
        add("REG-BINDING", rid, "An empty planning change cannot claim a PR")
    if head is not None and pr is None and state != "cancelled" and "ensure-pr" not in pending:
        add("REG-BINDING", rid, "Material commit requires a PR or durable publication recovery")
    if pr is not None and pr["headSha"] != head:
        add("REG-HEAD", rid, "PR observation does not bind the current material head")
    if state in {"publication", "merged"} and (head is None or pr is None):
        add("REG-PHASE", rid, "Publication requires material commit and exact-head PR")


def chain_findings(current, previous, add):
    if current["repository"] != previous["repository"]:
        add("REG-CHAIN", "$", "Previous snapshot belongs to another repository")
    if current["sequence"] != previous["sequence"] + 1 or current["previousDigest"] != digest(previous):
        add("REG-CHAIN", "$", "Snapshot sequence or previous digest does not extend the journal")
    if (current["planfile"] != previous["planfile"]
            and current["planfile"]["installationReceipt"] == previous["planfile"]["installationReceipt"]):
        add("REG-PROJECT", "$", "Changed Planfile installation needs a fresh installation receipt")
    now = {r["id"]: r for r in current["requests"]}
    for old in previous["requests"]:
        rid = old["id"]
        if rid not in now:
            add("REG-CHAIN", rid, "Request disappeared; preserve terminal history or archive externally first")
            continue
        new = now[rid]
        if new["state"] not in TRANSITIONS[old["state"]]:
            add("REG-CHAIN", rid, "Invalid workflow transition")
        for field in ("issue", "planfileTicket"):
            left, right = old[field], new[field]
            if field == "issue":
                left, right = left and left["number"], right and right["number"]
            if left is not None and left != right:
                add("REG-IDENTITY", rid, f"Existing {field} identity changed")
        if old["pr"] is not None and (new["pr"] is None or old["pr"]["number"] != new["pr"]["number"]):
            add("REG-IDENTITY", rid, "Existing PR identity changed or disappeared")
        before, after = old["binding"], new["binding"]
        if before is not None:
            if after is None or any(before[k] != after[k] for k in ("ticket", "branch", "worktree")):
                add("REG-IDENTITY", rid, "Existing implementation binding changed or disappeared")
            elif (after["lease"]["revision"] < before["lease"]["revision"]
                  or after["lease"]["fencingToken"] < before["lease"]["fencingToken"]):
                add("REG-CHAIN", rid, "Lease revision or fencing token regressed")
            elif before != after and (after["lease"]["revision"] <= before["lease"]["revision"]
                                      or after["lease"]["fencingToken"] <= before["lease"]["fencingToken"]):
                add("REG-CHAIN", rid, "Changed implementation requires a fresh fenced lease observation")
            if after and before["materialHead"] != after["materialHead"] and old["state"] != "editing":
                add("REG-HEAD", rid, "Return to editing before changing the material head")
        if old["state"] in TERMINAL and new != old:
            add("REG-CHAIN", rid, "Terminal request is immutable")
        if old["state"] == "publication" and new["state"] in {"publication", "merged"}:
            if before and after and before["materialHead"] != after["materialHead"]:
                add("REG-HEAD", rid, "Frozen publication head changed")


def inventory_chain_findings(current, previous, add):
    """Retain observations until an already bound request records retirement."""
    observed = {item["id"]: item for item in current["worktrees"]}
    requests = {request["id"]: request for request in current["requests"]}
    for old in previous["worktrees"]:
        newer = observed.get(old["id"])
        if newer is not None:
            for field in ("path", "branch"):
                if old[field] is not None and newer[field] != old[field]:
                    add("REG-IDENTITY", old["id"], f"Known checkout {field} changed or became unknown")
            continue
        if old["path"] is not None and any(item["path"] == old["path"] for item in current["worktrees"]):
            add("REG-IDENTITY", old["id"], "An observed checkout cannot be relabelled as a new inventory identity")
            continue
        retired = False
        for request in previous["requests"]:
            binding = request["binding"]
            if (binding is None or old["path"] != binding["worktree"]
                    or old["branch"] != binding["branch"]):
                continue
            retained = requests.get(request["id"])
            if (retained is not None and retained["state"] in TERMINAL
                    and retained["terminalReceipt"] is not None and retained["binding"] is not None
                    and all(retained["binding"][field] == binding[field]
                            for field in ("ticket", "branch", "worktree"))):
                retired = True
                break
        if not retired:
            add("REG-INVENTORY", old["id"],
                "Observed checkout disappeared without prior registration and a retained terminal receipt")


def validate(snapshot, previous=None):
    findings = []

    def add(code, subject, message, severity="error"):
        findings.append(dict(code=code, subject=subject, message=message, severity=severity))

    schema = load(SCHEMA_PATH)
    for label, value in (("current", snapshot), ("previous", previous)):
        if label == "previous" and value is None:
            continue
        for path in shape_errors(value, schema, schema["$defs"]):
            add("REG-SHAPE", label + path, "Input does not match the closed registration schema")
    if findings:
        return report(findings)
    repository, planfile = snapshot["repository"], snapshot["planfile"]
    if planfile["project"] != repository or not relative_path(planfile["configPath"]):
        add("REG-PROJECT", "$", "Planfile must be installed and configured for this exact repository")
    if previous is None:
        if snapshot["sequence"] != 1 or snapshot["previousDigest"] is not None:
            add("REG-CHAIN", "$", "A noninitial snapshot requires the previous snapshot")
    else:
        chain_findings(snapshot, previous, add)
        inventory_chain_findings(snapshot, previous, add)
    requests, inventory, effects = snapshot["requests"], snapshot["worktrees"], snapshot["outbox"]
    identities = {}

    def unique(namespace, value, subject):
        if value is None:
            return
        key = (namespace, value)
        if key in identities:
            add("REG-IDENTITY", subject, f"Duplicate {namespace} binding")
        identities[key] = subject

    for request in requests:
        rid = request["id"]
        unique("request", rid, rid)
        unique("planfileTicket", request["planfileTicket"], rid)
        unique("issue", request["issue"] and request["issue"]["number"], rid)
        unique("pr", request["pr"] and request["pr"]["number"], rid)
        if request["binding"]:
            for field in ("ticket", "branch", "worktree"):
                unique(field, request["binding"][field], rid)
        request_findings(request, effects, inventory, add)
    request_ids = {r["id"] for r in requests}
    bindings = {r["binding"]["worktree"] for r in requests if r["binding"]}
    for observed in inventory:
        unique("inventory-id", observed["id"], observed["id"])
        unique("inventory-path", observed["path"], observed["id"])
        if observed["path"] is not None and not relative_path(observed["path"]):
            add("REG-LAYOUT", observed["id"], "Use a repository-relative path or null for external/unknown placement")
        if observed["path"] not in bindings:
            add("REG-ORPHAN", observed["id"], "Unregistered checkout: preserve and reconcile ownership", "pending")
        elif observed["dirty"] == "unknown":
            add("REG-INVENTORY", observed["id"], "Bound checkout has unknown dirty state", "pending")
    if not snapshot["inventoryComplete"]:
        add("REG-INVENTORY", "$", "Incomplete inventory must be reconciled", "pending")
    for effect in effects:
        rid, action = effect["requestId"], effect["effect"]
        unique("effect", (rid, action), rid)
        if rid not in request_ids or effect["idempotencyKey"] != effect_key(repository, rid, action):
            add("REG-IDENTITY", rid, "Recovery effect has an unknown request or wrong idempotency key")
        add("REG-PENDING", rid, "Durable recovery remains pending: " + action, "pending")
    return report(findings)


def report(findings):
    invalid = any(f["severity"] == "error" for f in findings)
    return {"schema": "new-project.work-registration-report/v1", "readOnly": True,
            "grantsAuthority": False, "valid": not invalid, "complete": not findings,
            "status": "invalid" if invalid else "pending" if findings else "complete",
            "findings": findings}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("snapshot", type=Path)
    parser.add_argument("--previous", type=Path)
    args = parser.parse_args()
    try:
        result = validate(load(args.snapshot), load(args.previous) if args.previous else None)
    except (OSError, ValueError, RecursionError) as error:
        result = report([dict(code="REG-INPUT", subject="$", message=type(error).__name__, severity="error")])
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["complete"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
