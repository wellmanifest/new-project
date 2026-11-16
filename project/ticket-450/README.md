# Ticket 450: Wire optional legacy retirement regressions into required CI

- **ID**: ticket-450
- **Owner**: agent:codex
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Created**: 2026-11-16
- **maxActiveMinutes**: 30

SESSION_EXECUTION_AUTHORIZATION: the user requested continuation of verification,
repairs, overdue work and protected merging. This disjoint workflow repair is
required to complete the legacy terminal adapter's declared validation.

## Scope

Add the explicit required invocation missing from the adapter's separate source
scope. The workflow must require and run the regression whenever the adapter
exists. The pre-adapter baseline remains valid. Preserve the existing mandatory
suite-wiring assertion and all Linux, Windows and OneDev gates.

## Acceptance criteria

- [x] AC-01: Actual workflow command succeeds with no adapter, runs the 17
  regressions when present, and refuses an adapter with no regression file.
- [ ] AC-02: Governance, fresh exact-head/base required CI and independent
  protected publication pass.

No runtime dependency, lease, owner, required-check or publication-authority
change. Raw execution evidence remains outside the repository.

Local validation: the actual workflow command passed with the adapter absent,
ran 17 regressions with it present, and refused a missing regression file.
The complete suite-wiring assertion and deterministic governance passed.
