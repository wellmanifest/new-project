# Ticket 105: Release managed text hygiene as new-project 0.18.4

- **ID**: ticket-105
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Utworzono**: 2026-08-21

## Cel i Zakres

Opublikować zintegrowaną poprawkę ticketu 104 jako niezmienny
`new-project 0.18.4`. Ticket zmienia wyłącznie nośniki wydania i aktywne
asercje wersji.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: Nośniki wersji i aktywne asercje wskazują `0.18.4`.
- [x] AC-02: Changelog opisuje higienę zarządzanych tekstów jako patch.
- [x] AC-03: Wszystkie testy, Ruff, diff hygiene i exact-base governance
  przechodzą.
- [ ] AC-04: Validator zatwierdza i scala dokładny head wydania.
- [ ] AC-05: Czysty `main`, tag i GitHub Release `v0.18.4` wskazują merge commit.

## Ryzyka i Uwagi
- Tag i release są niezmienne, dlatego publikacja następuje dopiero po trusted
  merge i ponownym teście czystego `main`.

## Pre-publication evidence

- 11/11 `tests/*.test.sh`: PASS.
- Ruff i `git diff --check`: PASS.
- Exact-base governance od `1e51d2ec`: 0 errors, 0 warnings.
- Tag i GitHub Release `v0.18.4` są nieobecne przed publikacją.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-105/`.
