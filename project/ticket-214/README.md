# Ticket 214: Add a target-owned ticket activity policy override

- **ID**: ticket-214
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-09-11

## Cel i zakres

Dodać bezpieczny, target-owned opt-in dla `git-ancestry`. Managed
`ticket-activity.json` pozostaje konserwatywne (`status-projection`), a adopter
może dodać `.governance/ticket-activity.override.json` z samym
`missingPolicy=git-ancestry`.

## Kryteria Odbioru (Acceptance Criteria)

- [ ] AC-01: Brak override zachowuje `status-projection`.
- [ ] AC-02: Poprawny override uruchamia Git-derived terminal resolution.
- [ ] AC-03: Niepoprawny override kończy się fail-closed.

## Ryzyka i uwagi

- Override nie może zmieniać receipt registry ani terminal outcome rules.
- Otwarty ticket branch pozostaje aktywny dzięki istniejącej kontroli ancestry.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-214/`.
