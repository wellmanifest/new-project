---
participant-id: agent:codex
participant: codex
role: agent
ticket: ticket-042
---
# Participant: codex (AI agent)

## Understanding

Downstream todo2code adopted v0.13.1 correctly, but protected governance failed
before ticket resolution because the REST repository response available to the
workflow omitted `delete_branch_on_merge`. JavaScript consequently serialized
no `deleteBranchOnMerge` property. The repository setting is independently
verified as `true`; the failure is evidence acquisition, not policy state.

## Proposed change

Use the typed GraphQL `Repository.deleteBranchOnMerge` field in the protected
workflow snapshot acquisition. Retain REST metadata for `default_branch`, the
strict offline validator, and all branch/PR enumeration behavior. Extend the
static lifecycle regression to require the GraphQL field and prohibit reliance
on `repository.data.delete_branch_on_merge`.

## Execution plan after approval

1. Transition ticket-042 to `IN_PROGRESS / EDIT` in its isolated worktree.
2. Update `.github/workflows/governance.yml` to acquire the typed boolean.
3. Extend `tests/branch-lifecycle.test.sh` with the workflow regression.
4. Run governance, focused suites, full Linux contract and Docker checks.
5. Publish a protected PR and require exact-head Koru and Validator approval.
6. After merge, create a separate release ticket for immutable v0.13.2 and
   resume todo2code ticket-050 against that exact release SHA.

## Actual changes

- The user explicitly approved implementation on 2026-08-08.
- Diagit audited the local fleet and both relevant GitHub organizations. Its
  clean committed runtime confirmed the active ticket branches and PR #70.
- The ticket transitioned to `IN_PROGRESS / EDIT`; workflow implementation is
  now authorized within `intent.json`.
- Implemented typed GraphQL acquisition at `7f836f055976887a8701e635efa9747ab43acfb8`.
  The strict snapshot schema and offline validator are unchanged. The focused
  regression and full Linux CI command contract pass, so the ticket is in
  `VALIDATION` pending protected Linux/Windows and exact-head review.
- PR #62 passed protected Linux and Windows checks. Trusted Validator App
  approved exact head `2a0001a7ddde314d3af5a7d23553869d01f70bb6`, which merged as
  `main@b01cae0f47bb311d1e795600af49e0ba436e175d`.

## Blockers

- None. Release v0.13.2 points to `85631ea24d127f1f4797d2a67f3524a63cbbc95a`.
  Downstream todo2code PR #70 passed protected governance on exact head
  `fee491aac475ecbe6ce843d5fdbba25471c1db0e`, merged as `f60d3cc`, and its
  ticket-050 closure reached main at `11dff0d`. Ticket-042 is `DONE / DONE`.
