# Ticket 345: Keep host-test source fixtures outside recursive runtime state

- **ID**: ticket-345
- **Owner**: agent:codex
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Created**: 2026-10-15

SESSION_EXECUTION_AUTHORIZATION: the user requested continued repair of
standardization and mechanical path enforcement. Parent PLF-15925, preparation
PLF-15926. This native allocator reservation grants no implementation authority;
source editing waits for exact controller registration and authentic fencing.

The real isolated Goal release dry-run at base52537e6d failed in
`tests/agent-hosts.test.sh`: copying the source recursively included its own
`.subactor/cache` destination. Preserve canonical `.subactor/manifest.json`
and `.gitignore`, exclude operational state and put fixtures in this checkout's
own private cache. Keep the original `.koru` state and foreign worktrees intact.

- [ ] AC-01: Native host suite passes with its own cache nested inside the source,
  asserts canonical Subactor files remain and operational state is absent.
- [ ] AC-02: Material source fix passes complete scope/governance and independent
  exact-head protected checks/review/merge.

No deployment, release grant, tag/Release or adopter operation belongs to this
source slice. Raw proof and the exact registration proposal live in this
worktree's ignored `.subactor/receipts/ticket-345/`; source and tests stay in
ordinary source directories.
