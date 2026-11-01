# ticket-392: Private temporary roots for governance fixtures

- **ID**: ticket-392
- **Owner**: agent:codex
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION

SESSION_EXECUTION_AUTHORIZATION: the user requested execution, repair, tests and
protected merge. This bounded repair completes the native standard publication
following independently merged ticket-389. Session prose grants no trusted
review or merge approval.

## Goal and scope

Keep every governance integration assertion while creating disposable Git
fixtures in a private platform temporary root. Resolve its physical absolute
path before setting Git discovery ceilings, and clean only that newly created
root. Join patch 0.20.123 to the material implementation.

## Acceptance criteria

- [ ] AC-01: The complete governance integration job retains all nested suites
  and shell assertions and passes within its existing 480-second bound.
- [x] AC-02: Absolute and relative TMPDIR regressions preserve the complete
  caller directory and Git state, reject ancestor discovery, and remove the
  private root. Existing source-cache symlink refusal remains.
- [ ] AC-03: Full native health, root tests, Linux, Windows and OneDev pass;
  independent exact-head approval governs merge and immutable publication.

## Evidence and delivery boundary

The initial complete integration job passed in 205 seconds with a caller Git
ancestor and cleanup sentinel. A later preamble probe exposed relative TMPDIR
escaping its Git ceiling; the retained regression fails on that version and
passes after physical absolute-path resolution. The complete resulting
candidate still requires native checks and independent protected delivery.

Scope is seven material files in two components, no runtime dependencies and no
public interface change. Each implementation session is bounded to 30 minutes
with a checkpoint by 25. Raw diagnostics, snapshots, controller fencing and
continuity receipts remain outside Git. Keep IN_PROGRESS / PUBLICATION until
the protected controller's terminal receipt; create no closure commit. Publish
through native Goal and the independent Validator, then use C-PUBLISH-007 for
the immutable release from the approved current merge.
