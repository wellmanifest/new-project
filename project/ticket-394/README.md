# ticket-394: Validate Python packaging shapes and installed checker guidance

- **ID**: ticket-394
- **Owner**: agent:codex
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION

SESSION_EXECUTION_AUTHORIZATION: the user requested execution, repairs, tests
and protected merge. The native allocator explicitly bound this new ticket to
agent:codex and this session. Session prose grants no trusted review authority.

## Goal and scope

A syntactically valid TOML scalar or array at tool, pytest or ini_options can
raise AttributeError in the host checker instead of reporting packaging findings.
Guard the nested mapping shapes and retain valid lifecycle binding. Both error
guides must give the installed adopter checker path and distinguish the source
hub layout. Join material patch0.20.124.

## Acceptance criteria

- [x] AC-01: Wrong-shaped TOML tool/pytest/ini_options produce ordinary findings
  without traceback; valid and absent declarations retain existing behavior.
- [x] AC-02: Source/bundled parity holds and both guides identify executable
  installed and source-hub checker locations.
- [ ] AC-03: Version projections, full native health, root tests and exact-head
  CI pass; protected independent approval governs merge and immutable release.

## Delivery boundary

Ten material files in two components; no new dependency or public interface.
Implementation is bounded to30 minutes, checkpoint by25. Test logs, snapshots,
controller grants and continuity receipts remain outside Git. Preserve the
separate ticket393 scope. Keep IN_PROGRESS / PUBLICATION until the protected
terminal receipt; use native Goal and C-PUBLISH-007 for the resulting release.

Validation: the tracked CLI regression failed with the original scalar-tool
AttributeError. After the mapping guards, all24 source/bundled cases and the
complete existing host suite pass. Full native/CI results remain external;
trusted approval and terminal publication are still pending.
