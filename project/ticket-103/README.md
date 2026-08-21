# Ticket 103: Release digest-bound managed takeover as new-project 0.18.3

- **ID**: ticket-103
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
- **Utworzono**: 2026-08-21

## Cel i Zakres

Publish the integrated ticket-102 takeover contract as immutable
`new-project 0.18.3`. This ticket changes release carriers and assertions only.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: Version carriers and active assertions declare `0.18.3`.
- [x] AC-02: Changelog describes digest-bound takeover as a patch.
- [x] AC-03: All suites, Ruff and exact-base governance pass.

## Pre-publication evidence

- 11/11 `tests/*.test.sh`: PASS.
- Ruff: PASS.
- Exact-base governance from `5c337309`: 0 errors, 0 warnings.
- Tag and release `v0.18.3` absent before publication.
- [x] AC-04: Validator approves and merges the exact release head.
- [x] AC-05: Clean main, tag and GitHub Release `v0.18.3` bind the merge commit.

## Ryzyka i Uwagi

- Tag and release are immutable and follow trusted merge plus clean-main retest.

## Final evidence

- Validator merged exact head `6e129086` as
  `04ced312af75e478ac2ceea38c29c59c6d484270`.
- Clean-main 11/11 suites and Ruff: PASS.
- Goal direct-main publication: SUCCESS; peeled tag `v0.18.3` equals the merge.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-103/`.
