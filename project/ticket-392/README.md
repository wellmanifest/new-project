# ticket-392: Private platform temporary roots for governance fixtures

- **ID**: ticket-392
- **Owner**: agent:codex
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION

SESSION_EXECUTION_AUTHORIZATION: the user requested execution, repair, tests and
protected merge. This bounded repair is needed to complete the native standard
publication after the independently merged ticket-389. Session prose grants no
trusted review or merge approval.

## Goal and scope

The complete native check exceeded its existing480-second bound in the
governance integration script, which forces all temporary Git fixtures onto the
checkout filesystem. The isolated unchanged work-admission suite passes103 tests
in136 seconds using the platform temporary filesystem. Use a private temporary
root, preserve Git containment and every assertion, and clean only the directory
created by this invocation. Join the material patch release0.20.123.

## Acceptance criteria

- [x] AC-01: The complete governance integration job keeps all nested suites
  and shell scenarios and passes within its existing bound.
- [x] AC-02: Private fixture ownership, source-cache symlink refusal and Git
  discovery containment remain; unrelated directories are preserved.
- [ ] AC-03: Source projections, native health, root tests and exact-head CI
  pass; independent protected approval governs merge and immutable release.

## Delivery boundary

Scope is six material files in two components, no runtime dependencies and no
public interface change. Implementation is bounded to30 minutes with a checkpoint
by25. Raw timing, fixture diagnostics, leases and continuity receipts remain
outside Git. Keep IN_PROGRESS / PUBLICATION until the protected terminal receipt.
Publish through native Goal and the independent Validator; publish the resulting
approved merge through the declared C-PUBLISH-007 release mode.

The complete integration job passes in205 seconds under the unchanged480-second
bound. An outer fixture with a caller Git ancestor verifies sentinel retention,
unchanged Git HEAD/index and removal of the private root. The declared full
native checks and independent exact-head publication still remain required.
