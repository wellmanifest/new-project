# Ticket 103: Release digest-bound managed takeover as new-project 0.18.3

- **ID**: ticket-103
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-08-21

## Cel i Zakres

Publish the integrated ticket-102 takeover contract as immutable
`new-project 0.18.3`. This ticket changes release carriers and assertions only.

## Kryteria Odbioru (Acceptance Criteria)
- [ ] AC-01: Version carriers and active assertions declare `0.18.3`.
- [ ] AC-02: Changelog describes digest-bound takeover as a patch.
- [ ] AC-03: All suites, Ruff and exact-base governance pass.
- [ ] AC-04: Validator approves and merges the exact release head.
- [ ] AC-05: Clean main, tag and GitHub Release `v0.18.3` bind the merge commit.

## Ryzyka i Uwagi

- Tag and release are immutable and follow trusted merge plus clean-main retest.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-103/`.
