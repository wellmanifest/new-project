# Ticket 431: use canonical repository URI in local allocation leases

- **ID**: ticket-431
- **Owner**: agent:opencode
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
