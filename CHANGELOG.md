# CHANGELOG

## [Unreleased]

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
