# Ticket 126: Publish integrated autonomy governance as new-project 0.18.10

- **ID**: ticket-126
- **Owner**: agent:codex under SESSION_EXECUTION_AUTHORIZATION
- **Status**: IN_PROGRESS
- **Workflow state**: VALIDATION
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
- [ ] AC-03: Hosted Linux/Windows checks and independent Validator approve the
  same frozen PR head, which Validator merges.
- [ ] AC-04: Annotated tag `v0.18.10` and final GitHub Release point to that
  trusted merge commit.

## Risks and notes

- This release introduces no behavior beyond already integrated and validated
  tickets 123-125.
- Downstream adoption and runtime controller integration remain target-owned
  work in Subactor Orchestrator.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-126/`.
