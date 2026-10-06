# Standard Upgrade — immutable adoption and protected publication

## Overview

### Reusable workflow host audit (0.20.87)

The agent-host audit uses the adjacent managed required-checks validator for
direct jobs and pinned reusable callers. A caller check such as `ci / test`
must resolve through the same immutable callee bytes and SHA-256 lock as the
required-checks gate. Missing sources, mutable refs, digest mismatches and
unsupported local reusable calls produce a bounded `GOV-AGENT-HOST-004`
finding. Neither audit downloads or executes workflow input. Adopt the complete
published package so managed and bundled readers stay together.

After adoption, run `python3 .governance/agent_host_check.py --root . --format json`
and `python3 .governance/check_required_checks.py --root .` on the same checkout.
Both checks must resolve the pinned caller and callee; an unresolved-contract
finding requires correcting the source/lock or publishing the missing package,
while preserving the required job names.


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

### First adoption without a Wellman scaffold (0.20.84)

For a committed repository with no governance manifest, lock, base or package
map, explicitly review and apply the pinned adopter's
`--bootstrap-native-adoption` mode. This records the same exact installer-byte
receipt as scaffold migration, with `bootstrapKind: fresh`. It refuses existing
governance, including governance deleted from the working tree but present at
the original HEAD. An unborn or non-Git directory cannot use this mode.

Use the observed `dirtyDigest` with the existing managed allocator's
`--bootstrap-adoption-digest` after reconciling ownership. Native allocation
still writes only ticket metadata at the committed base; complete its intent,
acquire the actual fenced writer lease, and apply the ordinary pinned adopter
in that canonical worktree. Preserve primary and foreign bytes. The receipt
does not grant writer, review or publication authority. All first-allocation,
WIP, clone, payload, published-pin and independent delivery checks still apply.

Do not create a synthetic legacy scaffold or a carrier-only baseline commit to
access this route. Customized, partial and existing native governance must use
their own recovery or upgrade process. Source publication and the published
release precede production adoption of this new mode.

### Planning immutable reusable CI before first allocation (0.20.86)

An existing committed caller using a mutable ref cannot pass the offline
required-checks gate. When it also lacks native governance, changing that
caller must wait for its first native ticket. Fresh bootstrap accepts an
optional external `--bootstrap-reusable-plan /absolute/path/plan.json` to
describe the future check contract without changing target CI:

```json
{
  "schema": "new-project.bootstrap-reusable-plan/v1",
  "baseSha": "<current committed target HEAD: 40 lowercase hex characters>",
  "callerFile": ".github/workflows/ci.yml",
  "callerSha256": "<SHA256 of exact committed caller bytes>",
  "originalUses": "owner/repo/.github/workflows/test.yml@main",
  "uses": "owner/repo/.github/workflows/test.yml@<full immutable commit SHA>",
  "sourceFile": ".github/reusable-workflows/test.yml",
  "sourceSha256": "<SHA256 of exact published callee bytes>",
  "sourceBase64": "<base64 of those exact UTF-8 callee bytes>"
}
```

Acquire and independently review the callee from the named published revision.
Hashes bind supplied bytes; they do not authenticate provenance or approve its
execution. The plan has exactly these nine string fields and must be a regular
file outside the target repository. The caller must still match committed
HEAD and its digest, with one literal unquoted `uses` line. The plan pins the
same workflow to a full SHA. Existing reusable source contracts, symlinks,
unsupported jobs, stale input and unresolved additional callers are refused.
No callee is fetched or executed.

Use this option only together with `--bootstrap-native-adoption`. The adopter
computes future names in a temporary offline mirror, installs only managed
bootstrap files, and declares the three exact planned CI paths as owned by
the target's governance workstream. It never grants ownership of `.github/**`.
Request those exact caller, source and lock paths, plus the required managed
adoption scope, when allocating with `--bootstrap-adoption-digest`. Record the
bounded native intent and acquire the actual writer lease before implementing
the pin, source and `.github/reusable-workflows.lock.json` in that worktree.

The primary caller remains unchanged. Its required-checks gate intentionally
fails until real CI implements the future contract. Run ordinary pinned
adoption without a plan in the allocated worktree, validate the resulting
actual checks and obtain independent protected publication. A bootstrap plan,
installed receipt or planned check name grants no writer, review or merge
authority. Publish this standard and its release before production adoption.

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

## Offline reusable CI contracts

A reusable CI caller publishes `<caller display name> / <callee display name>`,
not the caller job key alone. Native adoption and the required-checks gate
resolve literal leaf jobs using an optional target-owned
`.github/reusable-workflows.lock.json`:

```json
{
  "schema": "new-project.reusable-workflows/v1",
  "workflows": [{
    "uses": "owner/repo/.github/workflows/ci.yml@<full 40-character commit SHA>",
    "sourceFile": ".github/reusable-workflows/ci.yml",
    "sourceSha256": "<SHA256 of the exact workflow bytes>"
  }]
}
```

Acquire the file from that published immutable revision before recording its
hash. Keep the exact bytes in the named file and pin the caller's `uses` to
that same revision. Review the source provenance and execution semantics as
part of the target's ordinary native ticket and protected PR; these
repository-owned bindings describe checks and do not grant execution or
merge authority. Updating the ref requires a matching reviewed source and
hash update. The resolver neither fetches nor executes external code.

The managed schema is `.governance/reusable-workflows.schema.json`. The first
bootstrap reads the lock and source from the target without changing them;
the ordinary adopted generator and checker use the same offline resolver.
Target-owned required-check declarations remain extensions. Missing bindings,
mutable refs and changed source hashes cannot resolve a caller. Symlinks,
traversal, duplicate bindings, unknown fields, nested calls, matrices,
conditional jobs and expression-based names fail closed. This initial profile
supports literal block mappings only; unsupported workflows need a separately
reviewed contract extension, never a guessed green context. Keep all required
checks and independent publication while arranging that extension.
