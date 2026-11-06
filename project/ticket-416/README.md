# ticket-416: Reject non-scalar allocator classifications

- **ID**: ticket-416
- **Owner**: agent:codex-maskservice-np033
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT

## Goal and scope

SESSION_EXECUTION_AUTHORIZATION: continued user repair/test/merge/bump request; logical NP-033 after NP-032 independently delivered. Exact full argument enum validation must occur before allocator identity effects. Preserve supported scalar values, templates and Unicode titles; escape fallback JSON scalars. Ship material0.20.144 with existing release projections. No receipt authentication, seed/activity/priority changes, takeover, dependency/cap changes or managed consumer edits.

## Acceptance criteria

- [ ] AC-01: Malformed classifications fail before reservation, refs, worktree or lease effects; all declared values remain valid.
- [ ] AC-02: Template and fallback produce valid JSON preserving Unicode, quote and backslash title bytes.
- [ ] AC-03: Scoped/full default-limit tests and actual required CI/OneDev pass; independent Validator App must merge before release.
