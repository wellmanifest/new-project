---
participant-id: agent:codex
participant: codex
role: agent
ticket: ticket-104
---
# Participant: codex (AI agent)

## Understanding

Platform wykrył, że aktualna adopcja standardu tworzy `AGENTS.md`, którego
`git diff --check` nie akceptuje. Defekt pochodzi z zarządzanego szablonu, więc
naprawa należy do Wellmanifest i musi chronić cały zbiór tekstowych źródeł
pakietu, nie tylko bieżącą linię.

## Execution plan

1. Zapisać i zwalidować zakres oparty na dokładnym `main`.
2. Dodać najpierw regresję obejmującą źródła `managed` i `extendable`.
3. Usunąć źródłowy trailing whitespace.
4. Uruchomić wszystkie testy, Ruff, exact-base governance i `git diff --check`.
5. Opublikować PR wyłącznie przez exact-head Validator-agent.

## Actual changes

- Initialized the bounded ticket and recorded `SESSION_EXECUTION_AUTHORIZATION`
  from the request to execute this work.
- Reproduced the defect at `template/files/AGENTS.template.md:82` and confirmed
  that it is the only affected package source at the accepted base.
- Added a manifest-driven byte-level regression, removed the source defect and
  passed all 11 shell suites, Ruff, diff hygiene and exact-base governance.

## Blockers

- None inside the recorded intent; proceed without a second confirmation.
- New authority is still required for destructive action, secret access, new
  external coordination or material objective expansion. Protected delivery
  may be invoked without another prompt when publication is in scope; its
  exact-head trusted approval remains independent evidence.
