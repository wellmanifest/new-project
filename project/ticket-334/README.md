# Ticket 334: Keep work-start diagnostics private and preserve clean Git state

- **ID**: ticket-334
- **Owner**: agent:codex
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Utworzono**: 2026-10-12

## Goal and scope

SESSION_EXECUTION_AUTHORIZATION: the user requests continuing the standard
refactoring, repairing regressions, testing and protected merge. Continue
existing Planfile NP-012 / Issue #472, parent wellmanifest/PLF-002. The managed
allocator admitted this work after the independently approved merge of #475.
Use the already qualified V2 diagnostic repair; source changes belong only to
this native ticket and its seven declared implementation/release files.

## Acceptance criteria

- [x] AC-01: Real CLI invalid-input and unknown-workstream refusal preserves
  Git status, generic output and safe bounded diagnostics; unsafe or unsupported
  sinks are refused without content disclosure or unhandled API errors.
- [x] AC-02: Material fix and release 0.20.95 stay atomic; native governance,
  version parity and installed package verification pass.
- [ ] AC-03: Fresh current-head required checks and independent protected
  approval precede merge and immutable standard publication/adopter reuse.

## Evidence and limits

Private V2 qualification: 81 work-start cases PASS, plus eight overlapping
boundary probes PASS and a failing previous-candidate unsupported-API control.
The same 81 cases PASS with the ticket-333 proposed 0.20.94 allocator. These
are rehearsal receipts; native delivery still needs its own checks and review.
Source333 and its expired advisory lease remain untouched. No source ownership
is transferred by its merge. Existing incident logs remain recoverable.

Canonical cross-repository result: [harmonization report](https://github.com/subactor/docs/blob/b80c27e6d4c8caa0c6db389eddb4377d9f86cd8a/architecture/analysis/wellmanifest-standards-harmonization.md).
Its next evidence appendix waits for protected Docs229 handoff; this ticket
contains bounded intent and receipt references, not a second final report.
Raw logs and plan/lease checkpoints remain ignored private recovery data.

Native validation: 81 work-start tests PASS; all seven version-parity fixtures PASS;
installed wheel regression PASS (3 isolation + 7 detached-PR cases). The actual
project gate and Goal hub health PASS (53 JSON contracts, 22 shell suites).
The initial M/45 estimate was not admitted by the unchanged hub XS/S/30 policy;
it was corrected to S/30 for this prequalified one-helper fix within the same
seven-file/two-component scope. Post-commit adoption and protected CI are pending.

Post-commit validation: 81/81 PASS with actual committed 0.20.95 adoption.
Goal dry-run finished without publication; clean committed candidates use its
actual registered resume route. Required current-head CI and independent review
remain pending. The publication-state amendment keeps the material fix atomic.
