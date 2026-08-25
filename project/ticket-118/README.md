# Ticket 118: Publish focused worktree guard as new-project 0.18.7

- **ID**: ticket-118
- **Owner**: agent:codex under SESSION_EXECUTION_AUTHORIZATION
- **Status**: DONE
- **Workflow state**: DONE
- **Created**: 2026-08-25

## Goal and scope

Publish the already integrated ticket-117 behavior as immutable release
`0.18.7`. The release lets adopters upgrade atomically through Goal instead of
copying managed governance files from an unpublished commit.

## Acceptance criteria

- [x] AC-01: The focused worktree overlap regression passes.
- [x] AC-02: The immutable adoption lock suite passes for version `0.18.7`.
- [x] AC-03: Exact-head governance and the governance validator pass.
- [x] AC-04: An annotated `v0.18.7` tag and final GitHub Release point at the trusted merged release commit.

## Risks and notes

- This ticket carries no new runtime behavior; it publishes ticket-117 only.
- Downstream adoption remains a separate target-owned ticket.

## Publication evidence

- Implementation PR: `wellmanifest/new-project#200`
- Frozen Validator-approved head: `ddad5a05eb4e97eb9d6400011bd5783388ce36ac`
- Trusted merge: `c6cf798727229df252fadfe02c0da36757a40673`
- Annotated tag: `v0.18.7` (peels to the trusted merge)
- GitHub Release: `https://github.com/wellmanifest/new-project/releases/tag/v0.18.7`
- Published: `2026-08-25T14:43:50Z`
- Terminal governance validation: `GOV-PASS` (0 errors, 0 warnings)
- Closure delivery mode: governed `pull-request`, registry publication disabled

## Participants

- Human participant: authorized by the active user request.
- Agent participant: [ai-codex.md](ai-codex.md)
