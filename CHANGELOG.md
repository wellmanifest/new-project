# CHANGELOG

## 0.20.128

- Revalidate SQLite and external ticket snapshots instead of reusing a Git-only
  preflight cache key; retain WAL visibility and current snapshot digest checks
  [ticket-393].
- Disable cache reuse for unbound comparison bases and unknown storage modes,
  while retaining explicit-base file-ticket cache hits and existing CI gates
  [ticket-393].

## 0.20.127

- Reject duplicate or unreadable Git snapshot inventory paths with the existing
  typed diagnostic, preserving source/runtime parity [ticket-397].
- Validate the complete host bootstrap file plan before writing: canonical
  contained paths, regular sources, distinct targets and matching contracts.
  Refuse symlink/reparse paths and replace files atomically while retaining
  hardlink referents and read-only checks [ticket-397].

## 0.20.126

- Derive PR checks only from the literal pull_request trigger and its own
  activity types; preserve sibling event isolation and refuse unsupported or
  ambiguous trigger declarations before writing [ticket-396].
- Preserve distinct SSH users and non-default repository ports while retaining
  conventional Git SSH aliases; reject ambiguous or password-bearing origins
  without exposing credentials [ticket-396].

## 0.20.125

- Fence integrated-worktree branch cleanup with an atomic transaction binding
  the observed branch and target tips and verify direct reference types under
  those locks; retain checked-out, changed or refused refs without
  forced deletion [ticket-395].
- Preserve target checkouts, ignored data and unrelated missing registrations;
  remove only the exact integrated checkout through Git.

## 0.20.124

- Report deterministic packaging findings for malformed nested Python tool
  metadata instead of raising AttributeError; preserve valid lifecycle binding
  and the byte-identical bundled checker [ticket-394].
- Use the installed adopter checker path in host and packaging error guides,
  with the source-hub command stated separately [ticket-394].

## 0.20.123

- Keep governance Git fixtures in a private platform temporary root; preserve
  Git discovery ceilings and every integration assertion, and clean the entire
  owned fixture root through one exit handler [ticket-392].

## 0.20.122

- Run fresh first-allocation authority tests directly in the protected adoption job. Preserve all cases while removing their duplicate nested whole-suite invocation from ordinary discovery.

- Adopt independently published Worktrees 0.5.4 with native Windows inventory paths, complete Git observation arguments and preserved stale/merged recovery diagnostics. Bind both artifacts to the approved source revision and test the adopted CLI on POSIX and Windows paths.

- Preserve quotes, backslashes and newlines in advisory model text through canonical decision DSL serialization and reject malformed JSON string escapes. Plain legacy advisory lines retain their representation.
- Check bare and fenced decision records together in document order, so mixing Markdown formats cannot hide mutation or removal of an earlier append-only record.

## 0.20.121

- Preserve head branches when an unmerged pull request is closed. The distributed close-only workflow now emits a read-only notice; branch discard requires separate reconciliation and explicit owner authority. GitHub handles branch deletion after merge through the repository setting.
- Execute the workflow script in regression tests across ticket, long-lived, default and fork branch events, asserting that no branch-write API is called.

## 0.20.120

- Idle takeover policy, slice 1 of 3 (tickets 374–376): the manifest schema and validator accept the optional, closed `coordination.idleTakeover` policy (`enabled`, `idleMinutes` 5–240, `leaseMinutes` 15–480 and greater than `idleMinutes`). The default and hub manifests enable it at 15 minutes with a 120-minute lease; the policy has no effect until the `idle_takeover.py` runtime ships. The hub allows two active governance tickets.
- `change_lease_check.py` exports the wellmanifest/worktrees v5 roots (`WORKTREES_ROOT`, `LEASE_ROOT`) and `MAX_LEASE_BYTES`; the writer check reads them instead of repeating the literals.

## 0.20.119

