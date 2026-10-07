# Ticket 319: Reject ticketless commit subjects before Git creates a commit

- **ID**: ticket-319
- **Owner**: agent:codex
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION

SESSION_EXECUTION_AUTHORIZATION: user supplied the unfinished maintenance list and requested continuation. Fix the commit-message gate in this standard source only; preserve all foreign dirty repositories.

## Acceptance criteria

- [x] AC-01: Missing, wrong, body-only and partial ticket identifiers cannot create a commit; matching subject succeeds and explicit repository profiles retain their contract.
- [ ] AC-02: Both managed hooks are installed and verified; regressions and governance pass before protected Goal publication.

## Boundary

No bulk adoption, existing history rewrite, direct merge or source edits in blocked repositories. Allocator lease revision 1 / fencing 1; active implementation bounded to 30 minutes. Exact-head independent validation remains mandatory for publication.

## Validation

Six real Git commit-message tests pass. Host installation and enforcement suite passes, including the message hook tests; canonical schema suite: four passes; managed governance: PASS. Version projections advance to 0.20.91 with the material implementation. Adoption-lock regression also passes. Protected publication and fleet adoption remain to be observed.
