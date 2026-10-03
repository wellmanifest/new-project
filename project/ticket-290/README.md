# Safe runtime boundaries for governed work

- **Status**: IN_PROGRESS
- **Workflow state**: EDIT

## Goal and scope
Terminate interrupted allocation before additional ticket effects; reject unsafe title controls before reservation while preserving Unicode; encode JSON scalars correctly; reject malformed or duplicate host contract headings while preserving user text; and match root-level files under recursive glob segments.

## Acceptance criteria
- AC-01: Real allocator, managed paragraph and runtime glob regressions expose the original bugs and pass after correction.
- AC-02: Existing host/governance tests, bundled parity, native gate and required exact-head CI pass; both hosted OS jobs run the new runtime boundary suite, with signal checks scoped to POSIX.
- AC-03: Independent protected merge and final immutable standard v0.20.64 publication are verified.

## Risks and limits
S / 25 minutes, ten implementation files, three components, one workflow interface path and no dependency changes. Tests use owned fixtures and do not alter user HOME or actual host files. Signal tests address only owned allocator processes. Raw logs, original-code reproductions and real controller evidence stay external.
