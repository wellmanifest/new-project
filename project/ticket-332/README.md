# Ticket 332: Isolate governance runtime installation

- **ID**: ticket-332
- **Owner**: agent:codex
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION

## Goal and scope

Fix workflow installation on externally managed Python runners through job-local virtual environments. Publish the source repair and matching release projections atomically as 0.20.93.

SESSION_EXECUTION_AUTHORIZATION: after the reported source-template blocker and proposed venv repair, the user requested continuing the planned work and verifying tests. This continues that bounded source repair and protected publication; it grants no independent review authority.

## Acceptance criteria

- [x] AC-01: Both installers use isolated runtimes and preserve failure propagation, with executable positive and negative regression fixtures.
- [x] AC-02: Package, workflow, release parity and managed governance checks pass.
- [ ] AC-03: Independent protected publication and immutable release succeed before adopter updates.

## Bounds

maxActiveMinutes: 30; checkpointMinutes: 25. Preserve the unrelated primary main commit and unknown branches. No system environment mutation or approval bypass.

## Validation

Six installer cases pass across both workflows; the previous workflows fail all six. Offline wheel build/install, seven detached-PR gate tests, required-check workflow tests, version parity and managed governance pass. Tests that create Git fixtures run with a process-local empty core.excludesFile, because this host globally ignores managed agent files; host configuration is unchanged. The first full Goal source-hub health pass succeeded; its dry-run entered a redundant second pass, which was stopped before the actual committed publication. Publication retains its required checks and independent review.
