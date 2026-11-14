# Standard Upgrade — immutable adoption and protected publication

## Overview

### Terminal owner handoff after published checkout removal (0.20.135)

The local terminal-release controller accepts the explicit current owner's
handoff when the already-merged branch and canonical checkout have both been
removed. In a nonfrozen allocation, `headSha` records the accepted base rather
than the later publication head. The controller verifies that base against
the receipt's merged source using real Git ancestry without replacement refs,
and requires the checkout path, branch and worktree registration to be absent.

Owner/session, exact lease digest and fencing, verified terminal receipt,
atomic journal and filesystem checks remain required. A remaining checkout,
registration or ref, unrelated base, Git failure or reviewed-head mismatch
is refused. This releases only that owner's terminal reservation; it grants
no fresh writer, takeover, cleanup, restoration or merge approval. Preserve
the original lease and receipts until the published controller accepts the
exact request.

This patch also contains the previously approved baseline-equivalent history
repair. Adopt the immutable published release through Goal; an independently
merged but untagged source revision is not a production release.

### Named primary aliases

Native allocation and immutable adoption plans may preserve a named primary
branch other than the target when HEAD, the local target and the observed
`origin` target identify the same commit. An alias with missing or divergent
refs, or a detached primary, is refused. These are observed local refs, not a
claim of network freshness. The primary branch, index and unrelated dirty
files remain unchanged. Native allocation rechecks the exact branch and target
observations immediately before reserving an identity; adoption verification
recomputes the package and target plan. Work-start ownership, WIP, published
source, managed metadata, fencing and independent publication still apply.


### Binding required checks on first adoption (0.20.115)

The adopter binds `.governance/required-checks.json` to the target's real
`OWNER/NAME` in the same pass whenever an `origin` remote exists. To adopt
before `git remote add`, pass `--repository OWNER/NAME`; a value that disagrees
with an existing origin is refused. Without either, the template marker
`unresolved/adopter` is kept and the adopter prints `UNBOUND ...` instead of
inventing an identity. The required-checks gate (`GOV-SYNC-001`) then names the
detected origin, or its absence, and the deterministic remedy: rerun the
managed updater at the locked `sourceRevision` with `--upgrade`. The updater
remains the only writer; do not edit the placeholder by hand.

### Fresh bootstrap with historical file tickets (0.20.89)

A repository without committed native governance can contain old file tickets.
The fresh bootstrap route accepts those carriers only when every directory
and regular file matches the exact committed tree at the receipt-bound original
HEAD. Historical status text stays unchanged; this observation grants no owner,
closure, retrospective compliance or review approval. Changed, missing,
untracked, symlinked or non-regular carriers require owner reconciliation.

Review and apply the same published immutable adopter with
`--bootstrap-native-adoption` only after preserving and reconciling any partial
installation. Reuse the existing trusted controller; do not fabricate a minimal
manifest to pass scaffold migration. Then confirm the actual primary dirty digest
through the first allocator's `--bootstrap-adoption-digest`. Allocation retains
the original legacy carriers, reserves a new identity above their high-water
IDs and writes only the new ticket metadata in its canonical worktree. Apply
the reviewed adoption in that worktree under a real fenced writer lease.

A prior allocation reservation, another registered worktree or a local ticket
branch still refuses this acknowledgement. The baseline scaffold route still
requires no historical tickets. Peer admission, intended scope, WIP, exact
installed bytes, current HEAD, clone binding, product checks and protected
independent publication remain required. Installer receipts grant no writer or
merge authority.

### Python expression secret detection (0.20.88)

The policy-as-code validator inspects Python abstract syntax trees rather than
treating unquoted dynamic expressions as raw secret literals. Python code
forwarding variables (such as token parameters), making dynamic calls
(such as node endpoint resolvers or keyring getters), and unpacking
tuples passes cleanly without false `GOV-SECRET-001` alarms. Genuine string
literals, string concatenations, malformed Python fallback, and non-Python
shell/config files continue to be strictly validated.


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
An expired/foreign lease needs a controller-observed handoff or a
`GOV-IDLE-TAKEOVER` CAS takeover, not a new local
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

From 0.20.100, local historical `ticket/*` refs may remain during the first
allocation when their exact commits are strict ancestors of the acknowledged
bootstrap HEAD. Checked Git ancestry must be readable and non-shallow. Refs at
HEAD, unintegrated history, live matching leases, unreadable lease expiry,
additional worktrees and prior native reservations still block. The guard
rechecks refs and allocation state before returning; it never deletes or moves
a ref, takes over ownership or grants editing/publication authority. These are
clone-local observations; independent clones and remote ownership still need
reconciliation through the existing external controller.

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

