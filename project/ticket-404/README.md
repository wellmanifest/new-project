# Ticket 404: Preserve bootstrap seeds and diagnose partial creation failures

- **ID**: ticket-404
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT

## Outcome

Resolve the grounded late-conflict finding from PR568: inspect every seed
leaf through pinned directory descriptors before creation. If a later race
or I/O failure interrupts creation, preserve and identify the partial paths,
keep concurrent bytes intact, and stop before managed writes or a receipt.
Publish standard0.20.134 through independent protected approval and merge.
PR568 was personally merged without approval;0.20.133 remains unreleased.

## Acceptance criteria

- AC-01: Early existing destination causes no creation, including no project directory.
- AC-02: A deterministic late concurrent VERSION is preserved; diagnostics identify prior seeds, managed files remain unchanged and no bootstrap receipt appears.
- AC-03: Genuine complete source checks and product tests pass; independent Validator assesses this repair before canonical release.

## Design and risk

Multi-file installation is not atomic under arbitrary concurrent mutation.
Do not unlink by pathname after an inode check: another owner can replace the
leaf before deletion. Preserve partial creation for explicit reconciliation.
The existing unknown-file preservation contract remains; no caller waiver of
semantic review is granted. Native ticket403/NP-024 owns disjoint checker paths.
Evidence: NP-025; primary ignored receipt bootstrap-conflicts-20261104.
