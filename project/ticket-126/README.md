# Ticket 126: Publish integrated autonomy governance as new-project 0.18.10

- **ID**: ticket-126
- **Owner**: agent:codex under SESSION_EXECUTION_AUTHORIZATION
- **Status**: DONE
- **Workflow state**: DONE
- **Utworzono**: 2026-08-25

## Goal and scope

Publish integrated tickets 123-125 as immutable `wellmanifest/new-project
0.18.10`: multi-agent change leases and fencing, their normative operating
rules, and explicit digest-bound recovery for a base-declared managed target
missing from the accepted Git tree.

HOME `wellmanifest`, SHAPE `domain_pack`, ADOPT `wellmanifest/new-project`.

## Acceptance criteria

- [x] AC-01: Canonical release carriers and test assertions move from 0.18.9
  to 0.18.10 with a complete changelog entry for integrated tickets 123-125.
- [x] AC-02: Every Linux test suite and exact-base governance pass.
- [x] AC-03: Hosted Linux/Windows checks and independent Validator approve the
  same frozen PR head, which Validator merges.
- [x] AC-04: Annotated tag `v0.18.10` and final GitHub Release point to that
  trusted merge commit.

## Risks and notes

- This release introduces no behavior beyond already integrated and validated
  tickets 123-125.
- Downstream adoption and runtime controller integration remain target-owned
  work in Subactor Orchestrator.

## Publication evidence

- Release PR: `wellmanifest/new-project#216`
- Frozen Validator-approved head: `26eca2dc6175281efd05de30f596091282343f2f`
- Validator run: `subactor/validator-agent#32903336242`
- Trusted merge: `4e0b7d6d888f1b4771781d25fa977f15725bcce5`
- Annotated tag: `v0.18.10` (peels to the trusted merge)
- GitHub Release: `https://github.com/wellmanifest/new-project/releases/tag/v0.18.10`
- Published: `2026-08-25T21:54:57Z`
- Closure delivery mode: governed `pull-request`; registry publication is
  disabled.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-126/`.
