# Ticket 213: Make Git ancestry the default missing receipt policy for adopters

- **ID**: ticket-213
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-09-11

## Cel i zakres

Wydanie `0.20.24` zmienia tylko domyślną wartość `registry.missingPolicy` w
pakiecie zarządzanym na `git-ancestry`. Dzięki temu checkouty, które nie mają
lokalnego rejestru receiptów, nie utrzymują w nieskończoność scalonych ticketów
jako aktywnych. Adopter może nadal jawnie przypiąć `status-projection`.

## Kryteria Odbioru (Acceptance Criteria)

- [ ] AC-01: Brak rejestru receiptów i ticket obecny na target ref daje
  `authority=git-ancestry`, `reason=delivery-on-target`.
- [ ] AC-02: Explicit `status-projection` pozostaje konserwatywne, a testy
  ticket activity oraz pełna suita standardu przechodzą.

## Ryzyka i uwagi

- Domyślna zmiana dotyczy nowych adopcji oraz upgrade'ów; istniejące checkouty
  zachowują swoją zapisaną politykę do czasu aktualizacji standardu.
- Resolver pozostaje fail-closed dla otwartego ticket branch oraz carrier-only
  zmian, co ogranicza ryzyko przedwczesnego zwolnienia rezerwacji.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-213/`.
