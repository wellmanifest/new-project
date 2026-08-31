# Ticket 168: Permit audited atomic upgrade from a drifted managed target

- **ID**: ticket-168
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-08-31

## Cel i Zakres

Naprawić ścieżkę atomowej aktualizacji standardu dla repozytorium, którego
poprzednio zarządzany plik zmienił się poza starym lockiem. Aktualizacja ma
pozostać fail-closed: ticket musi jawnie związać digest rzeczywistego pliku
bazowego, a nowy plik nadal musi odpowiadać immutable lockowi.

## Kryteria Odbioru (Acceptance Criteria)
- [ ] AC-01: Poprawny digest driftującego wcześniej managed pliku pozwala na
      atomową aktualizację.
- [ ] AC-02: Brakujący lub błędny digest nadal kończy się `GOV-SYNC-001`.

## Ryzyka i Uwagi
- Risk 1: Nie wolno zamienić tego wyjątku w ogólne ignorowanie driftu;
  mitygacją jest obowiązkowy, jednorazowo skonsumowany SHA-256 base targetu.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-168/`.
