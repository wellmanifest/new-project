# Ticket 467: Add opt-in warn-only pre-commit standard update action to reduce adoption churn

- **ID**: ticket-467
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-11-20

## Cel i Zakres
Dodać opcjonalny tryb `"action": "warn-only"` dla polityki `updates` w `.governance/standard-adoption.json` (`governance/standard-adoption.schema.json` + `scripts/precommit_standard_update.py`), aby repozytoria mogły otrzymywać czytelne ostrzeżenie o dryfie standardu (`goal governance adopt --latest --check`) bez blokowania zwykłych commitów produktowych i bez wymuszania wielokrotnych PR-ów adopcyjnych w ciągu dnia. Domyślna polityka `"prepare-and-abort"` pozostaje bez zmian.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: `governance/standard-adoption.schema.json` i `scripts/precommit_standard_update.py` akceptują `action` w `{"prepare-and-abort", "warn-only"}` przy zachowaniu domyślnego `"prepare-and-abort"` i fail-closed dla niepoprawnych konfiguracji.
- [x] AC-02: W trybie `warn-only` wywoływane jest wyłącznie odczytowe `goal governance adopt --latest --check --target-root <target>` (w tym przez `koru-goal`), a dryf lub brak narzędzia emituje ostrzeżenie `GOV-STANDARD-UPDATE-001 (warn-only)` na `stderr` i zwraca kod `0`.
- [x] AC-03: `tests/precommit-standard-update.test.sh`, `./project/governance-check.sh` i `wellman check` przechodzą bez błędów.

## Ryzyka i Uwagi
- Risk 1: Zachowanie wstecznej kompatybilności dla istniejących repozytoriów — domyślna polityka pozostaje `prepare-and-abort`, a niepoprawne lub nieczytelne `standard-adoption.json` nadal blokują commit kodem `2`.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-467/`.

<!-- ticket-radar:start -->
## Ticket Radar

Initial planned-scope estimate; advisory only, not execution or merge approval.

| Measure | Initial assessment |
| --- | --- |
| Impact score | 64/100 |
| Complexity | L |
| Estimated effort | 72 min |
| Planning budget | 30 min |
| Split recommended | yes |

Diagnostics: RADAR-ACCEPTANCE-MISSING, RADAR-BUDGET-EXCEEDED.
<!-- ticket-radar:end -->
