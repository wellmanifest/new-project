# Ticket 335: Close reviewed governance runtime boundary gaps

- **ID**: ticket-335
- **Owner**: agent:codex
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION

## Goal and scope

SESSION_EXECUTION_AUTHORIZATION: the user authorized the source repairs found
while reviewing the Coding Agent adoption, and requested continued implementation,
tests and protected merges. This slice repairs three independently reproduced
source defects; immutable CI installer pinning remains the next authorized slice.

## Acceptance criteria

- [x] AC-01: Literal secrets assigned to attributes/subscripts and nested targets
  are detected; dynamic expressions stay accepted. Adapter glob self-ownership
  is refused. POSIX bat-only gate fails with a controlled governance diagnostic.
- [ ] AC-02: Package mirrors, 0.20.96 release projections, full tests and governance pass.
- [ ] AC-03: Exact-head independent review, protected merge and immutable release complete.

## Bounds

maxActiveMinutes: 30; checkpointMinutes: 25. Thirteen implementation/release files,
two components. Preserve foreign ticket-334 and recovery branches. No target
repository implementation, raw logs or user-owned ticket files are changed.

## Validation

Before the fix, all twelve literal-assignment module subcases failed; adapter
self-ownership by glob and the POSIX bat-only gate also failed their regressions.
After the fix: 12 secret detection tests, adapter policy suite, pytest lifecycle
suite and seven version-parity fixtures pass. Package mirrors match canonical
scripts; managed governance reports zero errors and warnings. Full Goal health,
complete pytest and independent exact-head publication remain required.
