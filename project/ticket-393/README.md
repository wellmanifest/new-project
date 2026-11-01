# ticket-393: Prevent stale governance preflight cache

- **ID**: ticket-393
- **Owner**: agent:codex
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT

SESSION_EXECUTION_AUTHORIZATION: the user requested execution, fixes, testing
and protected merge. Ownership is accepted through the managed idle_takeover
CAS, with its original three-file draft retained in a content-addressed
snapshot. Session prose and the local cache grant no trusted review authority.

## Goal and scope

Real SQLite ticket updates currently retain a cached PASS while a fresh
validation rejects the same checkout. Disable reuse for mutable ticket inputs
and an unbound comparison base; preserve ordinary explicit-base file caching.
Join the material patch0.20.128 and exact-head protected delivery.

## Acceptance criteria

- [ ] AC-01: Real database/configured SQLite/WAL updates and invalidated
  external snapshots are revalidated; no stale PASS bypasses the ticket reader.
- [ ] AC-02: Omitted/unbound base and unknown storage cannot reuse results;
  safe file-ticket hits and CI/no-cache behavior remain covered.
- [ ] AC-03: Full governance, native health/root and required CI pass;
  independent protected approval governs merge and immutable publication.

## Delivery boundary

Nine material files, three components, no new runtime dependencies or public
flags. Source work has a30-minute bound and checkpoint by25. Preserve other
owners and all unknown work. Keep this implementation active through protected
publication; only the external terminal receipt closes it.
