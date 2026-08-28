# Ticket 132: Allow bounded non-active ticket transitions

- **ID**: ticket-132
- **Owner**: agent:codex
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-08-26

## Cel

Usunąć deadlock, w którym ticket nie może zwolnić rezerwacji przez przejście do
`BACKLOG`, `PLAN` lub `BLOCKED`. Hook ma dopuścić wyłącznie zmianę statusu z
ograniczonymi dowodami governance i analogiczny powrót do `IN_PROGRESS`.

## Kryteria odbioru

- Przejście do każdego statusu zadeklarowanego w `nonActiveStatuses` działa bez
  zmiany kodu produktu.
- Implementacja z nieaktywnego ticketu nadal kończy się odmową.
- Powrót do `IN_PROGRESS` nie wymaga sztucznej zmiany implementacji.
- `DONE` i `CANCELLED` nadal należą wyłącznie do chronionego zewnętrznego
  receipt i nie mogą powstać przez commit w repozytorium.
