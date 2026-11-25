# ticket-476: Support owner-reviewed first native allocation when the root .gitignore excludes .subactor/.

- **ID**: ticket-476
- **Owner**: agent:coding-agent
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION

## Goal and scope

Extend the owner-reviewed bootstrap ignore plan so the two managed root .subactor files become trackable and the existing first ticket allocation can proceed.

SESSION_EXECUTION_AUTHORIZATION: validated native ticket PLF-30155; Willman request 7df59922-4e01-49bb-aa9b-1df614bb5f9f; protected publication only.

## Acceptance criteria

- [x] AC-01: Use a real Git fixture with a committed .gitignore containing the literal .subactor/ rule and an existing root .subactor directory. Preserve every original ignore byte and verify that only .subactor/.gitignore and .subactor/manifest.json become trackable.
- [x] AC-02: Verify that recovery files, leases, caches, the bootstrap receipt, unknown new children and a nested project's .subactor/manifest.json stay ignored. Verify that existing operational files retain their bytes.
- [x] AC-03: Refuse stale HEAD, a mismatched ignore digest, uncommitted root ignore edits, symlinked inputs or destinations, arbitrary or incomplete leaf lists and unrelated excluded parents. Preserve the existing pre-write recheck and ordinary leaf-plan behavior.
- [x] AC-04: Run --bootstrap-native-adoption --bootstrap-ignore-plan with --check before fixture mutation, then apply the same reviewed plan with --upgrade. Verify the receipt and allocate the first canonical ticket at the original base through the existing allocator using the exact dirty digest. Document the commands and the existing owner, lease and independent publication requirements.

## Evidence

- All 21 tests in `tests/bootstrap_ignore_plan_test.py` passed with Git 2.51.0. The temporary fixtures ran under this checkout's ignored `.subactor/recovery/` because the primary recovery directory is read-only in the model session.
- The fixture verified read-only preflight, the projected ignore bytes, the installed lock and receipt, and first canonical allocation at the original base. The existing admission check refused an omitted or mismatched dirty digest and admitted the exact acknowledged digest. The resulting allocation lease bound the fixture actor, session, branch, worktree and base. The fixture stubbed external release verification.
- The parent exception requires case-sensitive Git matching. A Git probe showed that `core.ignoreCase=true` would also expose `.subactor/MANIFEST.JSON`. The focused suite verifies refusal in that configuration.
- Both documented Bash blocks passed `bash -n`. The owner-reviewed procedure is in [STANDARD_UPGRADE.md](../../docs/STANDARD_UPGRADE.md#first-native-allocation-with-a-committed-subactor-rule).

## Runner handoff

- Planfile request `PLF-30155` and admitted GitHub issue `wellmanifest/new-project#663` bind this work to `ticket-476`.
- Accepted base and checkout HEAD are `270858a006b50bf70c4e3166de05ddba08df94f9`. Branch `ticket/476-project-job-7df59922` is checked out at `.worktrees/ticket-476--project-job-7df59922`.
- The claimed lease observed for this worktree has revision 1 and fencing token 1. Its owner session is `coding-agent-PLF-30155-7df59922-4e01-49bb-aa9b-1df614bb5f9f` and its pull request field is empty.
- The trusted runner owns the repository gates and exact guarded publication. The implementation is ready for those gates.
