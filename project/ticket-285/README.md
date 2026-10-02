# Ticket 285: Keep incomplete workspace observations conservative

- **ID**: ticket-285
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION

## Outcome and scope
Failed checkout inspection and malformed active intent must fail the read-only audit. Outstanding supported ticket branches must retain activity even when a ticket directory already exists on the target. Share the matcher and synchronize the bundled activity runtime. Publish source standard 0.20.59 after independent approval and merge.

## Acceptance criteria
- AC-01: Real Git fixtures reproduce broken checkout, malformed intent and supported outstanding branch cases; regressions pass after repair.
- AC-02: Native governance, existing workspace/ticket tests and required protected CI pass.
- AC-03: Independently approved exact-head merge and final pinned 0.20.59 release are verified externally.

## Risks
Previously skipped unknown state becomes an explicit failed audit. Repair metadata or choose the documented narrower workspace; uncertainty cannot release an active reservation. Scope is S / 25 minutes, nine implementation files and no dependencies.

## Evidence
Raw logs and controller receipts stay in external operational storage. Tests remain in tests/workspace_activity_test.py; passing tests grant no merge authority.
