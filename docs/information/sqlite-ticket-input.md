---
{
  "schema": "wellmanifest.docs/document/v1",
  "id": "sqlite-ticket-input",
  "kind": "information",
  "version": 3,
  "title": "SQLite ticket input for governance validation",
  "status": "proposed",
  "owner": "wellmanifest/new-project",
  "created": "2026-09-08",
  "updated": "2026-09-08",
  "review_after": "2026-09-22",
  "source_revision": "84061f1e1368509c72db7a45150628ebffb07b2d",
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
0.20.17 introduced read-only inputs at the source baseline named above.
0.20.18 adds optional allocation and local consumers; Registry owns persistence.

<!-- docs:section scope -->
## Scope

File input remains the default. Explicit flags or clone-local configuration opt into the Registry
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

### Allocate without ticket files (0.20.18)

Install the reviewed Registry writer from commit
`408e90bb0a0554499fa4560cff9e2e0e83c2cd8d` (Registry PR 49) in a private release
directory. This versioned integration verifies all three transitive modules:
`storage-common.mjs`, `ticket-store.mjs` and `ticket-store-cli.mjs`. Obtain the
aggregate SHA-256 independently from that reviewed package: canonical compact
JSON mapping sorted module names to their SHA-256, then SHA-256 of that JSON.
The bridge's `digest` command computes a comparison value, not approval.

```sh
git config --local new-project.ticketStorage sqlite
git config --local new-project.ticketStoreRoot /private/releases/REGISTRY_SHA
git config --local new-project.ticketStoreSha256 INDEPENDENT_PACKAGE_SHA256
./project/new-ticket.sh --workstream WORKSTREAM --title 'Implement the bounded change'
python3 .governance/ticket_input.py read --root . --ticket ticket-NNN --file intent.json
```

`--storage`, `--ticket-store-root` and `--ticket-store-sha256` are explicit
allocation overrides. Persistent local configuration selects all local readers.
The existing clone-wide allocation lock and private high-water reservation remain
necessary for compatibility with older allocators. Database IDs also participate
in the next-ID calculation. The writer verifies its digest before reservation,
initializes only ignored storage and atomically persists the reserved ticket.
No ticket directory or index is written. Failed persistence can leave a reserved
number unused; it never permits reuse of that number.

The initial intent authorizes no implementation path. Append the complete bounded
intent through `subactor-ticket update --repository . --ticket ticket-NNN
--file intent.json --expected-revision N` with content on stdin before editing
source. Local pre-commit, governance, overlap and continuity readers use the
shared primary database; a linked worktree does not get a second ticket store.

`tests/sqlite-allocation.test.py` exercises the real immutable Registry writer,
allocation, Git commits, shared worktree storage and rejected runtime tampering.
Registry is private: these four interoperability tests require an explicit
`TEST_REGISTRY_TICKET_RUNTIME` directory and verify the immutable source hashes
before execution. They report a skip when absent; hosted CI does not implicitly
fetch private source. Two runtime-boundary tests and the existing eight SQLite
reader tests run without this package. A local interop receipt does not establish
that a protected executor has installed or run the private integration.
The existing file-mode regression remains required.

<!-- docs:section limitations -->
## Limits

This package does not install a trusted snapshot producer or activate fleet CI.
The Registry bridge additionally requires Node, the SQLite CLI and the reviewed writer package.
Protected intent chronology moves to the external receipt producer; a local
database or SHA-256 cannot prove that chronology or authorize execution/merge.
The rule traceability map records this producer dependency explicitly.

Existing scope, workflow, base, dependency, workstream, material-delivery and
approval checks remain active. File mode retains its Git intent-history check.
SQLite state is not silently synchronized back to legacy ticket prose.

<!-- docs:section next_actions -->
## Adoption and rollback

Adopt the immutable package through Goal, then explicitly enable local SQLite
configuration with an independently verified Registry package pin. Bind CI through an independently controlled
snapshot producer and verify a real PR containing code without ticket files.
Only after that canary should legacy carrier requirements be retired for a
repository. Rollback selects the former input explicitly and preserves all
database-only revisions; stale Git files are not a synchronized recovery copy.
