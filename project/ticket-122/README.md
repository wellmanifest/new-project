# Ticket 122: Release new-project 0.18.9 with pytest governance plugin

- **ID**: ticket-122
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-08-25

## Cel i Zakres
Opublikować wersję `0.18.9` standardu `wellmanifest/new-project`, która zawiera
scalony w `ticket-121` plugin cyklu życia governance dla pytest. Zakres zmiany
produkcyjnej jest ograniczony do sześciu kanonicznych nośników wersji i ich
asercji kontraktowych.

## Kryteria Odbioru (Acceptance Criteria)
- [ ] AC-01: `VERSION` wskazuje `0.18.9`.
- [ ] AC-02: pełny zestaw testów repozytorium i governance przechodzi.
- [ ] AC-03: PR zostaje zatwierdzony na exact-head przez niezależnego validatora.
- [ ] AC-04: po scaleniu istnieje tag i GitHub Release `v0.18.9`.

## Ryzyka i Uwagi
- Ryzyko: adoptery mogą przypiąć nieopublikowaną rewizję. Mitygacja: locki
  adopcji są regenerowane dopiero po scaleniu i publikacji `v0.18.9`.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-122/`.
