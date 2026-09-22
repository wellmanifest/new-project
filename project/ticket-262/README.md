# Ticket 262: Raise default WIP capacity for multi-agent repositories

- **ID**: ticket-262
- **Owner**: human-approved
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-09-22

## Cel i Zakres

Podnieść domyślny limit aktywnych ticketów na workstream z 3 do 8, aby
równolegle obsłużyć zespoły używające wielu agentów (Devin, Codex, Claude,
Agy i podobne), bez wyłączania lease, kontroli zakresów ani overlap guard.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: `governance/manifest.default.json` ustawia limit na 8.
- [x] AC-02: Test walidatora wymaga wartości 8.
- [ ] AC-03: Zmiana przechodzi pełny zestaw testów i może zostać adoptowana przez
  immutable release bez lokalnego override manifestu.

## Ryzyka i Uwagi
- Risk 1: {Opis ryzyka i mitygacja}

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-262/`.
