# Ticket 207: Resolve a merged ticket as terminal from Git when no receipt exists

- **ID**: ticket-207
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Owner**: founder

## Goal and scope

Coordination rules in this standard filter on active tickets:
`GOV-CONFLICT-001` compares active pairs, the allocator refuses a new ticket
while one is unfinished, and terminal outcomes release reservations. All of it
assumes the active set is small and true.

Measured on 2026-09-09 across four adopters:

| repository | projected active |
| --- | --- |
| `subactor/coding-agent` | 54 |
| `wellmanifest/new-project` | 65 |
| `subactor/platform` | 153 |
| `subactor/core` | 182 |

Sampled from `coding-agent`: `ticket-018`, `ticket-019` and `ticket-111` are all
merged into `main` and still read `IN_PROGRESS`. Deriving conflicts from these
sets produces 810, 1359, 2514 and 1292 colliding pairs — noise, not signal.

That is why declaring `conflictsWith` never helped anyone. The rule works; the
set it reasons over is roughly a hundred times too large.

## Why it happens

`resolve()` verifies a terminal outcome by Git ancestry, exactly as
`terminalOutcomes.merged.verification` declares — but only for a ticket that
already has a receipt. The receipt registry lives in the Git common directory
and is untracked, so it is usually absent, and a ticket merged through an
ordinary pull request stays projected active for the rest of the repository's
life.

The verification exists. Nothing invokes it without a receipt.

## What this changes, and what it deliberately does not

`missingPolicy` gains a second value, `git-ancestry`, and the default stays
`status-projection`.

The existing test states the reason for that default plainly — "Missing
optional registry is conservative and does not block ordinary work" — and it
caught an earlier version of this change that reversed it silently. Reversing a
tested decision belongs to the standard's owners, not to a patch. An adopter
whose hand-edited statuses have stopped tracking reality opts in; everyone else
sees no change at all.

A ticket's own directory is committed together with its delivery, because a
commit carrying only tracking carriers is refused. Its presence on the target
ref is therefore the ancestry evidence the policy already asks for. A branch for
the same ticket that the target does not yet contain means work is still in
flight, and the ticket stays active — the case that must never regress, because
a false terminal releases the reservation on live work.

Verified against `coding-agent` with `ticket-137` open and pushed: it resolves
active, while every merged ticket resolves terminal. Same repository,
`status-projection` 53 active, `git-ancestry` 0.

## Non-goals

No new conflict rule. Deriving conflicts from `allowedPaths` was measured first
and rejected: on today's active sets it yields thousands of findings. This
ticket makes the existing rules usable rather than adding another one beside
them.

## Acceptance criteria

- [x] AC-01: `status-projection` behaviour is unchanged, proven by the existing
      conservative test still passing untouched.
- [x] AC-02: Under `git-ancestry`, a ticket whose directory is on the target ref
      resolves terminal with authority `git-ancestry`.
- [x] AC-03: A ticket with any branch outside the target stays active, even when
      its directory is already on the target.
- [x] AC-04: A ticket that never reached the target is untouched.

Validation: `bash tests/ticket-activity.test.sh`.

## Tracking boundary

This directory contains the minimal reviewed intent. Executable code, research
scripts and tests belong in ordinary source directories, not in
`project/ticket-207/`.
