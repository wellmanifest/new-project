# Ticket 120: Publish terminal closure enforcement as new-project 0.18.8

- **ID**: ticket-120
- **Owner**: agent:codex under SESSION_EXECUTION_AUTHORIZATION
- **Status**: DONE
- **Workflow state**: DONE
- **Utworzono**: 2026-08-25

## Goal and scope

Publish the integrated ticket-119 terminal closure enforcement as immutable
`wellmanifest/new-project 0.18.8`. This release lets Platform and other
adopters upgrade through the digest-bound package lifecycle instead of copying
the merged source SHA.

HOME `wellmanifest`, SHAPE `domain_pack`, ADOPT `wellmanifest/new-project`.

## Acceptance criteria

- [x] AC-01: Canonical release carriers and version assertions move from
  `0.18.7` to `0.18.8` with a changelog entry for terminal closure enforcement.
- [x] AC-02: Host lifecycle, adoption-lock and governance validator suites pass.
- [x] AC-03: Exact-head hub governance passes before protected publication;
  hosted checks remain required on the frozen PR head.
- [x] AC-04: Annotated tag `v0.18.8` and the final GitHub Release point to the
  trusted merged release commit.

## Risks and notes

- This ticket introduces no new hook behavior beyond integrated ticket-119.
- Downstream adoption is target-owned and remains a separate Platform ticket.

## Publication evidence

- Release PR: `wellmanifest/new-project#204`
- Frozen Validator-approved head: `d872d5926898440c48a261ead85536186af389ab`
- Trusted merge: `7eecfddcde7e46a18a96f0dfd62a3024d3e9dfea`
- Annotated tag: `v0.18.8` (peels to the trusted merge)
- GitHub Release: `https://github.com/wellmanifest/new-project/releases/tag/v0.18.8`
- Published: `2026-08-25T18:36:26Z`
- Closure delivery mode: governed `pull-request`, registry publication disabled.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-120/`.