Acknowledgement is restricted to the first file-backed allocation from an
exact legacy scaffold. An untracked scaffold is accepted only when a checked
read of the original Git tree proves that no committed `.governance` entries
existed. An unreadable tree or remaining committed governance still refuses
admission. The published installer's exact-byte receipt is required in either
case; do not create a preliminary scaffold commit or edit that receipt.
Changed installed bytes, a stale dirty digest,
a moved HEAD, another clone, symlinked receipt/payload paths, unpublished locks,
foreign receipt paths, existing tickets/worktrees and incompatible allocator
modes are refused. Unrecorded changes overlapping the requested scope still
block admission; unrelated changes remain preserved. All WIP, branch, lease,
full product validation and independent protected publication gates remain.

### Refresh after an upgrade before the first allocation (0.20.150)

An ordinary `--upgrade` deliberately leaves the bootstrap ownership receipt
unchanged. When that upgrade completed before the first native allocation, use
the published 0.20.150-or-later adopter to review and explicitly refresh that
receipt. Pin the tool's own published checkout, and pass the exact full published
revision **already installed** in the target lock. The tool may inspect an older
published installed revision from its own immutable Git history.

```bash
python3 /path/to/published-new-project/scripts/create_adoption_lock.py \
  --target-root /path/to/target --source-revision <installed-full-SHA> \
  --refresh-bootstrap-receipt --check
python3 /path/to/published-new-project/scripts/create_adoption_lock.py \
  --target-root /path/to/target --source-revision <same-installed-full-SHA> \
  --refresh-bootstrap-receipt --upgrade
```

The first command is read-only: exit1 means a verified receipt update is needed;
exit0 means it is already current. The second command changes only the ignored
receipt. Complete any separately reviewed managed upgrade first. Refresh never
installs source, renders DSL, runs hooks or grants editing/publication authority.
Do not use the unpublished fixture exception for this operation.

Both the original and installed packages must have publication proof. The
original clone/HEAD, absence of prior reservations/extra worktrees, integrated
historical refs, original managed hashes and current installed closure are
rechecked. Target seeds and ignore rules must retain their acknowledged bytes.
A changed extendable manifest is accepted only if reversing the canonical
projection reproduces its original receipt hash and replaying it reproduces the
current bytes exactly. Added/removed managed fields or independent extensions
that cannot be proven this way refuse; route those cases to the standard owner
instead of editing the receipt or resetting the scaffold. Foreign receipt paths,
symlinks, changed observations and malformed metadata also refuse before writes.

After refresh, obtain a new work-start dirty digest and follow the normal first
allocation procedure above. The receipt is still an ownership acknowledgement;
source admission, the controller writer lease, validation and independent
protected publication remain separate requirements.

## Upgrade boundaries

### Explicit existing-file acknowledgment in native upgrade plans (0.20.136)

An older native package can leave independently maintained files at paths that
the incoming package now manages. The default allocation planner still refuses
to overwrite these files. An authorized upgrade owner can review an external
`--upgrade-ownership-plan /absolute/path/ownership.json` with
`--check --allocation-plan`. This option is for planning only; it is refused
with bootstrap, unpublished testing or installation modes.

The closed JSON object contains `schema: new-project.upgrade-ownership-plan/v1`,
`baseSha` (the current committed target HEAD), `sourceRevision` (the incoming
published standard SHA), and a nonempty `paths` array. Each entry contains
exactly `path` and `baseDigest`, the SHA-256 of its committed existing bytes.
Name every changed, existing target that becomes managed, exactly once.

Only regular files owned exclusively by the target's existing governance
workstream qualify. Their bytes and executable mode must still match the
committed base. Foreign or overlapping owners, integration requirements,
old managed targets, damaged managed closure, missing files, extra bindings
and stale hashes are refused. This acknowledges an exact data transition;
it cannot transfer a live writer's lease or repair an invalid adoption pin.

The input must be outside the target repository, at most 1 MiB, and readable
through POSIX no-follow directory descriptors. Unsupported hosts refuse this
optional mode. The resulting allocation plan embeds the existing
`delivery.standardAdoption.managedTargetTakeovers` bindings. Native allocation
recomputes the complete immutable plan under its existing lock before reserving
an identity; it needs no mutable path to the original acknowledgment file.
The generated intent describes the package and lock as component-local
governance state, so the unchanged architecture gate does not mistake this
bounded adoption for movement of product data between workstreams.

