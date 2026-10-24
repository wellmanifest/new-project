# ticket-382: Resolve issue #534 finding 4: validate seed preparation before ticket access or mutation and reject symlinked ticket paths.

- **ID**: ticket-382
- **Owner**: agent:coding-agent
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION

## Goal and scope

Deliver the bounded seed-preparation correction for issue #534 finding 4, preventing invalid requests and symlinked ticket paths from causing premature ticket reads, writes or staging.

SESSION_EXECUTION_AUTHORIZATION: validated native ticket PLF-19899; Willman request 6592949c-8898-4ca0-b085-463bee33ae66; protected publication only.

## Acceptance criteria

- [x] AC-01: prepare() validates request shape, authority, writer identity, repository binding and adoption context before reading ticket contents, rewriting files or changing the Git index.
- [x] AC-02: Reject symlinked project directories, ticket directories, README files and intent files before accessing their contents; external targets remain unchanged.
- [x] AC-03: Validate the allocator reservation, ticket intent binding and existing seed content before mutation. Rejected preparation leaves README bytes, index contents and seed-reservation state unchanged.
- [x] AC-04: Preserve successful allocator-driven preparation despite its two initially untracked ticket carriers. Permit only those exact validated carriers during preparation; unrelated untracked files remain forbidden and other operations retain their existing checks.
- [x] AC-05: Existing successful seed creation, canonical allocation, hook enforcement and second-seed refusal regressions pass alongside direct prepare() rejection tests.
- [ ] AC-06: Required governance and diff checks pass with implementation changes confined to the two frozen paths and no new runtime dependencies. Local diff checks passed; authoritative repository gates remain runner-owned.

## Implementation evidence — 2026-10-24

Scope remains issue #534 finding 4 only. Findings 1, 2, 3 and 5, evidence-policy
decisions, release/version changes and adopter upgrade reruns are excluded by
the immutable intent; this delivery does not complete the entire issue.

`scripts/seed_baseline.py` now validates the request and ticket path components,
allocator reservation, intent binding, seed inventory and digests before
appending authorization or staging. Preparation permits only its exact README
and intent as initially untracked files. Other context callers retain strict
inventory checks. Existing seed reservations and secret-bearing/oversized
carriers are rejected before mutation; final stage verification remains in place.
This remains an accidental-writer boundary, not a filesystem transaction or
hostile operating-system-user isolation guarantee.

Focused verification:

- `python3 -B tests/seed_baseline_test.py`: **PASS**, 17 tests in 38.365 seconds.
  Direct rejection tests cover malformed/invalid requests, authority, writer
  and repository bindings, adoption drift, all four symlink locations, invalid
  reservations/intents, seed drift and unrelated untracked, ignored or staged
  files. They compare ticket bytes, raw Git index, staged entries and reservation
  state. Content-access guards and external sentinel checks cover AC-01/02.
  The real allocator/bootstrap and enforced-hook fixtures also passed (AC-05).
- `git diff --check`: **PASS**. Material edits are confined to the two approved
  implementation paths; no runtime dependencies were added. Focused secret-pattern
  checks on both material files passed; test secret strings are synthetic.
- `work_start_check.py --root . --workstream governance --ticket ticket-382`:
  `REUSE_EXISTING`, no blockers, one active ticket with a workstream limit of two.
  Historical ticket-361 has no registered delivery worktree; no takeover occurred.
- Full repository verification, governance gate and todo2code compare-workspace
  were deliberately not run in this model turn. The trusted runner performs
  the authoritative gates once. Docker was not used (`docker.required=false`).

Validated material SHA-256 digests:

- `scripts/seed_baseline.py`: `072ba0ee47a656e61b746c8c09f768d6264b6d2889c6b46c8537a8c9d3eccab7`
- `tests/seed_baseline_test.py`: `9a64e1334d49dec3bd44fcc1da0cf1c660e55f79a4b1c9b5b04b9aad01a0196e`

## Runner handoff

- Ticket/request: `ticket-382`, `PLF-19899`, job `6592949c-8898-4ca0-b085-463bee33ae66`.
- Branch/worktree: `ticket/382-project-job-6592949c`, `.worktrees/ticket-382--project-job-6592949c`.
- HEAD and unchanged `acceptedBaseSha`: `66f4eabf6aa694abb4f51a98390a6b10457a01ca`.
- Unchanged intent SHA-256: `1c8885bb5844a2ae222d2fa80903defbeb23b74c164c1ca4fb1d87bb11a68211`.
- Observed lease: `allocation-ticket-382-project-job-6592949c`, revision **1**,
  fencing token **1**, owner session `coding-agent-PLF-19899-6592949c-8898-4ca0-b085-463bee33ae66`.
  The lease was neither renewed nor transferred by this model turn.
- Recovered runner checkpoint: sequence **3**, phase `tools`, next action `edit`,
  plan `artifact:project-plan/6592949c-8898-4ca0-b085-463bee33ae66`, slice **1/1**.
  Its snapshot predates these edits. The runner must capture the updated dirty
  snapshot/checkpoint and revalidate fencing before its guarded publication.
- Existing allocator changes to `project/TICKETS.md` and the intent were preserved.
  This turn edited only the two material files and this README.
- Completed: bounded finding-4 implementation and focused tests. Locally committed:
  **no**. Pushed/PR-open by this turn: **no**. Merged/deployed by this turn: **no**.
- Next action: runner-owned authoritative gates for AC-06, then exact guarded
  publication and independent review. Keep `IN_PROGRESS / PUBLICATION`.
