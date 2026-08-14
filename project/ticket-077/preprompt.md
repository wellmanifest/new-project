# Preprompt & Wytyczne Techniczne (ticket-077)

- **Tytuł Zadania**: Bind agent reports to workspace identity
- **Utworzono**: 2026-08-14T14:28:14Z

## Wymagania i Ograniczenia Techniczne

- Schema + docs + validate example; nie runtime i nie nowy daemon.
- Reuse `placement.home|shape|runtimeOwner|adopt`. `"w ramach wellmanifest"` =
  ADOPT, nie HOME.
- Nie wymagać `placement` na starych ticketach.
- Nie zmieniać zamkniętego `wellmanifest/agent` v1.
- Nie otwierać PR i nie pushować.

## Podlinkowane Zasoby

- `governance/agent-report.schema.json`
- Cursor user rule `workspace-identity-bind.mdc` (poza tym repozytorium)
- nlp2dsl `Ambiguity` na `placement.home`
- intract `validate_intent_snippet` / vallm `validate_intent_contracts` (wskazać, nie rozszerzać)

## Dyrektywy Wykonawcze dla Agenta AI

- Polecenie zlecające implementację bramek jakości tworzy
  `SESSION_EXECUTION_AUTHORIZATION`.
- Kod wykonywalny i testy poza katalogiem ticketu.
