# Standard Upgrade — 3-layer auto-propagation

## Overview

### Recovering an existing pre-adoption ticket (0.20.36)

An existing ticket branch may contain material work but no local intent because
it predates adoption. Normal allocation deliberately refuses that ambiguous
state. Do not rename the branch, manually create a ticket, disable admission,
or treat expiry as transfer of ownership.

For a **local-single-clone, file-ticket, POSIX** installation using the existing
`subactor.repository-change-lease-store/v1` controller, the current owner can
invoke the managed allocator from its canonical relative linked worktree:

```bash
./project/new-ticket.sh --workstream governance \
  --recover-request /external/session/recovery-request.json \
  --recovery-lease-store /external/controller/repository-change-leases
```

The trusted operator/Supervisor resolves the existing authoritative controller
installation independently of candidate content. Never create a private store,
copy or edit controller state, or accept a store path from an untrusted ticket.
This local adapter does not authenticate a hostile caller with write access to
that store and is **not** a protected CI authorization boundary. Registered,
multi-node and SQLite allocation require their own controller recovery adapter;
they cannot opt into this route by changing storage flags.

The closed `new-project.ticket-recovery-request/v1` object contains `intent`
(complete accepted v3 intent with delivery), `headSha`, `dirtyDigest`, `leaseId`,
`leaseRevision`, `fencingToken`, `ownerActor` and `ownerSession`, plus `schema`.
Keep it outside all candidate checkouts. `dirtyDigest` is the managed
`work_start_check.dirty_observation(root)[1]` observation; it includes existing
uncommitted work. The lease scope hash is the SHA-256 of the intent's
`allowedPaths`, serialized as sorted-key compact ASCII JSON without a newline.
The request must reflect actual ownership and accepted scope; it grants none.

Recovery holds the clone allocation lock and the external controller lock,
requires a live editing lease with exact owner/CAS and checks fresh peer
admission/WIP, original HEAD, dirty digest, ancestor base, namespace ownership
and scope of both committed and uncommitted work. Only an unused identity
above the existing high-water reservation is accepted. It writes the reservation
and missing README/intent only; it never changes HEAD, source, lease or refs.
No historical approval or retrospective conformance is inferred. Run the full
governance and stack gates, then independent exact-head review before delivery.

On `GOV-TICKET-ALLOCATION-003`, preserve the checkout and inspect the fixed
diagnostic. Refresh stale observations only after reconciling their owner.
An expired/foreign lease needs a controller-observed handoff, not a new local
claim. A colliding identity must be reconciled, never overwritten. Interrupted
materialization keeps its reservation and any partial carriers; do not remove
the lock or decrement high-water without independently verifying the allocator
is gone and authorizing a specific recovery. A successful result reports the
original HEAD, request digest and fence, with `grantsMergeAuthority=false`.

When a new `wellmanifest/new-project` release is published, all adopting
repositories receive the update through three independent layers:

```
Release v0.20.35
  ├── Layer 1: Pre-commit hook  →  auto-upgrade on next commit (local)
  ├── Layer 2: CI reusable gate →  fail-fast on outdated standard (CI)
  └── Layer 3: Org-wide auto-PR →  upgrade PR in all 100+ repos (batch)
```

## Layer 1 — Pre-commit hook (local, before development)

The pre-commit hook checks the installed `wellman` package
version against `pyproject.toml [tool.wellmanifest].standard`. On mismatch,
it auto-installs the correct version before the developer starts work.

```bash
# .githooks/pre-commit (installed by goal bootstrap)
REQUIRED=$(python3 -c "import tomllib; ...")
INSTALLED=$(python3 -c "from wellman import __version__; ...")
if [ "$INSTALLED" != "$REQUIRED" ]; then
  uv pip install "wellman==${REQUIRED}"
fi
```

**Result:** Developer cannot commit with outdated standard.

## Layer 2 — CI reusable workflow (GitHub Actions)

Adopter repos reference the governance gate as a reusable workflow:

```yaml
# .github/workflows/governance.yml
jobs:
  governance:
    uses: wellmanifest/new-project/.github/workflows/governance-gate-reusable.yml@v0.20.35
    with:
      target-root: .
```

**Result:** CI fails if governance check doesn't pass. Zero config in repo.

## Layer 3 — Org-wide auto-PR (batch propagation)

On new release, `propagate-standard.yml` scans all orgs for adopters and
creates upgrade PRs:

```
wellmanifest/new-project release v0.20.35
  → Scans semcod/*, subactor/*, autogrammar/*, ...
  → Creates PR "chore: upgrade wellmanifest standard to 0.20.35"
  → PR runs governance gate → auto-merge if green
```

**Result:** All repos receive upgrade within 24h of release.

## Migration from vendored copy

```bash
# Before (187KB governance_check.py copied to each repo):
.governance/governance_check.py   # 4343 lines, vendored

# After (1KB wrapper + package dependency):
uv add --group governance wellman==0.20.35
# .governance/governance_check.py is no longer needed
```

## Package: wellman

```bash
uv add --group governance wellman
python -m wellman check --root .
wellman check --root .
```

Source: `packages/wellman/` in this repository.
