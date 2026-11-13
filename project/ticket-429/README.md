# Ticket 429: Preserve continuity history with explicit repository namespaces

- **ID**: ticket-429
- **Owner**: agent:codex
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Created**: 2026-11-12

## Goal and authorization

SESSION_EXECUTION_AUTHORIZATION: user requested continued implementation and
protected merges. Standard request NP-047 / #604 supplies the missing reusable
capability requested by consumer heyasa/heyasa#592. Native allocation claims
codex-np-continuity-20261112t1006-4c37a9b2, revision1/fence1; writer-check passed.
Allocation alone grants no authority. Complete the mandatory delivery metadata
within the already allocated path scope; do not alter the lease projection.

Source session starts 10:04:13 UTC and ends 10:34:13 UTC under the manifest
30-minute maximum. Freeze the published source head for independent validation.
No consumer activation or old journal migration is authorized by this source PR.

## Acceptance criteria

- [x] AC-01: Default changed-origin behavior stays conservative; an explicit
  digest-bound initialization selects an isolated repository namespace. Actual
  capture, resolve, replay and verify work without changing legacy history.
- [x] AC-02: Invalid bindings, incomplete chains, links, occupied stores,
  concurrent initialization and publication failures preserve existing bytes.
  No namespace or checkpoint grants execution, lease or merge authority.
- [ ] AC-03: Package closure, documentation/index, version0.20.148 and required
  governance/regressions pass, followed by independent exact-head publication.

## Validation boundary

Use temporary Git fixtures only. Retain bounded source checkpoints and raw
logs in ignored recovery/receipt storage. The source change does not resolve
consumer enrollment or authorize any target journal migration or deployment.

## Checkpoint and publication blocker

The two new CLI cases fail on the accepted base. Candidate validation passes
12 namespace tests, the 32-case storage suite (4 platform skips), the complete
continuity shell suite, 3 local-pin tests, version parity, bundle parity,
Docs validation and governance (zero errors/warnings).

The required Goal source-hub preflight stops at adoption-lock.test.sh after
its 300-second limit. A separate project-bound 90-second trace preserves the
specific fixture progress; it is not a passing required gate. Testless scanning
also exposes two existing storage process-coordination timeouts under coverage
(38 passed, 4 skipped, 31 subtests); ordinary execution of that suite passes.
Neither failed path is waived or represented as green. No commit or push exists.

Stop source edits at the original 10:34:13 UTC boundary. Preserve the exact
secret-scanned snapshot and current lease1/fence1; do not renew or take over by
timeout. Next action is a declared bounded verification/publication handoff,
or a governed fix for the actual test environment/budget, followed by the same
required checks and independent current-head approval. Consumer #592 remains
pending source publication and qualified adoption. No source-stage budget reset.

## Accepted verification/publication handoff

The actual current owner explicitly stopped the first stage and handed off its
exact snapshot. The declared native controller observed the stopped checkout,
applied CAS transitions and issued session
`codex-np429-validation-publication-20261112t1046-6b48a091`, revision4/fence4,
at 10:49:16 UTC. Fresh work-start and writer-check pass. This separate stage
ends 11:19:16 UTC, allows zero implementation edits and one full verification
attempt, and has no further extension. Total lifetime is bounded at 13:04:13 UTC.

Record the frozen source through ordinary local hooks. Remote publication must
run Goal -a with the complete canonical health contract; the unchanged published
Goal SDK supports an explicit 600-second per-check verification budget, bounded
at 1200 seconds overall in this stage. A real complete PASS may populate its
native cache; never manufacture a cache or remove checks. Protected OneDev,
Linux, Windows and independent current-head approval remain required.

## Verification-stage result

The admitted stage recorded the frozen implementation as local commit
`ad324f2ea3ad93ff7e78b04af7da1028478f17ca`. Its one complete canonical
verification attempt returned124 at adoption-lock.test.sh after600 seconds;
only1 of23 checks completed and no success cache was created. No remote branch,
PR, approval, merge or consumer activation was produced. Stop this stage after
the failed attempt; no further extension or implementation edit is permitted.

The private process observation locates the long wait in the existing
adoption_legacy_scaffold fixture/updater, including filesystem journal waits.
Host load reached about50 on16 CPUs and I/O PSI showed substantial stalls.
These are observations, not proof that the candidate caused the slowdown.
Retain the paired baseline/candidate diagnostic and request qualified bounded
verification at the Goal/test-fixture owner. Do not hide the failure with an
invented cache, a check waiver or an unbounded timeout.

## Qualified publication continuation after resolved prerequisites

SESSION_EXECUTION_AUTHORIZATION: the continued implementation/merge request
retains this existing material source delivery. Published Goal d249e40c has
qualified immutable installed bytes and protected-ci preparation; independently
merged new-project606/607 now provide canonical external-check declarations,
lease identity and decomposed mandatory source verification. Previous source
and failed verification stages remain stopped, without a fabricated PASS.

The native idle controller observed no live writer, preserved the dirty
historical README and granted session
`codex-ecosystem429-qualified-publication-20261113-2050`, revision7/fence7,
at20:51:06Z. This distinct continuation ends21:21:06Z without extension.
Integrate published verification base1ee8c7a and reconcile unpublished commit
metadata while preserving the frozen namespace implementation bytes. No new
namespace implementation or consumer activation is allowed. Qualified Goal-a
preparation leaves all full source Linux/Windows/OneDev checks and independent
exact-head approval mandatory in protected CI. Historical local health failures
and their unchanged limits remain evidence, not success caches.

## Authoritative base refresh during preparation

Goal correctly refused the frozen candidate after independent PR610 advanced
origin/main to b0a6c4eb. No push or PR was created by that attempt. The current
unfrozen native owner10 integrates this independently approved base, preserving
all13 namespace feature files. This is metadata/base reconciliation within the
existing21:51:06Z total continuation bound; no new implementation, timeout
waiver, source-stage extension or consumer activation is allowed. A fresh
exact-head controller binding and all required CI/review gates remain mandatory.
