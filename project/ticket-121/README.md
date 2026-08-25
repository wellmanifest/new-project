# Ticket 121: Ship the required pytest governance plugin

- **ID**: ticket-121
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
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

## Publication evidence

- Release PR: `wellmanifest/new-project#207`
- Frozen Validator-approved head: `1e4f0aa00142f3d33d50914ef71e496a374eca4d`
- Trusted merge: `d958cd2e06f61551b1ab469ba66c8302cdd02af7`
- Validator run: `subactor/validator-agent#32887449868`
- Direct PR latency: `104s`, SLO `300s` met.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-121/`.
