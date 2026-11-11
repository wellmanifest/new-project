# ticket-426: Harden governance checks, external adapter source binding, and worktree newline regression for v0.20.145

- **ID**: ticket-426
- **Owner**: agent:antigravity
- **Status**: IN_PROGRESS
- **Workflow state**: VALIDATION

## Goal and scope

SESSION_EXECUTION_AUTHORIZATION: continued user repair, test, merge, and version bump request across disjoint canonical scopes (`wellmanifest/new-project#563`, `wellmanifest/new-project#583` subset). Resolve five upstream governance script findings without touching `governance_check.py` (reserved by `ticket-418`), add the temporary Git worktree newline overlap regression test required by `#563`, keep bundled Wellman copies byte-for-byte synchronized, and prepare release `0.20.145`.

## Acceptance criteria

- [x] AC-01: `resolved_checks_text` parses unquoted, single-quoted, and double-quoted `uses` keys without `IndexError` in both `scripts/generate_required_checks.py` and bundled Wellman copy.
- [x] AC-02: `adapter_error` and `policy_error` require non-empty `sourcePaths` bound exactly to `repositoryPolicy.tickets.sourcePaths`, and `scoped_paths` rejects `..` and non-canonical path components.
- [x] AC-03: `delivery_landed` requires terminal status or material non-carrier delivery commit evidence on the target ref (preserving `ActivityReadBatch` subprocess bounds), `publication_observation` catches `subprocess.SubprocessError` without leaking credentials, and `worktree-default-base.test.py` covers committed-versus-dirty newline filenames in real temporary Git worktrees (`#563`).
