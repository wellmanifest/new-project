---
participant-id: agent:codex
participant: codex
role: agent
ticket: ticket-011
---
# Participant: codex (AI agent)

## Understanding

Obecne testy nie są dowodem natywnej zgodności wrapperów z Windows.

## Execution plan

1. Dodać minimalny natywny fixture PowerShell.
2. Uruchomić wrappery i generator na Windows runnerze.
3. Sprawdzić pozytywne i negatywne kody wyjścia.
4. Włączyć wymagany status do procesu wydania.

## Actual changes

- Dodano job `windows-governance` na natywnym runnerze `windows-latest`.
- Dodano test PowerShell wrapperów i generatora w ścieżce zawierającej spacje.
- Utwardzono propagację błędów wrapperów `.bat`.
- PR #11 został scalony po zielonym CI i exact-head approval aplikacji.

## Blockers

- Brak; implementacja i wymagany status Windows są aktywne.
