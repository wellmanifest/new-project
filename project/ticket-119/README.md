# Ticket 119: Honor manifest-declared terminal closure statuses

- **ID**: ticket-119
- **Owner**: agent:codex under SESSION_EXECUTION_AUTHORIZATION
- **Status**: DONE
- **Workflow state**: DONE
- **Utworzono**: 2026-08-25

## Goal and scope

Remove the contradiction between the governance manifests, which declare both
`DONE` and `CANCELLED` as terminal statuses, and the managed pre-commit hooks,
which currently recognize only `DONE`. The hub hook and the adopter template
must enforce the same bounded governance-only closure for every declared
terminal status. Diagnostics must describe the contract without hard-coding a
single status.

HOME `wellmanifest`, SHAPE `domain_pack`, ADOPT `wellmanifest/new-project`.

## Acceptance criteria

- [x] AC-01: The hub and managed adopter hooks accept governance-only closure
  for `DONE` and `CANCELLED` and apply identical path/deletion restrictions.
- [x] AC-02: The host lifecycle regression proves `CANCELLED` succeeds, invokes
  the worktree guard, and still rejects implementation after closure.
- [x] AC-03: Diagnostics and remediation refer to manifest-declared terminal
  closure rather than implying that `DONE` is the only closed status.
- [x] AC-04: Focused host tests and exact-head hub governance pass.

## Risks and notes

- The hook remains fail-closed: terminal states authorize only the ticket's own
  evidence, repository indexes, and the exact generated artifact receipt.
- This ticket does not change the lifecycle vocabulary or add another status;
  it makes enforcement agree with the existing manifest authority.

## Publication evidence

- Implementation PR: `wellmanifest/new-project#202`
- Frozen Validator-approved head: `3e780314c6eaa61432901892516f5b2085bad557`
- Trusted merge: `2c7b79d09b9379b3ff05d4a72e4adec3683e4937`
- Merged: `2026-08-25T18:23:56Z`
- Hosted checks: `test` and `windows-governance` passed on the frozen head.
- Validator run: `subactor/validator-agent#32883398904`, approved and merged
  with exact-head convergence.
- Closure delivery mode: governed `pull-request`, registry publication disabled.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-119/`.
