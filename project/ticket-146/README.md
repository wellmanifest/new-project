# Ticket 146: Ignore unclaimed stale ticket scopes in worktree overlap guard

- **ID**: ticket-146
- **Owner**: human:founder
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-08-30

## Cel i Zakres

Nie przypisywać osieroconych, historycznych ticketów `IN_PROGRESS` do każdego
aktywnego worktree. Zakres ticketu ma właściciela tylko wtedy, gdy wskazuje go
branch albo checkout rzeczywiście zmienia jego katalog; realne konflikty
plików nadal są wykrywane niezależnie.

## Kryteria Odbioru (Acceptance Criteria)

- [x] AC-01: Bounded execution jest autoryzowane bieżącą instrukcją Foundera.
- [x] AC-02: Ticket bez branch ownera i bez zmian własnego katalogu nie jest
      przypisywany wszystkim checkoutom.
- [x] AC-03: Tickety przypisane do branchy nadal zgłaszają rzeczywisty konflikt.

## Ryzyka i Uwagi

- Rzeczywista kolizja dirty/committed paths pozostaje osobną, obowiązkową
  kontrolą i nie zależy od przypisania ticketu.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-146/`.
