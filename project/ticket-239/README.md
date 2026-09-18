# Ticket 239: reconcile CONTRIBUTING policy DSL grammar and rule enforcement

- **ID**: ticket-239
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-09-18

## Cel i Zakres
Aktualizacja gramatyki Policy DSL w `CONTRIBUTING.md` do wersji 24, deklaracja reguł `C-DONE-001` i `C-DONE-002`, aktualizacja digestów i wersji w `dsl-manifest.json` oraz powiązanie reguł z enforcementem manualnym w `governance/rule-enforcement.json`. Usuwa to błędy parsowania Policy DSL i zapewnia pełną spójność traceability z ekosystemem autogrammar.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: `CONTRIBUTING.md` posiada wersję 24 i zgodne reguły `C-DONE-001` i `C-DONE-002`.
- [x] AC-02: `dsl-manifest.json` posiada zaktualizowane hashe sha256 oraz version 24.0.0.
- [x] AC-03: `governance/rule-enforcement.json` zawiera wpisy dla `C-DONE-001` i `C-DONE-002`.
- [x] AC-04: `bash tests/rule-enforcement.test.sh` oraz `./project/governance-check.sh` przechodzą pomyślnie (`GOV-PASS`).

## Ryzyka i Uwagi
- Brak wpływu na kod runtime aplikacji; zmiana czysto kontraktowo-zarządcza.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-239/`.
