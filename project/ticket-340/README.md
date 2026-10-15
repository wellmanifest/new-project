# Ticket 340: Bootstrap prerequisite ownership

- **Owner**: codex
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION

## Session authority

SESSION_EXECUTION_AUTHORIZATION: continue repairing and independently publishing Wellmanifest adoption across maskservice repositories. Real Fleet bootstrap failed on default ownership for `.gitattributes`, `.github/workflows/new-project-branch-hygiene.yml` and its exact local-build Compose prerequisite. The installer-owned primary delta was captured and restored exactly; no native ticket was allocated in Fleet.

## Outcome and boundaries

Publish 0.20.99 with ownership of installed standard artifacts and an explicit external prerequisite ownership plan. Bind it to the current committed base and exact file hashes; admit only existing unowned regular files, preserve existing component ownership, and revalidate immediately before writes. A plan grants neither writer nor publication authority.

## Acceptance criteria

- AC-01: Complete package scope plus exact prerequisite passes real first allocation for fresh and legacy-scaffold fixtures. Wrong base, hashes, dirty files, existing ownership, unsafe paths, symlinks, plan tampering, late mutation and implicit ordinary-upgrade use fail closed. Target prerequisite bytes stay unchanged by the adopter.
- AC-02: Managed governance and focused tests pass. Source, version projections and tests publish atomically through OneDev and the independent Validator; annotated tag and release follow authenticated merge.

## Evidence

- Focused suite: 46 tests and 80 subtests passed in 46.76 seconds.
- Final Testless affected scan: six tests passed in 15.06 seconds, including genuine first allocation over the entire package scope for fresh and legacy-scaffold targets, and prerequisite/plan mutation immediately before writes. Publication lookup is mocked only in bounded synthetic fixtures.
- The complete-scope regression exposed the two missing default owners; no scope restriction or receipt digest was bypassed.
- The adopter leaves prerequisite bytes unchanged and extends only the selected target manifest ownership. Package targets, duplicate/unsafe paths, existing ownership, dirty recomputed hashes, wrong base and symlinks remain rejected.
- Managed governance passes with the hub's S class and existing budgets. No policy budget was increased.
- Publication through OneDev and the independent Validator is pending.