Pass that reviewed result to the published native allocator's existing
`--standard-adoption-plan` option. After allocation, acquire the actual fenced
writer and apply the complete pinned package through the ordinary adopter in
the canonical worktree. The unchanged gate verifies and consumes every exact
takeover binding against the reviewed base and installed managed payload.
Neither acknowledgment nor allocation grants execution, approval or merge
authority. Publish this source and its matching release before production use.

### Explicit missing prerequisites on first bootstrap (0.20.134)

An existing project can lack the target-owned files required before its first
native allocator is installed. An authorized bootstrap owner may supply
`--bootstrap-prerequisites-plan /absolute/external/plan.json` with either
`--bootstrap-native-adoption` or `--migrate-wellman-scaffold`. The option is
refused for ordinary upgrades; omitting it preserves the missing-file refusal.

The closed JSON object has `schema: new-project.bootstrap-prerequisites-plan/v1`,
the current committed `baseSha`, and a nonempty `files` array. Each entry has
exactly `path`, literal UTF-8 `content`, and its lowercase `sha256`. At most four
entries of 64 KiB each may name missing required target-owned `VERSION`,
`CHANGELOG.md`, `TODO.md`, or `project/TICKETS.md`. VERSION must contain the
explicit project SemVer. These are project values, never the standard version.

Review with `--check` before applying the same plan with `--upgrade`. Existing
files, deleted committed files, duplicate keys/paths, digest or HEAD mismatches,
symlinked inputs/parents and arbitrary source paths found during validation
are refused before seed writes. All destination leaves are checked again
through pinned directories before any seed or missing parent is created.

Exclusive creation never overwrites a file appearing afterward. Creation of
multiple files is not an atomic transaction: a later concurrent conflict, I/O
failure or interruption can leave earlier seeds, partially written leaves or
a newly created `project/` directory. A caught creation error identifies the
created paths for owner reconciliation; it stops before managed installation
and before a bootstrap receipt is written. Preserve and inspect the target
before retrying. Automatic pathname rollback could delete another owner's
concurrent replacement, so it must not remove these files. A missing bootstrap
receipt does not prove that the target is unchanged.

This opt-in mode requires POSIX no-follow directory-descriptor operations;
hosts without these primitives refuse it before effects. Actual plan reads
are bounded to 1 MiB from a verified regular descriptor. Seed creation pins
the original directories, refuses symlink replacements, and checks their
bindings before managed installation continues.

The existing bootstrap receipt binds the installed seed bytes. It grants no
writer or publication authority. Confirm its actual dirty digest at first
allocation, acquire a real fenced writer, apply the reviewed package in the
canonical worktree, then validate and publish independently. Foreign work and
every existing allocation/ownership check remain in force.

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

Since 0.20.107, `packages/wellman` builds distribution `wellmanifest-governance`,
module `wellmanifest_governance_runtime` and command `wellman-governance`. Its installed
wheel owns neither the `wellman` namespace nor that command. The full runtime in
`wellmanifest/wellman` retains `wellman` and owns `wellman run`. Both can coexist;
resolve their actual immutable sources and installed entry points independently.

Protected CI continues to install only its approved source revision in an
isolated environment. The delivered gate recognizes the new governance entry
point or the legacy `wellman.check:main` entry point from an older trusted pin.
It refuses the unrelated catalogue entry point and missing runtimes; it never
falls back to candidate Python modules or another executable on PATH. Existing
pins and published legacy wheels are unchanged. Publishing the newly named
package needs its own matching trusted publisher; this source change performs
no PyPI publication or fleet upgrade.

For development execution, use the approved full runtime's `wellman run` or an
enrolled executor SDK. Verify cwd, candidate source, associated interpreter,
checkout-owned scratch and the real result separately. Static checker JSON
reports `runtime_enforcement=not_checked`; even PASS grants no execution or
publication authority. Immutable tooling and protected CI remain explicit roles,
not arbitrary path-prefix exceptions. Missing executor enrollment must be repaired
before claiming mediated execution.
Installing a package or running legacy `wellman adopt baseline` does not install
or update the complete native governance contract. Native adoption/upgrades use
the pinned `create_adoption_lock.py` path above and retain protected delivery.

## Policy DSL runtime in adopters

Since 0.20.108 the package manifest installs the reviewed Policy DSL checker
and its lock at `.governance/policy_dsl_check.py` and
`.governance/policy-dsl.lock.json`, the targets the lock already declared. The
gate validates `CONTRIBUTING.md` only when it contains a ` ```dsl ` fence; an
existing contributor guide without one is not policy and is not parsed. A
`dsl` fence with a missing or modified runtime still fails `GOV-POLICY-DSL-001`.
Upgrading to 0.20.108 adds both managed files to the adoption lock.

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
