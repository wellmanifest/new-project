# Ticket 122: Release new-project 0.18.9 with pytest governance plugin

- **ID**: ticket-122
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
- **Utworzono**: 2026-08-25

## Cel i Zakres
Opublikować wersję `0.18.9` standardu `wellmanifest/new-project`, która zawiera
scalony w `ticket-121` plugin cyklu życia governance dla pytest. Zakres zmiany
produkcyjnej jest ograniczony do sześciu kanonicznych nośników wersji i ich
asercji kontraktowych.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: `VERSION` wskazuje `0.18.9`.
- [x] AC-02: pełny zestaw testów repozytorium i governance przechodzi.
- [x] AC-03: PR zostaje zatwierdzony na exact-head przez niezależnego validatora.
- [x] AC-04: po scaleniu istnieje tag i GitHub Release `v0.18.9`.

## Terminal receipt

- Integrated default-branch SHA:
  `6faa72b387f8198516c7fb01c5545d112bc0e7cf`.
- Integrated pull request: `wellmanifest/new-project#208`.
- Immutable tag `v0.18.9` resolves to the same integrated SHA.
- The published release is the immutable source for downstream adoption locks.

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
