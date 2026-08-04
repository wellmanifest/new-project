---
participant-id: agent:codex
participant: codex
role: agent
ticket: ticket-002
---
# Participant: codex (AI agent)

## Understanding

Użytkownik chce kontynuować utwardzanie standardu i umożliwić łatwą adopcję
manifestu w istniejących projektach korzystających z lokalnego repozytorium
`semcod/goal`. Integracja nie może używać ruchomego `main`, zgadywać SHA ani
nadpisywać driftu bez jawnego `--upgrade`.

## Execution plan

1. Dodać bezstanowy tryb `--check` i czytelny plan zmian generatora.
2. Dodać do `goal` komendę pobierającą i weryfikującą przypięty standard.
3. Pokryć oba repozytoria testami bez zależności od sieci.
4. Udokumentować pierwszą adopcję, kontrolę driftu i upgrade.

## Actual changes

- Utworzono ticket integracyjny i ograniczono zakres plików huba w
  `intent.json`.
- Polecenie użytkownika z 2026-08-04 stanowi interaktywną zgodę na ten zakres;
  nie jest zaufanym dowodem merge.
- Generator adopcji otrzymał bezstanowy `--check`, deterministyczny raport
  `CREATE`/`UPDATE`/`CHMOD` i korektę trybu wykonywalnego bez `--upgrade`.
- Pakiet zarządzany obejmuje teraz docelowy `AGENTS.md`, `project.sh` i
  `project.bat`.
- `semcod/goal` otrzymał `goal governance adopt`, który pobiera dokładny SHA,
  weryfikuje checkout i przekazuje `--check`/`--upgrade` bez shella.
- Dodano dokumentację retrofit, kontroli driftu i upgrade w obu repozytoriach.

## Acceptance evidence

- `new-project`: trzy zestawy regresyjne PASS.
- `goal`: 470 testów PASS, 2 SKIPPED.
- `goal` CLI regressions: 25 PASS.
- Black: 2 pliki zgodne; flake8 `E9,F63,F7,F82`: PASS.
- Test integracyjny Goal + rzeczywisty generator: PASS.
- `git diff --check`: PASS w obu repozytoriach.

## Blockers

- Produkcyjna aktualizacja repozytoriów zależnych wymaga opublikowanego tagu i
  pełnego SHA 0.9.0. Bieżący HEAD nie zawiera nieśledzonego generatora i nie ma
  tagu; użycie tymczasowego SHA fałszowałoby proweniencję locka.
- Wykryto 227 repozytoriów Git z `goal.yaml`. Kandydat prosty `emllm/qry` ma
  nieśledzony `local.dev.txt`; kandydat wielostackowy `if-uri/urirun` ma
  nieśledzony `.intent/`. Oba nie mają jeszcze governance ani konfiguracji
  Docker wymaganej przez domyślny manifest, więc przed pilotem wymagają czystej
  gałęzi/worktree i decyzji właściciela.
