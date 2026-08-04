---
participant-id: agent:codex
participant: codex
role: agent
ticket: ticket-001
---
# Participant: codex (AI agent)

## Understanding

Użytkownik jawnie polecił zastąpić bezwzględną deklarację READ-ONLY zasadą,
według której standard może być zmieniany w repozytorium `new-project`, jeśli
praca jest śledzona przez ticket w `project/ticket-{NNN}`. Nie wolno przenosić
do huba ticketów należących do systemów docelowych ani naruszać własności
plików `user-*`.

## Execution plan

1. Rozdzielić w politykach kontekst utrzymania standardu i kontekst systemu
   docelowego.
2. Ujednolicić deklaracje w głównych dokumentach i raporcie.
3. Sprawdzić pozostałe wystąpienia sprzecznej reguły i przejrzeć diff.

## Actual changes

- Utworzono ticket utrzymaniowy i ograniczono jego zakres maszynowym
  `intent.json`.
- Interaktywna zgoda użytkownika: polecenie z 2026-08-04 zezwalające na zmianę
  huba w ramach repozytorium `new-project` i ticketów `project/ticket-{NNN}`.
- Zgoda interaktywna nie jest zaufanym dowodem merge.
- Zastąpiono bezwzględny model READ-ONLY ticketowanym modelem utrzymania huba.
- Rozdzielono kontekst `GOVERNANCE_HUB_MAINTENANCE` od
  `TARGET_SYSTEM_DELIVERY`, w tym zasady narzędzi, Dockera i walidacji.
- Ujednolicono `README.md`, `RAPORT.md`, `TODO.md` i `project/TICKETS.md`.
- Zachowano izolację ticketów systemów docelowych oraz zakaz modyfikacji
  plików `user-*` przez agentów.

## Acceptance evidence

- `policy structure: PASS`
- `governance scripts: PASS`
- `governance validator: PASS`
- `adoption lock: PASS`
- `git diff --check`: exit 0.
- Nie znaleziono dawnych deklaracji READ-ONLY w dokumentach objętych zakresem.

## Blockers

- Brak.
