# Ticket 453: Wire bootstrap packaging scope regressions into native CI

- **ID**: ticket-453
- **Owner**: agent:codex / codex-bootstrap-ci-wiring-20261117t1630z
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION

## Goal and scope

PR #633 adds a controller suite that passes local verification, but GitHub's
required wiring assertion correctly reports that no native step invokes it.
Ticket452's reservation does not own the workflow. Fresh managed admission
found this CI-only scope free, within the two-ticket governance WIP limit.

Add one forward-compatible workflow step: if either the controller or its
regression suite is present, run the suite and propagate its exit status.
Neither exists on this base. After this independently reviewed dependency
lands, ticket452 rebases and must pass the actual suite through GitHub CI.
All existing checks, suite wiring assertions and permissions stay required.

SESSION_EXECUTION_AUTHORIZATION: the user's continuing instruction to repair,
test and complete autonomous API publication. Existing coordination remains
PLF-27911 / PLF-27919. This ticket owns only the CI dependency; ticket452
retains the implementation and its open PR.

## Acceptance criteria

- [x] AC-01: The exact CI step handles absence, executes the delivered suite and rejects a missing suite beside a delivered controller.
- [ ] AC-02: Native validation, required CI and independent Validator merge succeed.

Keep this ticket in publication until an external terminal receipt records
its result. No closure-only commit or separate package release is needed.

Classification correction: the hub explicitly lists the already owned CI
workflow as a public interface. The original zero-interface estimate was
incorrect; this same five-line, one-file change uses one interface. No path,
check, permission or implementation outcome was added to the accepted scope.

Validation: the exact workflow step passed against the delivered controller
at ae0de894 (16 tests); absence exits zero, while a controller without its
suite exits nonzero. Removing only this step restores the original parsed
workflow exactly. Native governance passed; required CI and independent
publication remain pending.
