# Ticket 321: Offline Wellman packaging regression

- **ID**: ticket-321
- **Owner**: agent:codex
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION

SESSION_EXECUTION_AUTHORIZATION: user requested continuation, testing and protected merging of the local alternative. Fix actual OneDev PR460 packaging failure without candidate network access or skipped tests.

## Acceptance criteria

- [x] AC-01: Real wheel build, clean-venv install and installed-runtime regressions work without an index; missing build tools fail immediately in a genuine clean venv.
- [ ] AC-02: CI provisions pinned test-only build tools, native governance and actual OneDev/required hosted checks pass before independent exact-head publication.

## Boundary

PLF-034, bounded S30/four material files. No runtime, protected policy or candidate network change. PLF-026/033 local publication and exact synthetic commit CI remain dependent work.

## Validation

Local no-index real wheel/install/runtime suite PASS, including seven detached PR runtime regressions; actual clean-venv missing-tools refusal PASS; pinned Ruff and diff checks PASS. Earlier deployed immutable executor canary built and installed the real wheel offline as uid65534 with setuptools80.9.0/wheel0.45.1. Exact candidate OneDev verification and protected independent publication remain pending.
