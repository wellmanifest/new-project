# Ticket 167: Document controlled streaming de-escalation

- **ID**: ticket-167
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: VALIDATION
- **Utworzono**: 2026-08-31

## Cel i Zakres
Udokumentować pozostałe prace potrzebne do kontrolowanego streamowania zmian
bez zamieniania technicznych kolizji w trwałe blokady.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: Dokument rozróżnia konflikt semantyczny od technicznego i opisuje
  bezpieczne ścieżki deeskalacji.
- [x] AC-02: TODO zawiera uporządkowane, weryfikowalne kolejne kroki standardu.

## Ryzyka i Uwagi
- Risk 1: Dokument nie zmienia authority, schematów ani runtime; każde
  wdrożenie pozostaje osobnym ticketem i release'em standardu.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-167/`.
