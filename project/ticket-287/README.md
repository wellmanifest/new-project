# Serialize continuity event and checkpoint index transactions

- **Status**: IN_PROGRESS
- **Workflow state**: EDIT

## Goal and scope
Protect journal validation, append, index replacement and rebuild with the same bounded per-stream OS lock. Reject a stale concurrent checkpoint before append, retain append-only durable events, rebuild a missing index on exact idempotent replay, and reject an oversized index before appending. Publish 0.20.61 after independent exact-head approval.

## Acceptance criteria
- AC-01: Two-process stale-capture and independent-ticket tests preserve monotonic journals and complete indexes; replay recovers interrupted index writes; preflight size rejection leaves the journal unchanged.
- AC-02: Existing continuity checks, native governance and required Linux/Windows/OneDev CI pass. CI wiring for the new suite is deferred to a dependent ticket with its own public-interface budget.
- AC-03: Independent exact-head merge and immutable final 0.20.61 release are verified externally.

## Risks and limits
Lock scope is the configured local stream, with a bounded acquisition wait. Shared advisory files do not grant controller or merge authority. Checkpoint creation outside the transaction may be stale and must be recaptured after a structured rejection. Scope is S / 25 minutes, seven implementation files, three components, no dependencies or schema changes.

## Evidence
Two isolated processes both reported recorded on the original code, yet persisted two sequence-one checkpoints with only one index entry and a non-monotonic chain. Raw test streams and real controller receipts remain in external operational storage.

## Scope correction
The initial native gate rejected workflow wiring because the ticket admitted no public-interface change. The exact owned workflow edit was removed, and this intent narrowed under a fresh accepted fenced lease. The failed gate and initial commit are preserved; the remaining CI outcome must use a dependent ticket, without raising this PR budget.
