# Ticket 384: Exact primary target aliases

- **ID**: ticket-384
- **Owner**: agent:codex
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION

SESSION_EXECUTION_AUTHORIZATION: continue PLF-20321 and existing new-project#473 adoption prerequisite, implementing bounded technical admission repairs and requesting independent publication.

A named primary checkout can already identify the exact target commit while the allocator and adoption exporter reject only its branch name. Admit this case only when HEAD, local target and observed origin target are identical. Preserve branch identity, dirty files and index; retain native ownership, WIP, published-package and lease checks. Re-observe at the identity boundary before reserving a ticket. Detached, missing, divergent or changed observations remain refused.

Six implementation files, two components, one existing schema field refinement, no dependency; S/25 minutes. No release/adoption execution or primary cleanup. Native allocation: canonical worktree, own actor/session, revision1/fence1. Independent Validator alone approves and merges.

- [x] AC-01: Native allocation admits exact alias, preserves dirty primary, and refuses divergent/detached/missing/racing targets before reservation.
- [x] AC-02: Adoption plan and verification admit only an exact alias, preserve source/target evidence, and refuse changed refs/branch/metadata.
- [ ] AC-03: Affected tests, governance, required Linux/Windows CI and independent exact-head merge pass.

## Validation and publication

The new exact-alias regression failed on the original allocator. All 24 native allocation tests and 21 adoption tests passed, including the published-plan path, dirty primary/index preservation, missing/divergent/detached state and a target change before reservation. Ruff and Bash syntax checks pass; native governance has zero errors/warnings. Required exact-head Linux/Windows CI and independent Validator publication remain pending.

Read-only checks on actual dependents confirmed the bounded distinction: an exact named alias is admissible for target observation, while a behind target is refused. This is no adopter execution or write authority. The source patch requires a final published package before downstream adoption.
