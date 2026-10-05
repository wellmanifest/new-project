# Ticket 310: Reliable autonomous publication handoff

- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Owner**: agent:codex / codex-publication310-oct5

SESSION_EXECUTION_AUTHORIZATION: user requested repairs to standards, Planfile and non-working publication dependencies. This source task owns allocator results and the host projection adapter only.

- [ ] AC-01: Native successful allocation explicitly returns exact identities; refusal produces no successful result.
- [ ] AC-02: Host projection is deterministic, preserves unrelated bytes, rejects stale input and competing writers, and has restorable backup.
- [ ] AC-03: Native tests, governance, exact-head/base OneDev and independent protected merge pass before applying the published updater.

The existing primary change in packages/wellman/src/wellman/check.py is outside this ticket and remains untouched. Current allocator lacks its required JSON result; this initial allocation is recorded from its exact native creation output and verified Git registration before controller admission. All later consumers must use the repaired machine result.
