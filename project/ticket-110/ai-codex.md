---
participant-id: agent:codex
participant: codex
role: agent
ticket: ticket-110
---
# Participant: codex (AI agent)

## Understanding

Standard 0.18.5 osobno dostarcza lifecycle hook i worktree runner, lecz nie
komponuje ich w egzekwowalny łańcuch. `exit 0` w obu poprawnych ścieżkach
sprawia, że dopisana później bramka jest martwa. Ponieważ hook jest managed,
to regresja dystrybucyjna: aktualizacja może usunąć działającą ochronę adoptera.

## Execution plan

1. Zapisać reprodukcję dla poprawnego `IN_PROGRESS`, poprawnego `DONE`,
   negatywnego werdyktu guarda i braku runnera.
2. Oddzielić zarządzany payload adoptera od aktywnego hooka huba i zastąpić w
   payloadzie terminalne sukcesy funkcją propagującą werdykt guarda.
3. Zadeklarować runtime hooka w kontrakcie hostów i wyprowadzić z niego
   atomowy bootstrap oraz kontrolę aktywacji.
4. Uruchomić test komponentu, pełny zestaw shellowy i governance na dokładnym
   base/head w trybie fail-fast; publikować wyłącznie przez Validator App.

## Actual changes

- Initialized the bounded ticket and recorded `SESSION_EXECUTION_AUTHORIZATION`
  from the request to execute this work.
- Hook lifecycle uruchamia worktree guard przed każdym dozwolonym sukcesem.
- Kontrakt hostów deklaruje trzy pliki runtime; bootstrap wyprowadza ich kopię
  z manifestu pakietu, a aktywacja sprawdza ich obecność.
- Test spy pokrywa obie ścieżki sukcesu, propagację porażki i brak runnera;
  pełny zestaw 10 testów shellowych przeszedł w trybie fail-fast.

## Blockers

- Lokalny commit implementacji jest prawidłowo blokowany przez istniejący,
  niezależny overlap w starych, brudnych worktree huba; żadnego cudzego stanu
  nie usunięto i nie użyto `--no-verify`. Payload adoptera został rozdzielony
  od aktywnego hooka huba, więc publikacja nie wymaga naruszania tych danych.
- New authority is still required for destructive action, secret access, new
  external coordination or material objective expansion. Protected delivery
  may be invoked without another prompt when publication is in scope; its
  exact-head trusted approval remains independent evidence.
