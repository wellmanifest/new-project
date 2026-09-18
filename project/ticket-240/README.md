# Ticket 240: PR-isolated remote lifecycle check in Hub workflows

- **ID**: ticket-240
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-09-18

## Cel i Zakres
Zapewnienie izolacji sprawdzania cyklu życia gałęzi w workflowach huba `wellmanifest/new-project` (`.github/workflows/governance.yml` oraz `.github/workflows/ci.yml`).
Dotychczas `template/files/new-project-governance.workflow.yml` przekazywał opcję `--focus-branch "$HEAD_REF"`, lecz lokalne przepływy CI huba sprawdzały cały snapshot repozytorium, powodując, że pojedyncza osierocona gałąź zdalna blokowała wszystkie PR-y (Issue #351).
Ticket dodaje przekazywanie `--focus-branch "$HEAD_REF"` w obu workflowach huba oraz testy funkcjonalne izolacji gałęzi PR w `tests/branch-lifecycle.test.sh`.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: `.github/workflows/governance.yml` przekazuje `--focus-branch "$HEAD_REF"` gdy zmienna środowiskowa `HEAD_REF` jest ustawiona.
- [x] AC-02: `.github/workflows/ci.yml` przekazuje `--focus-branch "$HEAD_REF"` gdy zmienna środowiskowa `HEAD_REF` jest ustawiona.
- [x] AC-03: `tests/branch-lifecycle.test.sh` weryfikuje izolację PR od osieroconych gałęzi za pomocą opcji `--focus-branch` oraz obecność odpowiedniej konfiguracji w workflowach.
- [x] AC-04: Wszystkie testy `tests/branch-lifecycle.test.sh` oraz `./project/governance-check.sh` przechodzą pomyślnie (`GOV-PASS`).

## Ryzyka i Uwagi
- Zmiana nie wpływa na kod produkcyjny ani nie osłabia weryfikacji w kontekście scheduled run (gdzie brak `HEAD_REF` powoduje pełny audyt repozytorium).

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-240/`.
