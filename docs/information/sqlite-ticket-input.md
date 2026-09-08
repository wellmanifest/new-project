---
{
  "schema": "wellmanifest.docs/document/v1",
  "id": "sqlite-ticket-input",
  "kind": "information",
  "version": 2,
  "title": "SQLite ticket input for governance validation",
  "status": "proposed",
  "owner": "wellmanifest/new-project",
  "created": "2026-09-08",
  "updated": "2026-09-08",
  "review_after": "2026-09-22",
  "source_revision": "ed1c3ea778989e911ff4f400d90f8064b8f95dfe",
  "affected_repositories": ["wellmanifest/new-project"],
  "evidence": ["https://github.com/wellmanifest/new-project/pull/310", "https://github.com/subactor/registry/commit/510ce294ed1e7ddcf1b877a76f72f4a41dfbebea", "tests/ticket-input.test.py"]
}
---

# SQLite ticket input for governance validation

<!-- docs:section purpose -->
## Purpose

Validate ticket intent, workflow state, ownership and scope without requiring a
ticket directory in the implementation commit. Operational updates can remain
in the ignored `project.sqlite` instead of producing Git changes. Version
0.20.17 introduces this input contract at the exact source revision named
above; Registry owns persistence.

<!-- docs:section scope -->
## Scope

File input remains the default. These explicit flags opt into the Registry
`registry.ticket-content/v1` contract published by Registry PR 48. The standard
distributes a read-only Python adapter with no additional runtime dependency.

<!-- docs:section evidence -->
## Evidence

`tests/ticket-input.test.py` runs the complete governance CLI against actual
Git repositories and SQLite databases with no `project/ticket-001` directory.
It verifies index/status invariance and rejects scope escapes, missing content,
corrupted data, duplicate tickets, wrong subject/digest, symlinks and
candidate-local CI input. It also proves that a valid snapshot does not satisfy
independent approval enforcement. The suite runs from the existing governance
regression entry point.

<!-- docs:section content -->
## Local and protected inputs

Local verification uses the initialized database in the registered primary
checkout, including when invoked from a linked worktree:

```sh
./project/governance-check.sh --base BASE_SHA --head HEAD --ticket-database /path/to/primary/project.sqlite
```

The adapter verifies the SQLite application/schema version, owner-only file
permissions, untracked/ignored database and journal paths, content digests,
closed document shape and ticket IDs. It creates no database, journal, ticket
file or Python bytecode. Legacy ticket files are not read when an explicit
database or snapshot input is selected.

Protected validation (`--actor ci` or `--enforce-approval`) rejects direct
SQLite input. Its trusted producer exports a complete snapshot outside Git:

```sh
python3 .governance/ticket_input.py export --root /path/to/repo --database /path/to/primary/project.sqlite --repository org/repo --base BASE_SHA --head HEAD_SHA
```

The protected launcher supplies the independently acquired file, its SHA-256,
the expected repository and exact Git base/head:

```sh
./project/governance-check.sh --actor ci --expected-repository org/repo --base BASE_SHA --head HEAD_SHA --ticket-snapshot /protected/input.json --ticket-snapshot-sha256 SNAPSHOT_SHA256
```

The `new-project.ticket-input/v1` snapshot retains each complete document string,
its digest and revision, plus repository/base/head bindings. A candidate cannot
substitute another ticket or silently change its scope without changing the
pinned digest. Local files inside any Git checkout are rejected as snapshot
sources. Snapshot hashes provide consistency; the protected launcher owns
independent acquisition and authentication.

<!-- docs:section limitations -->
## Limits

This reader does not allocate ticket IDs, update SQLite, install a trusted
snapshot producer, change existing pre-commit hooks or activate fleet CI.
Protected intent chronology moves to the external receipt producer; a local
database or SHA-256 cannot prove that chronology or authorize execution/merge.
The rule traceability map records this producer dependency explicitly.

Existing scope, workflow, base, dependency, workstream, material-delivery and
approval checks remain active. File mode retains its Git intent-history check.
SQLite state is not silently synchronized back to legacy ticket prose.

<!-- docs:section next_actions -->
## Adoption and rollback

Adopt the immutable package through Goal, then bind the managed allocator and
local hook to Registry storage. Bind CI through an independently controlled
snapshot producer and verify a real PR containing code without ticket files.
Only after that canary should legacy carrier requirements be retired for a
repository. Rollback selects the former input explicitly and preserves all
database-only revisions; stale Git files are not a synchronized recovery copy.
