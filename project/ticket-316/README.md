# Ticket 316: Avoid false secret alarms for Python token expressions

- **ID**: ticket-316
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Utworzono**: 2026-10-06

## Cel i Zakres
Wyeliminowanie fałszywych alarmów `GOV-SECRET-001` dla poprawnych wyrażeń w języku Python,
takich jak przekazywanie zmiennych (np. token), wywołania funkcji
(np. pobranie tokenu z resolvera/keyringa) czy przypisania krotek, przy zachowaniu
pełnej detekcji rzeczywistych sekretów zahardkodowanych w literałach łańcuchowych.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: `probable_secret_fields` w `scripts/governance_check.py` oraz `packages/wellman/src/wellman/_bundled/governance_check.py` używa AST dla plików Python (`.py`, `.pyi`, `.pyw`).
- [x] AC-02: Wyrażenia niebędące literałami tekstowymi (np. zmienne, wywołania funkcji, argumenty słów kluczowych) nie wyzwalają `GOV-SECRET-001`.
- [x] AC-03: Zahardkodowane literały tekstowe (o długości >= 12 znaków niebędące placeholderami) nadal wyzwalają `GOV-SECRET-001`.
- [x] AC-04: Dodano testy jednostkowe w `tests/secret_detection_test.py` weryfikujące obsługę AST i brak fałszywych alarmów.

## Ryzyka i Uwagi
- Pliki zawierające błędy składniowe Python (`SyntaxError`) fallbackują do analizy regexem `SECRET_RE`.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-316/`.