- The allocator indexes the ticket it has just created (issue #516): `new-ticket.sh` runs `project/readme.sh` with `T2C_TICKET_INDEX_OWN=project/ticket-NNN`, so a ticket's own PR carries exactly its own `project/TICKETS.md` row instead of the next ticket's PR adding it. Other untracked tickets in the checkout stay out of the index, and a malformed own-ticket value is refused.

## 0.20.118

- `ticket_activity` records a terminal receipt for a PR squash-merged or rebased onto a newer base whose generated `project/TICKETS.md` hunk vanished because a sibling ticket already added the same rows (issue #524). Patch identity for squash and rebase verification now excludes that index, which `project/readme.sh` regenerates, while every authored path must still match exactly. Such tickets no longer stay `IN_PROGRESS` and hold their scope and WIP slot forever.

## 0.20.117

- The default manifest assigns project CI workflows (`.github/workflows/**`) to the `infrastructure` workstream (issue #521), so an adopter can allocate a ticket that changes its own `ci.yml`. The governance workflows (`new-project-governance.yml`, `new-project-branch-hygiene.yml`) stay owned by `governance`; the hub manifest is unchanged.

## 0.20.116

- A bare `./project/governance-check.sh` (and `.bat`) on a `ticket/NNN-*` branch now validates the ticket's committed range (issue #520): the wrappers pass `--infer-ticket-base`, which binds `--base` to `git merge-base HEAD origin/<target>` (target from `delivery.targetBranches`, or the ticket's own `delivery.targetBranch` when several are allowed). A missing or unrelated `origin/<target>` is `GOV-BASE-001` instead of an empty `GOV-PASS`. Explicit `--base` or `--changed-file` wins, and other branches and detached CI checkouts are unchanged.

## 0.20.115

- Adoption binds `.governance/required-checks.json` to the real repository on the first pass (issue #518): `create_adoption_lock.py --repository OWNER/NAME` names the repository before `git remote add` (refused when it disagrees with an existing origin), and a run without any identity prints `UNBOUND ...` instead of silently keeping `unresolved/adopter`. The required-checks gate (`GOV-SYNC-001`) now names the detected origin, or its absence, and the deterministic remedy: rerun the managed updater at the locked `sourceRevision` with `--upgrade`. The updater stays the only writer.

## 0.20.114

- GOV-INTENT-002 delivery errors now name the required location of a misplaced but recognized field (issue #517): `delivery.interfaceChanges` reports `move interfaceChanges to delivery.architecture.interfaceChanges`, and architecture, budget and top-level delivery fields placed at the wrong level name their path the same way. The field is still rejected (no synonym); unknown fields get no location hint. Runbook `GOV-INTENT` documents the placement.

## 0.20.113

- `work_start_check.py --controller-store DIR --controller-repository OWNER/NAME` adds a read-only `editingResource` observation of the controller's exclusive editing resource (issue #510): `AVAILABLE`, `HELD_BY_TICKET`, `HELD_BY_OTHER`, `HELD_EXPIRED` or `UNAVAILABLE` with a reason, a safe holder reference, the state digest and a deterministic `nextAction`. Disjoint paths no longer look like an available editing slot, an expired holder is reported as still blocking, and an unreadable or changing controller is never reported as available. The observation grants nothing and writes nothing; the report schema declares it.

## 0.20.112

- `new-ticket.sh --restore-request FILE --recovery-lease-store DIR` restores an already reserved ticket whose canonical checkout, branch or uncommitted metadata was lost (issue #509). It never allocates a number or lowers the high-water mark. The request binds the reservation record in `.subactor/leases/`, the exact branch head, a SHA-256-pinned metadata snapshot (`README.md` and `intent.json` only) and the live controller lease CAS. Restoration rejects collisions, foreign or expired owners, symlinks, tampered snapshots and existing different metadata, resumes an interrupted run, and grants no editing or merge authority. Packaged as `.governance/ticket_restoration.py`; diagnostics stay `GOV-TICKET-ALLOCATION-003`.

## 0.20.111

- New warning `GOV-HOST-MERGE-001` (runbook `error/GOV-HOST-MERGE.md`): the gate flags `AGENTS.md`, `CLAUDE.md` or `GEMINI.md` whose `wellmanifest:autonomous-merge` block still carries the superseded merge-on-green authority (`wellmanifest/merge@ticket-008`). It is a warning, so it does not fail adopters; it makes the remaining host-file rollout of issue #507 visible per repository. Reconcile with `scripts/host_publication_policy.py` in an owned ticket.

## 0.20.110

- `scripts/host_publication_policy.py` reconciles host instruction files that carry the stale `wellmanifest:autonomous-merge` block without a `wellmanifest:nolimits` block, which is how the fleet's host files look (issue #507). Previously every such file was refused with `HOST_NOLIMITS_MARKERS_AMBIGUOUS`, so the stale merge-on-green authority could not be replaced. A partial or duplicated `nolimits` marker still fails closed, and a stray `LIM-MERGE-003` remedy outside a `nolimits` block is refused with `HOST_MERGE_REMEDY_OUTSIDE_NOLIMITS`.

## 0.20.108

- Adoption now installs the pinned Policy DSL runtime (`.governance/policy_dsl_check.py`, `.governance/policy-dsl.lock.json`) declared by its lock, and `GOV-POLICY-DSL-001` validates `CONTRIBUTING.md` only when it contains a `dsl` fence. An adopter's existing contributor guide no longer fails the gate; a `dsl` fence with a missing or modified runtime still fails closed (issue #479).

## 0.20.107

- Distribute the static checker as `wellmanifest-governance` / `wellman-governance` without owning the full Wellman CLI namespace. Isolated CI recognizes the new runtime and independently pinned legacy checker entry points, refusing the unrelated catalogue CLI. Static reports explicitly state that runtime enforcement was not checked; managed agent instructions require enrolled project-bound execution and declared tooling roles. Existing protected pins remain unchanged.

## 0.20.106

- New managed hook `.githooks/pre-push` refuses pushes that update a declared target branch (`delivery.targetBranches`, default `main`), including `HEAD:main` refspecs and deletions, with `GOV-PUSH-001`. Delivery reaches the target branch through a reviewed pull request merged by the validator; a direct push skips review, required checks and CI. Repositories with the `main-only-planfile`, `main-only-files` or `local-audit` delivery profile are exempt, as for the commit hooks. It is declared in `agent-hosts.json` `additionalHooks` and the package manifest, so `agent_host_check` requires it after upgrade.

## 0.20.105

- Work-start observation records a checkout under `.worktrees/.quarantine/` whose ticket intent cannot be read (for example an interrupted merge) as `QUARANTINED_UNREADABLE` instead of aborting every allocation; its Git delta is still compared as pending work. Unreadable intents outside quarantine still fail closed.

## 0.20.104

- Adoption evidence must prove its level: repository evidence must exist and match its SHA-256, S3 must be a CI definition or external proof, S4/S5 external proof (hosted ruleset, runtime receipt), and S3-S5 must not reuse lower-level proof. Records that reuse `.governance/manifest.json` for every level are now reported as `STD-ADOPTION-EVIDENCE`.

## 0.20.103

- Replace direct fleet upgrade writes with read-only requests bound to verified canonical annotated tags, final Releases and exact source package/tool hashes. Refuse unadmitted live dispatch; emitting an artifact grants no target execution authority.

## 0.20.102

- Export exact-state, read-only adoption allocation plans from verified immutable packages. Native allocation independently recomputes the full upgrade scope and writes bounded delivery intent before reservation hashes; stale or modified plans, unsafe paths and missing editing authority remain refusals. Preserve target overrides and existing owners.

## 0.20.101

- Admit only absent, required first-adoption seed files proven by the published manifest, exact installer acknowledgement and Git base. Keep declared ownership, shared-path controls and native writer/publication authority unchanged; protected governance independently recomputes the bounded first-adoption seed scope.

## 0.20.100

- Preserve strictly integrated historical ticket refs during first native bootstrap allocation, with checked ancestry and fresh clone-local ownership observations. Ambiguous refs, live leases, native reservations and changed installer bytes still block; no branch cleanup or writer authority is inferred.

## 0.20.99

- Declare ownership for the installed attributes file and branch hygiene workflow before real first ticket allocation.
- Add explicit bootstrap prerequisite ownership plans bound to committed HEAD and file digests. Existing owners, package targets, dirty files and unsafe paths remain rejected; plans grant no writer or publication authority.


## [0.20.98] - 2026-10-14

### Fixed

- Permit explicit native migration of the closed, committed seven-file Wellman
  registration while refusing native locks, changed bytes and unsafe paths.
- Reuse digest-bound future reusable workflow plans during scaffold migration;
  preserve actual target workflows and first-allocation authority boundaries.

## [0.20.97] - 2026-10-12

### Fixed

- Install CI governance runtime from an immutable SHA in the trusted base adoption
  lock, never a candidate version or mutable tag. Initial adoption without a base
  lock requires the protected repository variable `NEW_PROJECT_RUNTIME_SHA`.
- Keep job-local Python environments and refuse malformed or missing trusted pins
  before installation in both managed and reusable workflows.

## [0.20.96] - 2026-10-12

### Fixed

- Detect literal secrets in Python attribute, subscript and nested assignments,
  preserving dynamic expressions and independently testing the bundled checker.
- Reject external ticket adapters whose path globs cover their own authority file.
- Refuse a Windows-only governance gate on POSIX with a controlled diagnostic.

## [0.20.95] - 2026-10-12

### Fixed

- Store work-start failure diagnostics only in verified ignored, private and
  bounded operational receipts; preserve clean Git state and reject unsafe sinks.
- Preserve structured fail-closed output when directory-relative APIs are
  unavailable and when a workstream is unknown.

## [0.20.90] - 2026-10-07

- Add `.reuse/**`, `.redup/**`, and `.benchmarks/**` to `governance.ownedPaths` and `OVERVIEW.md` to `integration.ownedPaths` in `manifest.default.json` to prevent `GOV-WORKSTREAM-003` during reuse compliance scans and root v2 overview authoring [ticket-318].
- Support configurable delivery profile `maxActiveMinutes` for `XS` complexity classes in `governance_check.py` while preserving the default 10-minute fallback when omitted [ticket-318].

## [0.20.89] - 2026-10-07

- Preserve only the exact unchanged committed legacy ticket tree at a fresh first native bootstrap. Native allocation advances above historical IDs; changed, missing, untracked and symlinked carriers, prior reservations and live ticket branches/worktrees remain refused. No retrospective approval or ticket closure is inferred.

## [0.20.88] - 2026-10-06

- Inspect Python abstract syntax trees to distinguish unquoted dynamic expressions from secret literals.
- Pass variable forwarding (such as passing a token variable), dynamic calls and tuple unpacking without false GOV-SECRET-001 alarms.
- Retain strict secret detection for genuine string literals, string concatenations, malformed Python fallback and shell/config files.

## [0.20.83] - 2026-10-04

- Record exact local scaffold-adoption bytes bound to the original HEAD and clone for explicit first native allocation ownership acknowledgement.
- Admit only unchanged installer-owned pending paths; preserve foreign overlapping changes, stale snapshots, WIP, canonical allocation, controller writer leases and independent publication requirements.
- Render only first-ticket metadata at the original committed base, without copying or committing product or governance source.
- Exercise real first allocation and tamper, foreign path, moved HEAD, clone binding and authority refusal cases in the existing work-admission gate.

## [0.20.82] - 2026-10-04

- Open continuity transaction locks through anchored no-follow POSIX directory descriptors and recheck ancestor and lock inode identities before and after OS lock acquisition.
- Reuse reparse-safe Windows directory and read/write lock handles without delete sharing; retain bounded contention, private regular locks and interrupted-write replay.
- Add deterministic parent/lock substitution, missing-capability, linked-lock and native Windows replacement/junction regressions to the existing storage matrix.

## [0.20.81] - 2026-10-03

- Add explicit pinned native migration for exact minimal Wellman baseline scaffolds; preserve custom/native adoption, source publication proof and target prerequisites.
- Refuse duplicate keys, native adoption evidence and symlinked migration targets before writes; keep read-only review and unchanged default upgrade behavior.
- Run actual migration CLI cases in the existing adoption gate and document truthful upgrade, hook and protected publication boundaries.

## [0.20.80] - 2026-10-03

- Preserve literal Git path identities with NUL-separated status and diff records, including Unicode, whitespace, line endings and distinct non-UTF-8 filesystem bytes.
- Include both original and destination paths for staged and committed renames so overlap observations cannot miss either endpoint.
- Exercise source and actual managed installations with disposable Git worktrees on Linux and Windows; retain existing layout, base and ignore policies.

## [0.20.79] - 2026-10-03

- Fail the adopted pytest governance lifecycle when no explicit, event or verified upstream Git base resolves, instead of substituting HEAD and hiding committed changes.
- Preserve valid base sources, verified equal-head upstreams, collect-only behavior and existing hook activation and event fetching.
- Exercise actual Git and lifecycle regressions on Linux and Windows; bind the existing standalone integration fixture to its known upstream baseline.

## [0.20.78] - 2026-10-03

- Reject adjacent letter and digit suffixes when matching ticket numbers in read-only local and origin branch activity observations.
- Preserve supported branch forms and genuine outstanding reservations; retain independent terminal and lease authority.
- Exercise the actual source and bundled Git observers in portable regression tests, including Windows runtime validation.

## [0.20.77] - 2026-10-03

- Combine current output-path and resolved-ticket writer errors with cached preflight findings, summaries and exit status.
- Preserve cached warnings/timing and later valid reuse; keep cache entries unchanged by invocation errors and retain cache-disabled CI.
- Synchronize the installed checker and exercise the actual source/bundle CLI on Linux and Windows without granting advisory cache data any authority.

## [0.20.76] - 2026-10-03

- Validate execution-model names, object declarations, maximum levels and boolean effect flags before adoption conformance.
- Confine managed-artifact file access to the canonical checkout; reject portable drive/root/parent escapes before hashing and report resolution/read failures.
- Preserve valid catalog metadata, model levels and confined artifacts, including in-root symlinks; verify the actual strict CLI on Linux and Windows without granting runtime effects.

## [0.20.75] - 2026-10-03

- Reject repeated physical change identities even when their before/after states or acceptance metadata differ.
- Reject no-change markers mixed with changes to the same contract while preserving independent properties, signals and contracts.
- Exercise the actual physical contract gate and source/bundle parity in portable regression tests without executing hardware effects.

## [0.20.74] - 2026-10-03

- Align branch-name checks in the intent schema, source runtime and installed bundle with Git's ref rules; reserve standalone `@` because its revision meaning is HEAD.
- Reject invalid dot/lock components, trailing separators/dots, leading dash and ASCII whitespace/control names while retaining valid Unicode and punctuation.
- Compare source, bundle and schema against the actual Git branch validator in the existing Linux/Windows runtime suite.

## [0.20.73] - 2026-10-03

- Open continuity streams through anchored no-follow POSIX descriptors and held Windows reparse-point-safe handles.
- Reject linked or non-regular stream targets before data access; preserve append-only events, absent reads and replay/recovery.
- Add portable link regressions plus native Windows junction and POSIX substitution/capability checks.

## [0.20.72] - 2026-10-03

- Reject malformed remediation collection/source shapes with structured errors while preserving original input, exact path bytes and advisory authority.
- Require full timezone-qualified source timestamps and retain valid explicit offsets.
- Cover malformed cross-field data, JSON CLI output, blocked projection and input immutability in portable regressions.

## [0.20.71] - 2026-10-03

### Fixed
- Align standalone repository-policy and remediation scope globs with the existing canonical governance segment algorithm. Single-star and question-mark globs stay within directory segments; whole-segment recursive stars cover zero or more directories. Preserve character classes, Unicode, staged snapshot selection and advisory authority; synchronize the existing repository-policy bundle without introducing a remediation bundle.

## [0.20.70] - 2026-10-03

### Fixed
- Replay only the explicitly supported check-gate rules and reject caller-supplied results for unimplemented rules. Require unique nonempty check names and reject contradictory observations. Derive defaults from local hub/adopter metadata without inventing observed PASS; preserve denied evaluations, supported aliases, diagnostic codes and the independent publication boundary. Synchronize installed-package behavior.

## [0.20.69] - 2026-10-03

### Fixed
- Require the complete local agent source set for the selected canonical hub or adopter contract, including each applicable manifest, lock and package. Reject omitted declarations, missing or unsafe files, duplicate local identifiers and unknown layouts; retain optional inactive-layout files and the diagnostic result shape. Preserve explicit selected-contract context and synchronize installed-package validation.

## [0.20.68] - 2026-10-03

### Fixed
- Constrain declared host paths to portable repository-relative paths without parent traversal, drive prefixes, control characters or empty segments. Reject package governance gates outside the checkout or reached through symbolic links, including when lock metadata is unavailable. Preserve valid hub/adopter paths and Unicode file names; retain existing finding shape and installed-package parity.

## [0.20.67] - 2026-10-03

### Fixed
- Return stable diagnostics without a fabricated receipt or arithmetic crash for malformed transition documents. Require rejected trace receipts to preserve counters/phase and match the last accepted lease identity/state; only accepted receipts advance the trace anchor. Preserve scalar validation and local allocation identity; reuse portable and installed-package regressions.

## [0.20.66] - 2026-10-03

### Fixed
- Enforce canonical scalar types, string bounds, patterns, nullable references and explicit-offset timestamps in lease, request and receipt validation without new runtime dependencies. Preserve transition reply and trace behavior; run portable scalar and installed CLI regressions on Linux and Windows. Make basename-only native allocator projections schema-conforming through an explicit nonauthoritative local namespace.

## [0.20.65] - 2026-10-03

### Fixed
- Block relevant todo2code file-delete proposals under the closed remediation DSL, including IMPLEMENT actions with destructive and explicit-human risk metadata. Preserve advisory authority, valid modify plans and isolation from unrelated history. Run complete synthetic producer-plan regressions on Linux and Windows.

## [0.20.64] - 2026-10-03

### Fixed
- Terminate ticket allocation on SIGINT/SIGTERM after cleanup instead of continuing with a released clone lock. Reject ASCII control-character titles before reservation and encode JSON scalars with the existing Python serializer while preserving Unicode.
- Reject malformed or duplicate managed host contract headings without replacing user pointer bytes or reporting successful activation.
- Match zero-directory cases for whole-segment recursive globs, preserving simple-star boundaries and literal regex characters. Run actual allocator, pointer and glob regressions in Linux and Windows CI; signal checks remain POSIX-specific.

## [0.20.63] - 2026-10-03

### Fixed
- Use Node canonical file URLs for both the independently captured Registry module closure and entry identity. Preserve verified-byte execution, stdin and argv for tilde, Unicode, percent and hash paths.
- Run byte-exact Registry integrity regressions on Windows as well as Linux; retain the existing required job names and fail-closed exit propagation.

## [0.20.62] - 2026-10-03

### Fixed
- Respect ancestors when merging ticket rows, table headers and surrounding prose. Preserve one-sided deletions and edits, merge independent additions and fall back to Git conflicts for conflicting edits or ambiguous sections.
- Run continuity storage and ticket-index regressions in Linux and Windows CI, and captured Registry regressions on Linux. Canonicalize mocked continuity fixture roots across Windows temporary-path aliases. The diagnosed Registry URL canonicalization failure and its Windows wiring are deferred with the runtime fix to a dependent ticket.

## [0.20.61] - 2026-10-03

### Fixed
- Serialize continuity journal validation, append, advisory index replacement and rebuild with a bounded per-stream OS file lock. Reject stale concurrent checkpoints before append and restore interrupted index writes on exact replay.
- Preflight bounded index serialization and validate event digests before persisting. Add real process regressions for concurrent writers, rebuild races and replay recovery.

## [0.20.60] - 2026-10-03

### Fixed
- Execute the exact captured, independently pinned Registry ESM module closure rather than reopening mutable source paths after verification. Preserve CLI module identity, arguments and stdin; reject unpinned imports and unbounded/non-regular module inputs.
- Add real Node regressions for entry-point/dependency replacement, Unicode input, large source frames and closed module resolution.

## [0.20.59] - 2026-10-03

- Fail overlap audits on incomplete Git inspection or malformed active file/SQLite intent. Share ticket branch matching so outstanding supported local and origin branch forms retain activity even when ticket content already exists on the target.

## [0.20.58] - 2026-10-03

- Preserve non-default network ports in repository identities, reject incomplete overlap inventory and derive omitted inventory. Rescan existing worktrees each watch interval so dirty edits update overlap reports without a topology change.

## [0.20.57] - 2026-10-02

- Return deterministic catalog findings for malformed ownership, inheritance, requirement and alias inputs; reject Boolean checkpoint sequence values. Install an adopter-specific guard configuration pointing to its managed checker, with command execution regressions.

## [0.20.56] - 2026-10-02

- Bind snapshot entry mode and bytes to the same no-follow descriptor and reject observed replacement or mutation during proof collection. Add deterministic filesystem-race regressions and synchronize the bundled runtime.

## Unreleased

## 0.20.55 - 2026-10-02

- Fenced pre-adoption recovery accepts its exact published origin branch alias
  while rejecting divergent heads, duplicate identities and foreign remotes.
  Existing source, refs and protected approval requirements are preserved
  [ticket-281].

- Adopters can declare files with physical meaning in
  `.governance/physical-contracts.json`. A change to such a file needs a
  `physicalChanges` intent entry per changed property (pin, active level,
  pull, capability set, scale, range, timing) with before, after and hardware
  acceptance checks; otherwise the gate reports `GOV-PHYS-001`. Motivated by a
  limit-switch polarity flip and a dropped pump module that both passed their
  repository tests [ticket-280].

- `propagate-standard` fails with an explicit error when `ORG_GOVERNANCE_TOKEN`
  is unset or an organization cannot be listed, and skips the upgrade matrix
  when no adopter is found. Previously an unset secret silently discovered zero
  adopters and every release run failed on an empty matrix, so adopters were
  never upgraded [ticket-275].

## 0.20.54 - 2026-09-28

- Managed snapshot proposals reserve an identity without writer authority. Exact
  external grants and live controller fencing are required before materializing
  a lossless two-parent import; failed candidates remain detached for recovery
  [ticket-279].
- Verified unchanged imports retain source history while repairs keep normal
  scope, ownership and budgets; import-only publication still needs independent
  exact-head approval [ticket-278].

## 0.20.53 - 2026-09-24

- Local OneDev verification followed by the independent Validator is the
  default publication route for every repository, not only `semcod/*` and
  `subactor/*`. An adopter may only narrow that default with the optional
  `.governance/local-ci-publication.json`
  (`new-project.local-ci-publication/v1`); absent or `mode: "all"` means
  unrestricted, and a restriction never grants authority [ticket-270].
- The authored local-ci-publication document and the adopter reference copy
  now pin the merged ticket-270 revision `d4dab328` under standard 0.20.53
  instead of the superseded 0.20.10 revision `d5f77d8`, with document and
  managed-copy digests updated [ticket-274].

## 0.20.50 - 2026-09-24

- Adopter workflows run `wellman check` with `--actor ci`, so CI no longer
  fails on developer-clone checks such as an unset `core.hooksPath`
  (`GOV-AGENT-HOST-006`) [ticket-269].

## 0.20.49 - 2026-09-23

- The adopter governance workflow no longer forces `standard_pack_check.py
  --strict`; the adopter's `standard-adoption.json` mode decides, so `enforce`
  fails on missing packs and `audit` reports them without failing CI
  [ticket-268].

## 0.20.48 - 2026-09-23

- Bundle the complete governance checker closure (`governance_check.py` and
  the eight sibling modules it loads) in the `wellman` package, synchronized
  byte-for-byte from `scripts/` by `packages/wellman/sync_bundled.py`; support
  the documented `wellman --version` and `wellman check [--json]` invocations;
  test the installed wheel in CI [ticket-266].

## 0.20.47 - 2026-09-23

- Install the governance runtime from the immutable `wellman-v<standard>` Git
  tag so adopter CI does not depend on PyPI trusted-publisher configuration;
  keep PyPI publication failures visible (failed run) while still creating the GitHub release
  asset [ticket-265].

## 0.20.46 - 2026-09-22

- Raise the default active-ticket capacity per workstream from 3 to 8 for
  concurrent work by multiple agent providers, while retaining leases,
  canonical worktrees, scope ownership and overlap fencing [ticket-262,
  ticket-263].

## 0.20.45 - 2026-09-22

- Standardize root LICENSE recognition in governance workstream and provide Apache-2.0 template [ticket-260, ticket-261].

## 0.20.44 - 2026-09-22

- Support Windows batch gate execution in pytest governance plugin template [ticket-258].

## 0.20.43 - 2026-09-22

- Publish a digest-bound managed-copy inventory so Docs validation excludes
  standard-provided `.governance/docs` files from product-document checks
  [ticket-257].

## 0.20.42 - 2026-09-22

- Add strict standard-pack enforcement for CI while preserving audit-only local
  rollout mode [ticket-257].

## 0.20.41 - 2026-09-22

- Add `wellmanifest/docs` to the baseline pack and expose its canonical policy
  from agent host guidance [ticket-257].

## 0.20.40 - 2026-09-22

- Harden repository delivery profiles against staged/working-tree drift,
  out-of-scope deletions, unsafe paths and same-commit adapter expansion;
  support audit-only hook dispatch [ticket-257].

## 0.20.39 - 2026-09-21

- Add explicit repository delivery profiles, including `main-only-planfile`,
  and validate external ticket adapters with bounded staged scopes [ticket-257].

## 0.20.38 - 2026-09-19

- Restore the independent protected-review boundary in hub and adopted host
  guidance; reject account, administration and browser bypasses, forced cleanup
  and WIP waivers, with regressions for both projections [ticket-256].

## 0.20.37 - 2026-09-19

- Allocate file-backed tickets in canonical Worktrees v5 linked checkouts with
  a matching local lease, preserving the clone-wide reservation and leaving
  primary ticket carriers untouched [ticket-255].

## 0.20.36 - 2026-09-19

- Recover a pre-adoption ticket through the explicit local allocator route,
  checking live external controller ownership, exact HEAD/dirty state, scope,
  canonical relative worktree and unused identity under controller and clone
  locks. Ordinary allocation remains fail-closed [ticket-254].

## 0.20.35 - 2026-09-19

- Support standard upgrade verification from repositories whose base revision contains legacy subset locks (e.g., standard 0.14 where not all package-manifest entries were locked into manifest.lock.json) [ticket-252].

## 0.20.34 - 2026-09-19

- Generate adopted `AGENTS.md` files with one final newline, so a clean,
  atomic standard upgrade passes `git diff --check` [ticket-250].

## 0.20.33 - 2026-09-19

- Skip the managed pytest governance gate for `--collect-only` inventory
  sessions before any gate or Git operation. Sessions that execute tests retain
  the existing fail-closed behavior [ticket-248].

## 0.20.30 - 2026-09-14

- Classify private component state explicitly without weakening integration ownership for migrations, transfers or legacy data-impact descriptions; distribute a deterministic remediation runbook.

- Add an opt-in lossless snapshot migration proof bound to an independently pinned external grant, original Git parents and exact inventory.
- Keep ordinary repair budgets, secret scanning and independent publication approval; reject consumed grants and changed subjects.

## 0.20.14 - 2026-09-08

- Distribute published Worktrees 0.5.2 so canonical allocation preserves existing repository basenames, including .github, mixed case, underscores and spaces.

## [Unreleased]

## [0.20.94] - 2026-10-12

### Docs
- Update project/ticket-333/README.md

### Test
- Update tests/ticket-allocation-worktree.test.py

### Other
- Update VERSION
- Update governance/manifest.default.json
- Update governance/manifest.hub.json
- Update packages/wellman/pyproject.toml
- Update project/new-ticket.sh
- Update project/ticket-333/intent.json

## [0.20.29] - 2026-09-14

### Fixed
- Reuse repeated activity reads within one checkout inspection, then revalidate consulted Git and document inputs before accepting results. Pin ancestry targets to observed commit IDs, discard batches after each invocation, and preserve independent clone and terminal receipt authority [ticket-230].

## [0.20.28] - 2026-09-14

### Fixed
- Derive adoption/governance fixture versions from canonical source data instead of the current release literal. Keep mismatch tests negative even when the source version matches the usual sentinel; validate source, manifest and lock agreement [ticket-227].
- Avoid false work-admission conflicts from unregistered historical branches only when every unique complete commit tree occurs in observed target history after divergence. Preserve refs, new rollback intent, active-worktree protection, WIP limits and cleanup authority; matching HEAD or patch IDs alone is insufficient [ticket-225].

### Added
- Offer opt-in read-only publication observation separating dirty paths, remote commit reachability, branch binding and target ancestry. Missing or changing evidence stays unknown; observation grants no push, merge, release or cleanup authority [ticket-226].

## [0.20.27] - 2026-09-13

### Fixed
- Preserve every nonzero Goal refusal in the explicit standard-update adapter; generic diagnostic text no longer overrides errors. Remove unused drift helpers and cover stdout/stderr diagnostic collisions [ticket-221].

## [0.20.26] - 2026-09-13

### Fixed
- Prevent ceremony-only worktrees and recursive decision evidence. Local checks remain reports, not trusted review decisions.
- Inspect pending branches, worktrees, intents and workstream capacity before allocating another ticket; prefer reuse, read-only help, controlled handoff or serialization. Ship the closed work-start report, fail-closed allocator integration and regression tests in the same material ticket [ticket-218].

## [0.20.25] - 2026-09-12

### Fixed
- Keep `scripts/agent_host_check.py` importable on interpreters without `tomllib` (Python 3.10). `governance_check.py` reported the `ImportError` as a missing managed validator, so an adopter declaring `requires-python >=3.10` failed its own gate with a false `GOV-SYNC-001`, and the pytest lifecycle binding aborted the session. The Python packaging binding is skipped when no TOML reader exists; 3.11+ enforces `GOV-PACKAGING-001/002/003` unchanged [ticket-216].

## [0.20.24] - 2026-09-11

### Test
- Update tests/adoption-lock.test.sh
- Update tests/governance-validator.test.sh

### Other
- Update VERSION
- Update governance/manifest.default.json
- Update governance/manifest.hub.json

## [0.20.4] - 2026-09-02

### Automatic, fail-closed standard update preparation

- Add a managed pre-commit controller that checks the local immutable pin,
  resolves the latest final release through Goal and prepares an atomic update
  only under an exact staged adoption ticket.
- Abort the initiating commit after preparing an upgrade so the full diff can
  be reviewed and restaged; never silently commit, merge or publish it.
- Allow adopters to disable freshness checks or select `goal`/`koru-goal`
  execution through validated `standard-adoption.json` configuration.
- Publish `GOV-STANDARD-UPDATE-001`, its runbook and deterministic hook,
  configuration and failure-path tests as managed standard payload.

## [0.20.3] - 2026-09-02

### Digest-bound target-owned adoption transitions

- Allow an upgrade ticket to migrate an existing target-owned CI workflow in
  the same atomic adoption only with its exact path plus accepted-base and
  working-head SHA-256 digests.
- Restrict eligible targets to workflow patterns from the immutable managed
  adoption-binding registry; declarations cannot create, delete or overlap a
  package-owned target.
- Reject malformed, duplicate, unused, unallowlisted and digest-mismatched
  transitions while retaining all managed takeover, restoration and lock
  checks.

## [0.20.2] - 2026-09-01

### Protected rewritten-merge terminal receipts

- Preserve direct ancestry as the primary terminal proof and add fail-closed
  fallbacks for GitHub rebase and squash merges.
- Require rebase to preserve a linear, equally long series of ordered stable
  patch IDs; require squash to match the aggregate head patch with one terminal
  commit before releasing a reservation.
- Continue requiring the terminal SHA to be reachable from the declared target
  branch; malformed, nonlinear, empty or changed series remain active.
- Keep the existing receipt schema and append-only registry bindings while
  publishing the corrected policy, runtime, runbook and regression fixture.

## [0.20.1] - 2026-09-01

### Host-agnostic local continuity

- Keep `.subactor/manifest.json` tracked while managing ignores only for local
  leases, sessions, recovery, receipts, cache and content-addressed snapshots.
- Advance continuity to v2: append-only host-agnostic session events have no
  policy size cap, while a bounded latest-checkpoint index is replaced
  atomically and can be rebuilt from the stream.
- Bind every checkpoint to the exact plan, slice, ticket, branch, HEAD, lease,
  remote/account observation and snapshot receipt. Dirty work is resumable
  only from a commit or a content-addressed snapshot with a secret-scan receipt.
- Make the managed pre-commit validate only the locally pinned standard. It
  never fetches or mutates; explicit adoption/updater automation owns freshness.
- Add the provenance-verified worktree test bootstrap template derived from
  `autogrammar/hillm` commits `305361a` and `b8a9f8a`.

## [0.20.0] - 2026-09-01

### Repository-local relative delivery worktrees

- Adopt immutable `wellmanifest/worktrees` v0.4.0 from exact source revision
  `73f9b99227bfbad6ce02834324d053279fb48611`.
- Make `<primaryCheckout>/worktrees/<ticket-NNN>--<slug>` with relative Git
  metadata the only publishable layout and bind its lease below
  `<primaryCheckout>/.subactor/leases/`.
- Require anchored `/worktrees/` and `/.subactor/` ignores, primary-checkout
  resolution from Git, and a Git 2.51 relative-path feature probe.
- Classify legacy v1/v2/v3, `/tmp`, duplicate and unknown registrations as
  read-only recovery inventory. Never move, repair, delete, prune or clean
  observed work automatically.

## [0.19.22] - 2026-09-01

### Collision-proof branch worktree namespace

- Pin the immutable `wellmanifest/worktrees` v0.3.0 owner artifacts.
- Place every new delivery worktree under the reserved
  `<workspace>/.worktrees/.branches/<repo>/<ticket-NNN>--<slug>` namespace.
- Reject symbolic-link traversal in existing canonical path components before
  a runtime performs Git or filesystem effects.
- Preserve version 1 and version 2 worktrees as legacy inventory; never move
  them automatically or create a separate release-only commit.

## [0.19.21] - 2026-09-01

### Legacy-adopter anti-noise compatibility

- Assign the shared manifest, lock, package marker, agent contract and every
  extendable governance target used by atomic adoption to one integration
  workstream, so one precise adoption ticket can own the complete material
  diff. A verified adoption lock joins that atomic ownership proof.
- Reject legacy target overrides that make agent prose, raw logs, preprompts or
  ticket changelogs mandatory; the only required ticket files are `README.md`
  and `intent.json`.
- Keep the patch release in the same material changeset and reuse its terminal
  merge receipt instead of creating a release-only ticket or PR.

## [0.19.20] - 2026-09-01

### Repository-namespaced ticket worktrees

- Pin the immutable `wellmanifest/worktrees` v0.2.0 owner artifacts.
- Standardize `<workspace>/.worktrees/<repo>/<ticket-NNN>--<slug>` and matching
  repository-scoped leases across every adopter.
- Reject the legacy flat layout and require audit-first, non-destructive
  migration of existing linked worktrees.
- Publish the version from this material changeset instead of creating a
  separate release-only ticket and pull request.

## [0.19.15] - 2026-08-30

### Registered ticket allocation

- Separate the compatible single-clone high-water profile from distributed
  allocation through an adopter-registered atomic process URI.
- Add closed request and receipt contracts with exact repository, correlation,
  issuer, digest, expiry and fencing-token bindings.
- Make `new-ticket.sh` fail closed for distributed writers without a fresh
  receipt and reject identities already visible in repository state.
- Standardize lossless ticket-collision recovery: preserve both heads, trust
  only the terminal merge receipt, allocate a successor, verify equivalence,
  then close the predecessor as superseded.

## [0.19.14] - 2026-08-30

### Docs
- Update CHANGELOG.md
- Update project/ticket-160/README.md

### Test
- Update tests/adoption-lock.test.sh
- Update tests/governance-validator.test.sh

### Other
- Update VERSION
- Update governance/manifest.default.json
- Update governance/manifest.hub.json
- Update project/ticket-160/intent.json
- Update scripts/governance_check.py

## [0.19.14] - 2026-08-30

### Resolver-aware active ticket content

- Apply active-only ticket scaffold requirements to the verified activity set
  instead of the raw Markdown status projection.
- Preserve executable-content scanning across every ticket directory.
- Add regression coverage proving terminal receipts remove false scaffold
  blockers while genuinely active incomplete tickets remain fail-closed.

## [0.19.13] - 2026-08-30

### Resolver-aware dependency ordering

- Reuse verified external terminal receipts when validating ticket
  dependencies instead of consulting only the Markdown status projection.
- Keep missing, non-terminal and unverifiable prerequisites fail-closed with
  the existing `GOV-DEPENDENCY-002` diagnostic.
- Add a Git-ancestry regression fixture proving a merged prerequisite releases
  its dependent ticket without a repository closure commit.

## [0.19.12] - 2026-08-30

### Self-hosted governance Python compatibility

- Keep pinned Python 3.11 provisioning on GitHub-hosted runners, but use an
  already-provisioned compatible `python3` on self-hosted runners.
- Fail closed with an explicit Python 3.11+ prerequisite instead of asking
  `actions/setup-python` for an unavailable build on a newer host distro.
- Preserve the same deterministic governance commands and merge gates on both
  runner environments.

## [0.19.11] - 2026-08-30

### Recoverable terminal receipt activity

- Resolve ticket reservations through one managed status/receipt resolver used
  by the allocator, governance gate and worktree overlap checker.
- Release stale `IN_PROGRESS` projections only when external terminal receipt
  bindings and Git ancestry verify; unsupported or malformed evidence remains
  conservative with `GOV-TICKET-ACTIVITY-001`.
- Require every fail-closed blocker to expose an authority-preserving exit, and
  keep normative standards focused on invariants and forbidden shortcuts.

## [0.19.10] - 2026-08-30

### Registry-driven revision workflow bindings

- Ship the exact revision-bound workflow paths as a digest-locked managed
  registry instead of maintaining a repository-specific runtime list.
- Admit a registered workflow into atomic adoption only when both its reusable
  workflow pin and `standard-ref` equal the immutable target revision.
- Fail closed for malformed registries, wildcard paths, missing workflows and
  mismatched pins.

## [0.19.9] - 2026-08-30

### Consistent atomic adoption ownership

- Derive one digest-verified managed-path set from the immutable package and
  base/head locks, then reuse it in coordination and change-scope gates.
- Keep `seed`, `extendable`, target-owned and unverified paths behind their
  manifest-declared workstream ownership.

## [0.19.8] - 2026-08-30

### Registry-driven ticket allocation

- Resolve active lifecycle statuses and valid workstreams from the current
  governance manifest rather than duplicating their values in the allocator.
- Fail closed before allocation when the manifest registry is missing,
  malformed or does not declare the requested workstream.

## [0.19.7] - 2026-08-30

### Truthful worktree ticket attribution

- Attribute an active ticket scope only to its matching branch or a checkout
  actually changing that ticket directory.
- Stop historical `IN_PROGRESS` copies without either ownership signal from
  reserving every active worktree while preserving real path collisions.

## [0.19.6] - 2026-08-28

### Portable and durable adoption

- Allow adopters to select a repository-appropriate governance runner through
  `NEW_PROJECT_RUNNER_LABEL`, while retaining `ubuntu-latest` as the default.
- Preserve downstream managed-file bindings across adoption upgrades so
  generated governance remains reproducible after the first installation.

## [0.19.5] - 2026-08-28

### Atomic adoption bindings

- Permit atomic standard adoption to update only the target packaging and
  Docker files required by the adopted contracts across workstream ownership;
  unrelated application paths remain governed normally.

## [0.19.4] - 2026-08-28

### Docker multi-stage validation

- Recognize previously declared Docker build-stage aliases as internal graph
  references while retaining immutable digest enforcement for external images.

## [0.19.3] - 2026-08-28

### Monorepo application ownership

- Assign conventional `packages/**` source trees to the default application
  workstream so monorepo adopters can govern package changes without a local
  manifest fork.

## [0.19.2] - 2026-08-28

### Integrated coordination snapshots

- Stop projecting tracked `IN_PROGRESS` authorization snapshots as concurrent
  live writers when the integrated default branch has no proposed change.
- Preserve fail-closed ticket selection and collision diagnostics for every
  non-empty material or governance change.

## [0.19.1] - 2026-08-28

### Atomic target-owned adoption profile

- Classify `.governance/standard-adoption.json` as a governance carrier in
  both adopter and hub manifests so introducing the seed during an immutable
  standard upgrade does not become a false cross-workstream product change.
- Add Linux and Windows conformance coverage for the carrier classification.

## [0.19.0] - 2026-08-28

### Material delivery without ticket ceremony

- Allow bounded intent to enter atomically with the first material change;
  remove the mandatory plan-only commit.
- Reject ticket, TODO, ticket-index and generated-registry-only changes as
  non-delivery.
- Close merged or no-change work through protected external receipts without a
  repository closure commit, branch or pull request.
- Reduce the required ticket scaffold to `README.md` and `intent.json`; raw
  command logs and participant prose are optional and stay out of Git by
  default.

### Canonical ticket worktree placement

- Adopt the immutable `wellmanifest/worktrees` contract at revision
  `bad8fab4ef96e770ccc4e4089bb4a3d623c1651a` with SHA-256-bound schema and
  conformance checker artifacts.
- Distribute the schema, pure path checker and dependency lock as managed
  governance files in generated projects.
- Require workspace-level `.worktrees` placement and reject repo-local,
  parallel-root, nested and duplicate-clone layouts for publishable ticket work.

## [0.18.10] - 2026-08-25

### Autonomous change fencing and managed recovery

- Distribute a closed multi-agent change-lease contract with compare-and-swap,
  monotonic revisions, fencing tokens, publication freeze and terminal
  receipts while keeping the effectful runtime in adopters.
- Bind the lease contract to normative claim-before-effect, heartbeat,
  exact-head publication and merge-receipt operating rules with deterministic
  enforcement traceability.
- Allow an upgrade to restore a base-declared managed target missing from the
  accepted Git tree only through an exact-path, exact-base-lock-digest
  declaration consumed once; existing base bytes remain ineligible.

## [0.18.9] - 2026-08-25

### Pytest governance lifecycle plugin

- Ship the managed `wellmanifest_governance` pytest plugin referenced by
  Python adopter configurations.
- Run the deterministic repository governance gate once before pytest
  collection with explicit base and changed-path evidence.
- Fail closed on invalid governance results without adding a runtime
  dependency, with Linux and Windows CI coverage.

## [0.18.8] - 2026-08-25

### Manifest-declared terminal closure enforcement

- Honor both `DONE` and `CANCELLED` from `ticket.closedStatuses` in the hub and
  managed adopter pre-commit hooks.
- Apply the same fail-closed, governance-only path and deletion restrictions to
  every terminal closure, including worktree guard execution.
- Keep diagnostics and remediation status-neutral and add lifecycle regression
  coverage for cancellation.

## [0.18.6] - 2026-08-23

### Windows pre-commit executable check fix

- Guard the POSIX executable check on `.githooks/pre-commit` in `agent_host_check.py` with `os.name != 'nt'`, preventing false-positive test failures on Windows CI.

## [0.18.5] - 2026-08-23

### Host-agnostic governance enforcement

- Distribute one deterministic host contract, instruction surfaces and
  fail-closed Git hook to adopters as managed package artifacts.
- Validate host materialization, hook activation and package lifecycle
  bindings through the ordinary governance gate.
- Add `governance / enforce` to the managed adopter workflow so the full
  governance validator runs in CI instead of checking remote branch lifecycle
  alone.
- Extend diagnostic and rule-enforcement audits to cover Git hooks and the
  host-contract validator.

## [0.18.4] - 2026-08-21

### Managed text hygiene

- Remove trailing whitespace from the managed `AGENTS.md` source so adopters
  pass diff-hygiene checks after an upgrade.
- Add a manifest-driven regression that rejects trailing horizontal whitespace
  in every `managed` or `extendable` package source.

## [0.18.3] - 2026-08-21

### Digest-bound managed target takeover

- Authorize a changed pre-existing target entering managed ownership only with
  its exact path and SHA-256 digest from the accepted Git base.
- Reject missing, malformed, duplicate, mismatched and unused takeover
  declarations while preserving immutable head-lock verification.
- Add deterministic rule traceability and positive/fail-closed takeover tests.

## [0.18.2] - 2026-08-21

### Generated artifact receipt ownership

- Treat the exact `config/artifact-registry.json` receipt as governance
  metadata so managed-document builds do not falsely cross workstream scope.
- Permit that exact receipt in governance-only DONE closures while retaining
  fail-closed rejection for adjacent `config/**` files and implementation.

## [0.18.1] - 2026-08-14

### Generated bootstrap placeholder secret scan

- Accept only the exact uppercase `__GENERATE_[A-Z0-9_]+__` bootstrap marker
  as a safe tracked placeholder, allowing generated `.env.example` contracts
  to remain publishable without embedding credentials.
- Keep `GOV-SECRET-001` fail-closed for marker prefixes, suffixes, lowercase
  spellings, forbidden characters and real token-shaped values.

## [0.18.0] - 2026-08-14

### HOME vs ADOPT placement

- Add optional `intent.json` `placement` (`home`, `shape`, `runtimeOwner`,
  `adopt`) so SERVICE/FEATURE that create a repo can name the owning org
  without treating "w ramach wellmanifest" as HOME. Existing tickets stay
  valid; invalid placement values reject. `runtime_service` must not HOME
  wellmanifest.

- Keep adoption distinct from repository ownership: `adopt` contains closed
  `wellmanifest/<pack>` identifiers while `home` and `runtimeOwner` use the
  closed `wellmanifest`, `subactor` or `semcod` vocabulary.
- Validate placement deterministically, including the cross-field rule that a
  runtime service cannot be HOME in Wellmanifest.

## [0.17.0] - 2026-08-14

### Repository modes and bounded delivery profiles

- Declare standalone and monorepo topology explicitly, with component-root
  validation for monorepo targets and backward-compatible standalone handling
  for existing v2 manifests.
- Keep Docker opt-in and validate existing Docker configuration without
  inferring a container requirement from the application kind.
- Add closed XS/S/M/L delivery profiles and bind each ticket's declared file,
  component, public-interface and runtime-dependency budgets to its exact
  complexity class.
- Keep workflow status and execution state distinct so only `IN_PROGRESS`
  reserves ownership while `EDIT`, `VALIDATION` and `PUBLICATION` remain
  implementation states.

## [0.16.2] - 2026-08-12

### Orphan local branch workspace audit

- Inventory every non-default local branch in the shared Git directory so a
  released worktree cannot leave an invisible disposable branch behind.
- Report orphaned refs and secondary checked-out branches with stable
  `GOV-WORKSPACE-LIFECYCLE-004` evidence, while retaining exact-path
  allowlisting only for the branch checked out in that explicitly active
  workspace.
- Keep the checker read-only and fail closed when a default branch cannot be
  derived safely; cleanup still requires independent dirty-state, integration
  and reachability evidence before deleting an exact ref.

## [0.16.1] - 2026-08-12

### Canonical managed workflow formatting

- Canonicalize the managed governance workflow's cron scalar for Prettier 3
  without changing its schedule or behavior.
- Guard the exact managed byte with a dependency-free contract test so adopted
  targets remain formatting-clean without bypassing their immutable lock.

## [0.16.0] - 2026-08-12

### Validated remediation planning and source-hub delivery

- Add the target-owned `new-project.remediation-intent/v1` DSL, semantic
  validator and canonical LLM/todo2code projections, with digest-bound advisory
  analysis that cannot expand approved authority or scope.
- Register deterministic remediation diagnostics and adopted schema, template,
  analyzer and runbook coverage for detector false positives, unreadable paths,
  ambiguous layouts, missing inventory, dirty worktrees and release ordering.
- Replace the ticket-specific generated Goal defaults with the truthful generic
  `new-project` release contract: no package registry, governed PR delivery and
  an immutable Git tag plus GitHub Release from clean `main` only.
- Validate the Governance Hub's real pull-request diff against its active ticket
  intent so a generated file outside `allowedPaths` cannot pass on fixture tests
  alone.

## [0.15.0] - 2026-08-12

### Truthful publication provenance and complete lifecycle standard

- Require the adoption generator itself to verify that the canonical annotated
  version tag peels to the requested full SHA and that its GitHub Release is
  final, published and bound to the same tag before recording `published`.
- Add an explicit fixture-only candidate mode that records
  `unpublished-test`; the production governance validator continues to reject
  that provenance as an immutable published standard.
- Establish Goal 2.1.295 or newer as the supported production adoption entry
  point, retaining generator-level verification as defense in depth.
- Publish the accumulated v0.14.1 follow-up standard: atomic initial adoption,
  target prerequisite diagnostics, stackless and Docker ownership repairs,
  branch/worktree cleanup enforcement, collision-free ticket allocation,
  Node.js 24 Actions, and canonical diagnostic/runbook contracts.

## [0.14.1] - 2026-08-10

### Bounded autonomous execution and safe legacy migration

- Treat an explicit request to execute or work autonomously as bounded session
  authorization, eliminating a redundant confirmation pause while retaining
  separate authority for destructive actions, secrets, material scope growth
  and trusted exact-head merge approval.
- Generate new tickets consistently in `IN_PROGRESS / EDIT` with the same
  authorization language in hub templates and the managed downstream fallback.
- Migrate a legacy target manifest from the exact content authenticated by its
  installed lock hash instead of reconstructing a possibly unavailable or
  mismatched pristine historical default.
- Preserve target-owned manifest extensions, add current managed requirements
  during upgrade and fail closed on a tampered legacy manifest.
- Validate the patch through Goal-shaped migration, generator fallback, Linux,
  Windows and independent exact-head Validator App regressions.

## [0.14.0] - 2026-08-09

### Extendable target manifest contract

- Added the bounded `extendable` package strategy for the target-owned
  `.governance/manifest.json`, while keeping exact standard-owned fields in
  the managed `.governance/manifest.base.json` projection.
- Preserve downstream project-specific workstreams across deterministic
  adoption upgrades without adding the extendable target to the managed lock.
- Fail closed when the accepted managed base has drifted, and migrate legacy
  seed installations through a revision-bound three-way merge.
- Validate the public adoption contract through Linux, Windows, exact-head
  independent review and a real customized todo2code manifest smoke test.

## [0.13.2] - 2026-08-08

### Protected branch lifecycle acquisition

- Acquire `deleteBranchOnMerge` through GitHub's typed GraphQL Repository
  field instead of relying on an optional property in the restricted REST
  repository response.
- Preserve the strict `new-project.branch-lifecycle-snapshot/v1` schema and
  unchanged fail-closed deterministic validator; missing or malformed facts
  remain blocking.
- Add a workflow regression that requires GraphQL acquisition and rejects
  renewed reliance on `repository.data.delete_branch_on_merge`.
- Validate the repair through the full Linux and Windows governance contracts,
  exact-head Validator review and a real downstream protected failure capture.

## [0.13.1] - 2026-08-08

### Review-compatible managed Python

- Refactored the managed governance validator and Decision DSL parser into
  smaller behavior-preserving helpers, keeping every touched or extracted
  function at cyclomatic complexity 15 or below.
- Preserved classification, package, adoption-lock, managed-hash and Decision
  DSL diagnostics and public behavior, with additional exact parser-diagnostic
  regression coverage.
- Passed the full Linux and Windows governance contracts, exact-head Validator
  review and the pinned downstream Vallm 0.1.94 deterministic scan without
  suppressing paths or increasing review thresholds.
- Kept the v0.13.0 provenance-bound atomic-adoption contract unchanged; this
  patch release only makes its managed Python payload review-compatible for
  downstream exact-SHA adoption.

## [0.13.0] - 2026-08-08

### Provenance-bound atomic standard adoption

- Added the optional intent/v3 `delivery.standardAdoption` contract, binding
  one upgrade to `wellmanifest/new-project` and distinct full source revision
  SHAs.
- Deterministically account for a complete, hash-bound `managed` payload as an
  atomic standard transaction, including new managed targets that are absent
  at the approved base.
- Keep the seed manifest, adoption lock, changelog and every other target-local
  path under the ordinary active-ticket, scope, workstream, delivery-budget and
  protected exact-head approval gates.
- Fail closed with `GOV-SYNC-001` when base/head locks, package strategies,
  source revisions or content hashes are inconsistent.
- Added positive multi-workstream upgrade coverage and negative hash, revision,
  seed-budget, unlisted-path and missing-approval regressions, plus the Goal
  adoption trust-boundary documentation.

## [0.12.0] - 2026-08-08

### Root governance contracts

- Assigned the exact root paths `CHANGELOG.md` and `.env.example` to the
  default `governance` workstream, making release evidence and the reviewed,
  non-secret environment surface explicitly publishable.
- Added positive fixtures proving governance tickets may change either path
  and negative fixtures requiring `GOV-WORKSTREAM-003` when another
  workstream claims them.
- Extended immutable-adoption coverage to verify that freshly seeded target
  manifests contain both ownership declarations.
- Preserved customized target manifests as explicit reviewed adoption
  decisions; the standard does not silently overwrite target-specific
  workstream maps.

## [0.11.0] - 2026-08-05

### Canonical work classification

- Added a versioned, schema-validated DSL with independent `kind`, `priority`
  and `origin` axes and deterministic
  `dependencies -> kind -> priority -> stableId` ordering.
- Standardized ready-work kind order as `BUG`, `FEATURE`, `SERVICE`, while
  preserving `P0` through `P3` as an independent urgency axis.
- Classified baseline-to-head complexity increases and new threshold crossings
  as `BUG/regression`, and pre-existing non-increased debt as
  `SERVICE/health`; LLM classification remains advisory.

### Release operations

- Added a fail-closed publication and rollback runbook requiring exact-head
  approval, a clean checkout of the merge commit, an immutable tag, a GitHub
  Release and full-SHA downstream adoption.

### Trusted Validator App approvals

- Hardened external approval evidence reads with a no-follow regular-file
  boundary, and stopped invalid binding/authority evidence before it can be
  projected into the trusted approval gate.
- Added a versioned approval-evidence contract binding merge authority to the
  repository, pull request, current HEAD, active ticket and actor.
- Added a separate `trusted-validator-apps` allowlist and accepted only exact
  current-head reviews from configured GitHub App bot logins; arbitrary Bot
  reviews remain untrusted.
- Required signed attestations to be signature- and issuer-verified by a
  protected resolver before ephemeral evidence is created outside the PR
  checkout.
- Added deterministic approval binding/authority diagnostics and positive and
  negative regression fixtures.
- Documented direct `validate-pr` migration for `validator-agent` and
  `todo2code`, using `openrouter/z-ai/glm-5.2` as the advisory Validator model.

## [0.10.0] - 2026-08-04

### Canonical lifecycle and bounded delivery

- Reconciled the two divergent contracts previously identified as `0.9.0`:
  queue-safe lifecycle and immutable adoption from `main`, plus bounded
  delivery schemas and deterministic validation from the delivery branch.
- Kept `IN_PROGRESS` as the only status reserving a workstream and scope;
  `BACKLOG`, `PLAN` and `BLOCKED` remain validated but do not participate in
  active conflict, dependency, ownership or overlap checks.
- Added architecture-first `XS|S` slices, a 30-minute ceiling, a 25-minute
  checkpoint, explicit file/component/interface/dependency budgets and
  fail-closed base-SHA validation.
- Preserved published-full-SHA lock provenance and the drift-safe adoption
  generator. Existing targets change only through explicit reviewed upgrade.
- Retained the bounded-complexity validator refactor and wildcard ownership
  regression while adding fixtures for all three non-active lifecycle states.
- Documented exact-SHA migration and rollback. LLM selection remains outside
  deterministic governance and cannot approve or block the contract by itself.

## [0.9.0] - 2026-08-04

### Queue-safe governance and reviewer authority

- Made `IN_PROGRESS` the only status that reserves a workstream and write
  scope; `BACKLOG`, `PLAN` and `BLOCKED` preserve work without deadlocking the
  implementation queue.
- Added `GOV-STATUS-001` so missing or misspelled statuses fail closed instead
  of silently behaving like an unreserved ticket.
- Updated the ticket scaffolder and regression fixtures to prove that blocked
  or deferred work releases its reservation while active overlap still fails.
- Required reusable-workflow callers to provide explicit `trusted-reviewers`;
  current-head approval from an arbitrary non-author no longer becomes trusted
  governance evidence.
- Documented that final adoption requires a published immutable
  `sourceRevision`; an uncommitted digest lock is integrity evidence, not
  reproducible publication provenance.
- Added a Draft 2020-12 lock schema and made the validator reject null,
  uncommitted, version-mismatched or otherwise non-reproducible lock provenance.
- Added `scripts/create_adoption_lock.py`, which copies managed artifacts from
  a full Git commit SHA, preserves a version-matched target manifest, refuses
  unreviewed drift and atomically emits a published lock. CI exercises initial
  adoption, reviewed upgrade, invalid revisions and mismatch rollback.
- Added a post-0.9.0 roadmap covering release publication, controlled pilots,
  cross-platform hardening, rollback operations and evidence required before
  broader adoption.

## [0.8.0] - 2026-08-01

### Concurrent workstream governance

- Added named workstreams with owned paths, a per-workstream active-ticket
  limit and deterministic rejection of overlapping active write scopes.
- Added intent v2 dependency, conflict and integration-routing fields while
  retaining read compatibility for archived intent v1 records.
- Added stable diagnostics for unknown workstreams, ambiguous ticket routing,
  dependency cycles/unmet prerequisites, active conflicts and shared-contract
  changes without an integration ticket.
- Added an explicit `WAIT_FOR_APPROVAL` state and made `--workstream` mandatory
  so newly scaffolded tickets are valid before implementation begins.
- Formalized the DSL legend, operator semantics, state-transition meaning and
  the non-authoritative role of Git history for agents reading the policies.
- Made diff discovery fail closed, rejected unsafe manifest/intent paths and
  detected planned glob ownership/overlap before concrete files exist.
- Bound GitHub review evidence to the current PR head and enforced full commit
  SHAs plus 64-character analysis-image digests on both supported entry points.
- Documented manager/developer/two-agent separation of duties, isolated
  branches/worktrees and merge-queue enforcement.

## [0.7.0] - 2026-08-01

### Enforced policy-as-code

- Added a versioned governance manifest/schema, machine-readable ticket intent,
  stack profiles and a stable `GOV-*` diagnostic catalog.
- Added a dependency-light deterministic validator with text, JSON and SARIF
  output plus positive and negative transition fixtures.
- Added a reusable GitHub workflow that checks independent review approval,
  active-ticket identity, diff scope, ownership and manifest integrity.
- Changed `project.sh`/`project.bat` into fail-closed governance entry points;
  optional analysis tools now require an explicitly digest-pinned Docker image
  and are never installed as unpinned latest packages on the host.
- Documented required Rulesets/CODEOWNERS and kept LLM findings advisory rather
  than part of the required merge decision.

## [0.6.0] - 2026-07-31

### Hardened ticket ownership and namespace

- Moved the generated ticket index to `project/TICKETS.md`, preserving any
  analysis-owned `project/README.md`.
- Made `new-ticket.sh` fail closed when an unfinished ticket exists and added
  validated agent IDs, complete ticket/agent scaffolding and safe template
  rendering.
- Stopped automatic human-file generation. Human intent must come from its
  owner or a trusted intake boundary; unresolved routes use explicit role
  sentinels.
- Added role-specific participant templates with typed metadata and prohibited
  executable implementation under ticket directories.
- Removed machine-local documentation links and added an isolated regression
  test for scaffolding, indexing, traversal protection and active-ticket reuse.

## [0.5.0] - 2026-07-30

### Added & Updated (Etap 4 Completed)
- **Mandatory Target Architecture Diagrams (`P-DOCS-001` & `C-DOCS-001`)**: Added rules requiring AI agents to generate visual Mermaid architecture & logic flow diagrams under `docs/` in all target repositories (e.g. `docs/ARCHITECTURE.md`, `docs/LOGIC_FLOW.md`).
- **TODO Roadmap Overhaul**: Refactored `TODO.md` with clean, precise descriptions for all 4 completed stages.
- **Version Bump**: Bumped `VERSION` to `0.5.0`.

## [0.4.0] - 2026-07-30

### Added & Updated (Etap 3 Completed)
- **Technical Directive Template `preprompt.template.md`**: Created `template/files/preprompt.template.md` establishing standardized ticket preprompt layouts for technical constraints, linked resources, and execution directives.
- **Scaffolder Integration**: Updated `project/new-ticket.sh` to use `template/files/preprompt.template.md` when generating `project/ticket-{NNN}/preprompt.md`.
- **Template Indexing**: Updated `template/files/README.md` to index `preprompt.template.md`.

## [0.3.0] - 2026-07-30

### Added & Updated (Etap 2 Completed)
- **Universal Ticket Automation Scripts**: Added `project/new-ticket.sh` (POSIX script for scaffolding tickets with `preprompt.md` and `changelog.md`) and `project/readme.sh` (POSIX script for generating `project/README.md` master menu index).
- **Template Standards**: Created `template/files/project.template.md` adhering to `*.template.md` naming standards. Updated Polish documentation in `template/files/README.md` and `template/projects/README.md`.
- **DSL Procedural Rule `C-TOOLS-006`**: Added rule in `CONTRIBUTING.md` requiring AI agents to copy existing shell scripts from Governance Hub during target repository bootstrap instead of regenerating them.
- **Active Ticket Reuse Rule `P-CORE-009` / `C-TICKET-008`**: Added rules prohibiting spawning multiple tickets for follow-up prompts and forbidding AI edits to human participant files.
