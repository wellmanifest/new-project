# Preprompt & technical directives (ticket-042)

- Preserve the strict `new-project.branch-lifecycle-snapshot/v1` schema.
- Fix protected GitHub fact acquisition, not the deterministic validator.
- Obtain `Repository.deleteBranchOnMerge` as a typed GraphQL boolean; do not
  substitute a default when the API omits or rejects the fact.
- Add a bounded regression to `tests/branch-lifecycle.test.sh`.
- Validate Linux, Windows and Docker contracts before publication.
- Do not create or edit human-owned `user-*.md` files.
