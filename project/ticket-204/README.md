# Ticket 204: Refuse a commit on standard drift, not on standard staleness

- **ID**: ticket-204
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Owner**: founder

## Goal and scope

`scripts/precommit_standard_update.py` refuses a commit whenever the pinned
standard revision is not the latest published one, unless the ticket named on
the commit is itself a governance adoption ticket binding the exact old and new
revisions. An implementation ticket can never be that, and should not become
one.

This standard published seven revisions on 2026-09-08 (0.20.12 through
0.20.18). The window in which an adopter's pin equals the published revision is
therefore hours wide, and every commit outside it is refused.

Measured consequence in one adopter, `maskservice/update`: five pull-request
repairs failed on this gate, spent their whole retry budget and went terminal.
Verified afterwards that the repository had zero drift — all 88 managed files
matched their recorded sha256 digests exactly. Nothing was wrong with the
repository, and nothing those commits contained could have made it right.

## What this ticket does not claim

The managed commit hook no longer invokes this updater.
`template/files/pre-commit.template.sh` performs a local `verify-pin --staged`
check with no network and no adoption demand, and the adopter above stopped
invoking the updater on 2026-09-08 at 12:06 when it took standard 0.20.12. The
failures above come from a roughly six-hour window on 2026-09-07/08 when the
call was live, and they are frozen: the controller replays the stored child
outcome rather than re-executing.

This is therefore not a fix for an active recurrence on the managed hook path.
It closes residual exposure, which is real: the script still ships to every
adopter as a `managed` file, and `governance/standard-adoption.default.json`
still declares `enabled: true`, `trigger: pre-commit`,
`action: prepare-and-abort`. Any repository still pinned at or below 0.20.11,
and any repository that wires the updater as the declared policy describes,
reproduces the outage today.

## The distinction this restores

Staleness and drift are different facts, and the gate treated them as one.
Staleness means the world moved: a newer revision was published. Drift means
this repository moved: a managed file no longer matches the digest recorded in
its own pinned lock. A commit can cause or repair only drift, so refusing on
staleness protects nothing and stops everything.

## Acceptance criteria

- [x] AC-01: A refusal carrying `GOV-STANDARD-UPDATE-001` is downgraded to a
      reported advisory when every staged managed file matches the digest in
      the staged lock; the commit proceeds and the staleness is still printed.
- [x] AC-02: Drift in any managed file keeps failing closed with the canonical
      diagnostic, and so does a refusal that is not adoption authorization.
- [x] AC-03: Evidence that cannot be read — no staged lock, malformed JSON, no
      Git — never relaxes the gate. An unestablished answer is not a pass.
- [x] AC-04: Drift is judged on staged content, never the worktree, and is read
      in one batched Git process rather than one per managed file.

Validation: `tests/precommit-standard-update.test.sh` covers all four criteria
and was verified to fail when the downgrade is removed.

## Tracking boundary

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-204/`.
