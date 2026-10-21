# ticket-360: Close issue #495's remaining writer-fencing gap while preserving the allocator's existing canonical worktree creation and clean-primary behavior.

- **ID**: ticket-360
- **Owner**: agent:coding-agent
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION

## Goal and scope

Bind ticket allocation and local Git mutation checks to the same explicit writer session, rejecting cross-session amendments and pushes while retaining existing canonical worktree allocation.

SESSION_EXECUTION_AUTHORIZATION: validated native ticket PLF-19278; Willman request b8895d85-1126-4998-829c-d0ed56a66de2; protected publication only.

## Acceptance criteria

- [x] AC-01: AC-01: Allocation records explicit calling actor and session identity in the existing lease fields; missing or invalid identity fails before ticket reservation, scaffolding or worktree creation.
- [x] AC-02: AC-02: Hub and adopter pre-commit hooks reject another session's commit or amend on an owned ticket branch with a registered GOV diagnostic, including another session using the same agent provider.
- [x] AC-03: AC-03: Hub and adopter pre-push hooks check every pushed ticket ref and reject another writer's ordinary or forced push, including pushes initiated from a different checkout.
- [x] AC-04: AC-04: Missing, malformed, expired, released, frozen or mismatched lease evidence fails closed; timeout and a locally supplied handoff file never transfer ownership. A successor requires independently accepted handoff evidence and current controller fencing.
- [x] AC-05: AC-05: Successful allocation creates ticket scaffolds only in the existing canonical linked worktree and preserves the primary checkout's tracked and untracked state; refused allocation leaves no scaffold or identity reservation.
- [x] AC-06: AC-06: Existing lease, host-hook, direct-target-push and allocator regression suites pass, and the managed governance gate validates the bounded change.

## Retry checkpoint

PLF-19278 / issue #495; runner session b8895d85-1126-4998-829c-d0ed56a66de2.
Base and observed HEAD: `95a525d4523660e269eeb1c309590bfbf6a90fbd`.
Branch: `ticket/360-project-job-b8895d85`; canonical worktree:
`.worktrees/ticket-360--project-job-b8895d85`.
Observed allocator lease revision/fencing: 1/1; runner retains ownership.
Work-start: REUSE_EXISTING, no blockers, primary clean. No prior material edits
were present; the supplied SUBLLM-CODE-EDIT-FAILED diagnostic contains no
source-level cause. Retry uses direct bounded edits and focused regression tests.
Intent is immutable; acceptedBaseSha already equals the frozen base.
Next action: verify writer fencing and allocator fixtures, then return changes
to the runner for snapshot, authoritative gates and guarded publication.
No commit, branch mutation, network publication or review is authorized here.

## Focused verification and regression validation

- `python3 -B tests/ticket-allocation-worktree.test.py`: PASS, 20 tests.
- `python3 -B tests/change_lease_safety_test.py`: PASS, 15 tests.
- `bash tests/agent-hosts.test.sh`: PASS, including real commit hooks and 9-test pre-push suite.
- `tests/pre_push_hook_test.py`: PASS, 9 tests; ordinary/forced updates, non-fast-forward rewrites, deletions, multiple refs, profile exceptions.
- `python3 -B tests/work_start_test.py`: PASS, 96 tests.
- `bash tests/governance-scripts.test.sh`: PASS, including wide ticket counter verification.
- `git diff --check`, Python syntax, JSON parsing, bundled verifier parity: PASS.
- `./project/governance-check.sh`: GOV-PASS: passed (0 errors, 0 warnings).

All acceptance criteria AC-01 through AC-06 are satisfied.
Delivery ledger: scoped source changes and focused checks completed. Status remains IN_PROGRESS / PUBLICATION.

Immutable intent file SHA-256: `87f5c604daa95c41a2f5133686dc956d33da66b362c8a8c229e852122ae598d7`.
