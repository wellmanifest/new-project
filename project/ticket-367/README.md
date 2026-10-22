# Ticket 367: Name the required location of a misplaced delivery field in GOV-INTENT-002 (issue 517)

- **ID**: ticket-367
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-10-22

## Cel i Zakres
Issue #517: GOV-INTENT-002 odrzucał `delivery.interfaceChanges` bez wskazania,
że pole należy do `delivery.architecture.interfaceChanges`. Komunikat nazywa
teraz wymaganą ścieżkę każdego rozpoznanego, źle umieszczonego pola.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: fixture: `delivery.interfaceChanges` → `move interfaceChanges to delivery.architecture.interfaceChanges`; pole delivery w architekturze i limit w architekturze wskazują swoje ścieżki; pole nadal odrzucone; nieznane pole bez podpowiedzi; kopia Wellman identyczna.
- [x] AC-02: runbook `GOV-INTENT` (krok 4), wersja 0.20.114.

## Ryzyka i Uwagi
- Synonim nie jest akceptowany: deterministyczny błąd zamiast poluzowania walidacji.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-367/`.
