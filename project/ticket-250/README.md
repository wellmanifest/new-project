# Ticket 250: Trim AGENTS template EOF whitespace

- **ID**: ticket-250
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-09-19

## Cel i Zakres

Usunąć pojedynczą nadmiarową pustą linię na końcu zarządzanego szablonu
`AGENTS.template.md`. Wydanie 0.20.33 przekazuje ją do adoptera i przez to
`git diff --check` odrzuca poprawną, atomową aktualizację standardu.

## Kryteria Odbioru (Acceptance Criteria)
- [ ] AC-01: Szablon kończy się pojedynczym znakiem nowej linii.
- [ ] AC-02: Walidacja źródła i testy przechodzą bez regresji.

## Ryzyka i Uwagi
- Zmiana jest ograniczona do końca pliku i nie zmienia treści kontraktu.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-250/`.
