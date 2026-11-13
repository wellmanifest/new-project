# Ticket 431: use canonical repository URI in local allocation leases

- **ID**: ticket-431
- **Owner**: agent:codex
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Created**: 2026-11-13

## Goal and scope

SESSION_EXECUTION_AUTHORIZATION: continue the user-requested repair and protected
publication. The local allocator currently writes the primary checkout basename
(`new-project`) to `repositoryRef`, but the canonical lease schema requires an
`owner/repository` slug. Normalize the origin to that slug for lease identity,
while retaining a separate local label for Worktrees path planning. Without an
origin, use the canonical clone-local `local/<sha256>` reference. Test this in
the isolated allocator fixture; do not mutate historical leases.

## Acceptance criteria

- [x] AC-01: origin-backed lease uses `owner/repository`; layout planning uses the separate checkout label
- [x] AC-02: no-origin allocation uses canonical `local/<sha256>` and generated leases pass canonical validation
- [x] AC-03: all 36 allocation-worktree tests and canonical governance pass; PR publication remains pending.

CI compatibility: legacy fixtures without the allocation helper retain their
prior clone-local hash fallback; origin-backed allocations use the canonical
owner/repository slug when the pinned helper is available.

## Validation evidence

`python3 tests/ticket-allocation-worktree.test.py` under Wellman: 36 tests
passed. `bash project/governance-check.sh`: GOV-PASS (0 errors, 0 warnings).
Bash syntax, Python compilation and `git diff --check` pass. Fixture warnings
about unbound required-checks are expected for no-origin fixtures; generated
leases validate.

## Tracking boundary

This directory contains the minimal reviewed intent. Optional participant prose
and raw command logs are not required delivery output.

## Accepted continuation and publication prerequisite

The managed idle-takeover controller assigned this existing checkout to
`agent:codex` / `codex-ecosystem-20261113-1450`, revision 4 and fence 4, on
2026-11-13. The user again requested continuation, testing and protected merge.
CONTRIBUTING C-APPROVAL-003 retains that execution authorization for this safe
prerequisite; this prose grants no independent approval.

The protected publisher refused the otherwise green HEAD because the registry
requires `onedev/local-verify`, `test` and `windows-governance`, while the source
declares only the latter two. Extend the bounded intent to reconcile that
declaration and validate the existing OneDev producer explicitly. Preserve both
hosted jobs and every protected requirement. A declaration never supplies an
execution result, and no synthetic workflow job or status is introduced.

- [x] AC-04: The source declares all three required contexts; unknown,
  duplicated, undeclared or provider-mismatched external checks and omitted
  hosted jobs are rejected. The bundled checker stays synchronized.

The scope rationale is recorded in [scope-decision.md](scope-decision.md).
The initial public-CLI regression run failed eight assertions on the original
checker. The corrected checker passes all 17 new methods, the 10 repository
binding methods and 26 reusable-workflow methods. The complete governance gate
passes with zero errors and warnings. The allocation rerun passes all 36 methods
(371.295 seconds), giving 89 distinct methods across these four selected suites.
The real Testless scan repeats the 17 new methods and measures 47 passing
subtests; these overlap the selected suites and are not an additional 17 methods.
Its first attempt lacked pytest-cov and is retained as incomplete. Only this
checkout's ignored development environment received pytest-cov 7.1.0 and coverage
7.16.2; package compatibility and both bundled helper copies pass. Generated
Testless plans are advisory and are not applied. New-head protected checks and
independent approval remain required.

Fresh hosted CI correctly refused the first head because the closed JSON
schema did not yet admit `externalChecks`. The follow-up adds the same closed
producer contract to that schema and two schema regressions. The original
failed CI is retained; the complete required-check shell suite and fresh CI
must validate the resulting head before publication.

<!-- ticket-radar:start -->
## Ticket Radar

Initial planned-scope estimate; advisory only, not execution or merge approval.

| Measure | Initial assessment |
| --- | --- |
| Impact score | 48/100 |
| Complexity | M |
| Estimated effort | 47 min |
| Planning budget | 30 min |
| Split recommended | yes |

Diagnostics: RADAR-ACCEPTANCE-MISSING, RADAR-BUDGET-EXCEEDED.
<!-- ticket-radar:end -->
