# Standard Upgrade — immutable adoption and protected publication

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

## Migrating an exact minimal Wellman scaffold

Some repositories were registered by the separate Wellman catalogue CLI with
only this manifest:

```json
{"schema":"wellmanifest.manifest/v1","standard":{"id":"profile:baseline","version":"0.20.37"}}
```

This is requirement registration, not an installed native governance contract.
The ordinary immutable adopter refuses it because it does not extend the full
managed manifest. For an authorized bootstrap, use the published adopter's
explicit migration option introduced in standard 0.20.81:

```bash
python3 /path/to/pinned/new-project/scripts/create_adoption_lock.py \
  --target-root /path/to/repository --source-revision <published-full-commit-sha> \
  --migrate-wellman-scaffold --check

# Apply the same reviewed scope through the authorized bootstrap owner.
python3 /path/to/pinned/new-project/scripts/create_adoption_lock.py \
  --target-root /path/to/repository --source-revision <published-full-commit-sha> \
  --migrate-wellman-scaffold --upgrade
```

The option accepts exactly the two-key baseline scaffold with a valid version,
without a native lock, manifest base or package map. Additional fields, native
schemas, duplicate keys and symlinked target paths are refused before writes.
Existing target prerequisites remain required; the review is read-only and
reports drift. The full manifest and managed files come from the same verified
annotated tag and final canonical GitHub Release. Ordinary native upgrade and
extension rules remain unchanged. Never use `--allow-unpublished-for-testing`
on a production repository.

Reconcile the current owner, pending changes, exact bootstrap scope and existing
session authorization before applying. Preserve the original committed history
or an authorized external snapshot. This option installs files only: it grants
no repository admission, lease, trusted approval or merge authority. A usable
native allocation/canonical worktree, full product validation and the declared
independent protected publisher are still required for subsequent delivery.
Do not replace customized or partial native governance with a scaffold. Restore
it through its own pinned adopter and controller-owned recovery instead.

### First allocation after scaffold migration

An exact scaffold migration on an existing Git repository leaves owned installed
files pending in the primary checkout. The installer records their exact bytes
in ignored `.subactor/receipts/bootstrap-adoption.json`, bound to the original
HEAD and clone. This receipt grants neither writer nor publication authority.

Read the work-start report and reconcile the owner of the recorded adoption
files before passing its primary `dirtyDigest` explicitly:

```bash
python3 .governance/work_start_check.py --root . --workstream governance \
  --path '.governance/**' --allocation-check
./project/new-ticket.sh --title "Adopt native governance" --agent codex \
  --workstream governance --path '.governance/**' \
  --bootstrap-adoption-digest <exact-primary-dirtyDigest>
```

The declared `--path` arguments must cover the intended subsequent adoption
work and be owned by the selected workstream. Allocation writes only ticket
metadata in the canonical relative worktree at the original committed base.
It does not copy governance or product source into that checkout. Complete the
bounded intent, acquire the real controller writer lease, then apply the same
pinned adopter there. Preserve the primary bootstrap and unrelated changes
until their owner reconciles them; allocation never cleans or commits primary.

Acknowledgement is restricted to the first file-backed allocation from a
committed exact legacy scaffold. Changed installed bytes, a stale dirty digest,
a moved HEAD, another clone, symlinked receipt/payload paths, unpublished locks,
foreign receipt paths, existing tickets/worktrees and incompatible allocator
modes are refused. Unrecorded changes overlapping the requested scope still
block admission; unrelated changes remain preserved. All WIP, branch, lease,
full product validation and independent protected publication gates remain.

## Upgrade boundaries

| Boundary | Actual responsibility |
| --- | --- |
| Local hook | Validate the installed immutable pin and bounded ticket scope; it does not fetch or update governance. |
| Explicit adopter/updater | Verify the published revision, review drift, preserve target extensions and apply an authorized upgrade. |
| CI and protected publisher | Validate the exact base/head and required checks, then obtain independent trusted approval before merge. |

`create_adoption_lock.py --check` reports missing files, changed digests,
executable modes and target prerequisites without writing. `--upgrade` replaces
reviewed managed files and performs the supported three-way merge of the
managed manifest base and target-owned extensions. A missing/invalid base or
conflicting extension is a recovery condition, not permission to overwrite it.
The resulting lock binds the immutable source revision and managed digests.

The optional `propagate-standard.yml` workflow can propose upgrades when its
repository configuration enables it. A proposal, green CI or a version string
alone proves neither fleet adoption nor merge. Observe each repository's actual
PR, independent approval and terminal receipt. Verify publication and deployed
runtime separately; no universal 24-hour rollout is guaranteed by the standard.

## Runtime package and CLI identity

The governance runtime in `packages/wellman` and the separately installed
Wellman catalogue CLI have distinct responsibilities. Resolve the actual
executable, source revision and adoption lock before selecting a command.
Installing a package or running legacy `wellman adopt baseline` does not install
or update the complete native governance contract. Native adoption/upgrades use
the pinned `create_adoption_lock.py` path above and retain protected delivery.
