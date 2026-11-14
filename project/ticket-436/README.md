# Ticket 436: Deterministic continuity-storage clock assertion

- **ID**: ticket-436
- **Owner**: agent:codex
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Utworzono**: 2026-11-13

## Cel i zakres

Fix [issue #608](https://github.com/wellmanifest/new-project/issues/608) by freezing the clock in the existing distinct-storage-parent commit/rebuild regression. Keep all exact index, event and rebuild assertions. Production timestamps and storage behavior stay unchanged.

## Acceptance Criteria

- [x] AC-01: A deterministic second-boundary diagnostic reproduces the original mismatch and passes with the test-local clock patch, retaining every assertion.
- [ ] AC-02: The complete continuity-storage suite and required protected platform checks pass for the publication head.
- [x] AC-03: The canonical governance gate accepts the bounded test-only change.

## Authorization and ownership

SESSION_EXECUTION_AUTHORIZATION: user requested sequential Heyasa implementation, testing and protected publication, and repeated “kontynuuj,scalaj,testuj”. Native Heyasa job b5006c79-35be-47d5-bd1b-7f2d7a05fe1f allocated this exact ticket; its worker stopped before implementation with session_allocation_repository_invalid. Continue this allocation rather than creating another.

The published idle-takeover controller accepted the handoff at 2026-11-14T00:03:32Z, revision 4, fence 4; its snapshot preserves the allocated scaffold. This continuation has a hard stop at 2026-11-14T00:33:32Z. The scope is unchanged; the explicit delivery metadata completes the allocated intent. No lease hash is manually rewritten.

## Evidence and risks

The paired clock diagnostic is an isolated local check, not merge approval. Raw logs remain in private operational receipts. Required full protected CI and independent Validator approval remain mandatory. No production code, timestamp format, test skips or release version changes are included.

Local checks: all 32 continuity-storage cases completed (28 passed; four existing platform-specific skips). The paired forced second-boundary diagnostic failed on the original test and passed on the proposed patch. Protected CI and independent exact-head approval remain pending.
