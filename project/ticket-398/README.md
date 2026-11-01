# ticket-398: Detect Python secret literals in defaults and comparisons

- **ID**: ticket-398
- **Owner**: agent:codex
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION

SESSION_EXECUTION_AUTHORIZATION: the user requested execution, fixes, tests
and protected merge. Managed allocation names this actor and session; no
foreign draft is taken over. Session prose is not trusted review evidence.

## Goal and scope

Current Python scanning misses positional-only defaults, attribute/subscript
comparisons and literal-left comparisons. Reuse the existing secret-name and
literal rules across those forms and lambda defaults. Keep source and bundle
identical and preserve dynamic expressions, placeholders and normal behavior.
Join the material implementation with patch0.20.129.

## Acceptance criteria

- [x] AC-01: Previously missed forms fail before the fix and are detected in
  both modules afterward; async/lambda, chained comparisons and positional
  alignment pass with negative controls for safe/dynamic values.
- [ ] AC-02: Native health, root tests, version parity, normal hooks and
  exact-head CI pass; independent approval controls merge and publication.

## Delivery boundary

Eight material files in three components; no dependencies, new CLI or changed
diagnostic. Source work is bounded to30 minutes with checkpoint by25. Preserve
unknown and foreign work. Keep raw logs and controller receipts external;
keep IN_PROGRESS / PUBLICATION until a protected external terminal receipt.

Review remediation retains all adverse AST cases and uses the protected public
dummy sentinel; dynamic sample parameter names are generated explicitly.
No real credentials, protected-policy changes or test exemptions are involved.
