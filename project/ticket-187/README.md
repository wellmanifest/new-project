# Ticket 187: Adopt observed repository name inventory fix

- **ID**: ticket-187
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Created**: 2026-09-05

## Goal and scope

Adopt the protected Worktrees 0.4.1 patch and publish new-project 0.20.5. The maintenance belongs to this package; target adoption is a separate target ticket.

## Acceptance criteria

- [x] AC-01: Lock and vendored artifacts bind the exact merged upstream revision.
- [x] AC-02: Packaged lifecycle audit handles .github and other observed names without allocation-policy changes.
- [ ] AC-03: Relevant suites, governance and protected exact-head review pass before publication.

## Authorization

SESSION_EXECUTION_AUTHORIZATION: user requested repair/publication via goal -a and continued after the workspace audit .github naming failure. This bounded dependency adoption carries the upstream repair to adopters.

## Validation

The .github regression failed against Worktrees 0.4.0 and passes with the exact 0.4.1 merge 46db8845637cef2388282b15fe6b17fc76c141d3. Eight adoption tests, workspace lifecycle, adoption lock, governance validator, agent host suites, managed gate and whitespace checks pass. The existing hub pre-commit hook remains active; the target host installer expects adopter-only .governance files and was not used to overwrite the hub.
