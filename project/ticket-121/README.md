# Ticket 121: Ship the required pytest governance plugin

- **ID**: ticket-121
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Utworzono**: 2026-08-25

## Cel i Zakres

Usunac regresje publikacji standardu, ktory wymaga
`pytest -p wellmanifest_governance`, ale nie dostarcza importowalnego pluginu.
Plugin ma uruchamiac deterministyczna bramke repozytorium przed testami,
przekazujac jawna baze oraz aktualny zbior zmienionych plikow.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: Package manifest instaluje importowalny managed plugin.
- [x] AC-02: Plugin uruchamia gate raz, przekazuje baze i changed files oraz
  zatrzymuje pytest przy negatywnym werdykcie.
- [x] AC-03: Test regresyjny jest wykonywany przez CI i przechodzi lokalnie.

## Ryzyka i Uwagi
- Rekurencja lub ukrycie bledu governance. Mitygacja: plugin wywoluje tylko
  zarzadzany gate, nie uruchamia pytest i propaguje pelne stdout/stderr.
- Bledna baza w lokalnym worktree. Mitygacja: jawny override srodowiskowy,
  GitHub base ref, merge-base `origin/main` oraz staged/working diff.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-121/`.
