# Ticket 272: Resolve reusable target-root version and publish standard 0.20.51

- **ID**: ticket-272
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: VALIDATION
- **Utworzono**: 2026-09-24

## Outcome

The reusable governance workflow currently reads `pyproject.toml` at the checkout root when installing Wellman, even when `target-root` selects another governed component. Read the standard identity and version from `target-root/.governance/manifest.json`, reject an invalid identity/version, and install Wellman from the canonical `v<version>` standard release tag. Release this material correction together with the merged exact PR-range fix as immutable standard `0.20.51`, so Paxlet can adopt a published revision.

## Acceptance criteria

- [x] AC-01: Nested target-root selects its manifest version and wrong identity fails closed in an actual workflow-shell regression.
- [x] AC-02: Wellman package, required checks, governance gate and diff checks pass on the ticket HEAD.
- [ ] AC-03: Protected exact-head PR validation/Validator merge, clean merged-SHA retest, and immutable `v0.20.51` GitHub release complete.

## Authorization and ownership

SESSION_EXECUTION_AUTHORIZATION: the user requested continued implementation, testing, protected merge and publication. On 2026-09-24 the user explicitly approved one additional disjoint release ticket despite the hub WIP limit: “Tak — jeden rozłączny ticket wydaniowy”. The one-shot process-local admission exception is recorded at `receipt:release-02051.authorization`; the tracked WIP limit remains 1. Ticket-270 and its owner are preserved. No approval or CI gate is waived.

## Risk and delivery

The release must bind the tested merged SHA. A checkout-level `pyproject.toml` is not authoritative for a nested `target-root`. Changes to ticket-270, its reserved paths, or permanent WIP policy are outside scope. Publication follows independent exact-head review and managed Goal delivery.

## Validation

The freshly built 0.20.51 Wellman wheel passed the installed-runtime suite, including seven detached PR/workflow cases, the nested target-root identity rejection, and the canonical runtime source tag. Required-checks regressions, the managed governance gate, and `git diff --check` passed. AC-03 remains pending protected exact-head review, merge, clean merged-SHA retest, and immutable release.
