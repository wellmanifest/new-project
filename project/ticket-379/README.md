# Ticket 379: Require the writer checker before ticket writes

- **ID**: ticket-379
- **Owner**: agent:codex
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION

## Goal and authorization

SESSION_EXECUTION_AUTHORIZATION: the user explicitly requests continuing the wellmanifest/new-project backlog, testing and protected delivery. This bounded slice resolves finding3 in issue534. Existing source373 has independently merged through PR531; its terminal receipt is recorded. No other source ticket is taken over.

The current hub and adopted hooks silently skip writer verification if both checker locations are missing. Make that prerequisite fail closed for ticket refs. Preserve the existing managed-to-hub lookup and normal source writer fencing; do not implement a second lease checker.

## Acceptance criteria

- [x] AC-01: Missing checker prevents real commit/amend attempts with a stable GOV-CHANGE-LEASE diagnostic and unchanged HEAD, for both hook variants.
- [x] AC-02: Missing checker prevents real ticket pushes with unchanged remote refs.
- [x] AC-03: Existing valid writer/session and hub fallback paths work, while other-session, force-push and target-push restrictions remain enforced.
- [ ] AC-04: Focused tests, required native full suite and canonical governance pass, followed by independent exact-head/base protected publication.

## Bounded plan

S, estimated25minutes, maximum30active minutes: four hook projections, the existing real-Git pre-push fixture suite and its required four-digit allocator fixture, two components, no dependencies/public interfaces. Allocator lease allocation-ticket-379-require-writer-checker, owner agent:codex/session codex-newproject-534-hooks-20261024, revision1/fence1. Accepted base b923f8972149208d9ec087f22c9c014e0230b94d. Read-only managed work-start admitted this exact free scope; no idle takeover was performed.

Parser/default and IR findings belong to the independently pinned wellmanifest/policy-dsl producer before hub adoption; seed-baseline and S4/S5 evidence decisions remain separate issue534 work. This slice does not close all of issue534 or publish a release tag.

<!-- ticket-radar:start -->
## Ticket Radar

Initial planned-scope estimate; advisory only, not execution or merge approval.

| Measure | Initial assessment |
| --- | --- |
| Impact score | 60/100 |
| Complexity | L |
| Estimated effort | 64 min |
| Planning budget | 30 min |
| Split recommended | yes |

Diagnostics: RADAR-ACCEPTANCE-MISSING, RADAR-BUDGET-EXCEEDED.
<!-- ticket-radar:end -->

## Validation and publication

Baseline: two real-Git regressions failed because a missing checker allowed a commit and push; the real hub-checker fallback control passed. Corrected full pre-push suite:12tests PASS. Managed host integration suite PASS, including all12pre-push checks. Canonical governance PASS with0errors/0warnings; diff whitespace check PASS. Python tests used the approved full Wellman runtime with explicit same-repository primary venv reuse. Its selected execution profile supports Python/pytest; the separately declared native Bash suites ran through the canonical repository scripts with that same project venv, without claiming universal shell mediation.

The generated Ticket Radar section records the initial scaffold assessment before these acceptance criteria were completed; it is advisory. The accepted source delta is one prerequisite check in four maintained hook projections plus three real-Git regressions in one existing test file, six implementation files/two components/no dependencies or public interfaces. Current native exact-head/base CI and independent protected review/merge remain pending; no full-stack PASS or release deployment is claimed yet.

## Required fixture refinement after full CI

Hosted run40100321879 rejected the existing four-digit allocation fixture at its final commit: it copied the new hook but omitted the writer checker entirely. Within the user's existing bug534 authorization, the bounded intent now includes tests/governance-scripts.test.sh (six implementation files, same two components, estimated25minutes). The fixture will use the actual managed checker/schema and explicit writer identity returned by its own allocator; no checker stub or control waiver. The original source lease owner/session/revision/fence remain unchanged; no lease or workstream ownership is rewritten. Re-observe the expanded test path through managed admission before changing it. The published cbb52e37 remains in branch history; the corrected head must receive fresh full native and hosted checks and independent review.

The refined fixture scope was re-observed with managed work-start: REUSE_EXISTING, no blockers, same writer/session/fence. Its exact four-digit allocation block now passes independently, including the actual writer check (GOV-CHANGE-LEASE-PASS). The complete local governance-scripts rerun is still running at this publication boundary; fresh full native/hosted checks on the corrected head remain mandatory.
