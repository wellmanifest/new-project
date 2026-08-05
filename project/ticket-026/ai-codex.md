---
participant-id: agent:codex
participant: codex
role: agent
ticket: ticket-026
---
# Participant: codex (AI agent)

## Understanding

Użytkownik oczekuje, że reguły normatywne z `CONTRIBUTING.md` będą naprawdę
egzekwowalne, a nie jedynie obecne jako tekst DSL. Obecny runtime sprawdza
strukturę dziesięciu reguł `C-EVALUATION-*`, lecz dokument zawiera 87 reguł, a
nawet część `C-EVALUATION` ma zależności poza lokalnym procesem. Potrzebny jest
kanoniczny rejestr pokrycia, który nie miesza lokalnej deterministyki,
chronionego CI i decyzji człowieka.

## Execution plan

1. Po zakończeniu ticketów 023/025 odświeżyć bazę i ponownie sprawdzić kolizje.
2. Dodać wersjonowany rejestr i schemat mapowania wszystkich reguł `C-*`.
3. Rozszerzyć `scripts/runtime.sh policy` o fail-closed walidację kompletności,
   adapterów, stanów pokrycia i dowodów.
4. Dodać pozytywne oraz mutacyjne przypadki regresyjne.
5. Włączyć artefakty do immutable adoption package i uruchomić pełny kontrakt
   Linux/Windows przed publikacją przez ticket branch i PR.

## Actual changes

- Zebrano audyt bieżącego stanu: 87 reguł ogółem, 10 enumerowanych przez
  runtime i niepełna semantyka `C-EVALUATION-001..010`.
- Potwierdzono niezależnym uruchomieniem walidatora, że PR #34 jest odrzucany
  jako `GOV-TICKET-001`, mimo zielonych testów obecnego CI.
- Utworzono wyłącznie plan i machine-readable intent; nie zmieniono
  implementacji.

## Blockers

- Nakładające się prace: ticket 023 zmienia `CONTRIBUTING.md`, manifest pakietu
  i CI, a PR #34 zmienia CI. Należy poczekać na ich zakończenie.
- Po ustaniu kolizji wymagane jest zatwierdzenie aktualnej bazy i zakresu
  implementacji.
