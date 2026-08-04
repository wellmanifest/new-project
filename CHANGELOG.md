# CHANGELOG

## [Unreleased]

### Trusted Validator App approvals

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
