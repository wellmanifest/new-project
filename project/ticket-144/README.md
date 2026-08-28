# Ticket 144: Allow portable governance runner selection

- **ID**: ticket-144
- **Owner**: agent:codex
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Utworzono**: 2026-08-28

## Cel i Zakres

Usunąć zależność zarządzanych bramek governance od jednej puli GitHub-hosted.
Standard ma pozwolić repozytorium wskazać autoryzowany runner, zachowując
`ubuntu-latest` jako bezpieczny domyślny wybór bez konfiguracji.

## Kryteria Odbioru (Acceptance Criteria)

- [x] AC-01: Workflow wielokrotnego użytku i zarządzany workflow adoptera mają jawny, opcjonalny wybór runnera z fallbackiem `ubuntu-latest`.
- [x] AC-02: Pełny deterministyczny zestaw testów standardu przechodzi bez osłabienia bramek.

## Ryzyka i Uwagi

- Self-hosted runner wykonuje kod workflow; dostęp pozostaje decyzją operatora repozytorium i nie jest rozszerzany przez sam standard.
- Brak zmiennej lub inputu zachowuje dotychczasowe zachowanie.

## Dowody

- `branch-lifecycle.test.sh`: PASS, w tym kontrakt obu wariantów runnera.
- 13/13 deterministycznych zestawów `tests/*.test.sh`: PASS.
- Hub governance: 0 błędów, 0 ostrzeżeń.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-144/`.
