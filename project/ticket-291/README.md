# Block unsupported file deletions in remediation analysis

- **Status**: IN_PROGRESS
- **Workflow state**: EDIT

## Goal and scope
The closed remediation DSL has no file-deletion operation. Treat every relevant producer delete proposal as a blocking advisory finding, even when an IMPLEMENT action on that path has destructive risk and explicit-human metadata. Preserve valid modify plans and ignore unrelated historical plans.

## Acceptance criteria
- AC-01: Complete synthetic producer plans reproduce the original defect, and deletion/advisory/isolation regressions pass after correction.
- AC-02: Existing governance integration, bundled parity, native gate and required exact-head CI pass.
- AC-03: Independent protected merge and final immutable standard v0.20.65 publication are verified.

## Risks and limits
S / 25 minutes, nine implementation files, three components, one CI workflow interface, no new dependencies. Source and test fixtures remain repository-local; target incident data and raw logs remain external. No deletion operation, invented producer field or execution authority is introduced.
