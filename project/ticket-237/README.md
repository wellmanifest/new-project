# Ticket 237: fix scheduled governance carrier fallback and add unmerged branch hygiene

- **ID**: ticket-237
- **Owner**: codex
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-09-18

## Cel i Zakres
1. Rozwiązanie problemu fałszywych błędów `GOV-MATERIAL-001` podczas uruchomień zaplanowanych (scheduled / workflow_dispatch) w `new-project-governance.workflow.yml` poprzez usunięcie sztucznego fallbacku `--changed-file project/TICKETS.md` (Issue #371).
2. Dodanie szablonu workflow `new-project-branch-hygiene.workflow.yml` i zarejestrowanie go w `governance/package-manifest.json`, co automatyzuje usuwanie zdalnej gałęzi po zamknięciu PR bez scalenia i zapobiega kaskadowym awariom `GOV-BRANCH-LIFECYCLE-002` (Issue #372).

## Kryteria Odbioru (Acceptance Criteria)
- [ ] AC-01: Szablon `template/files/new-project-governance.workflow.yml` nie przekazuje `--changed-file project/TICKETS.md`, gdy brak zakresu PR.
- [ ] AC-02: Szablon `template/files/new-project-branch-hygiene.workflow.yml` jest poprawnym plikiem YAML i został zarejestrowany w `governance/package-manifest.json` z celem `.github/workflows/new-project-branch-hygiene.yml`.
- [ ] AC-03: Zestaw testów `tests/required-checks.test.sh` oraz dedykowany test `tests/branch_hygiene_template_test.py` przechodzą na zielono.
- [ ] AC-04: Bramka `./project/governance-check.sh` kończy się wynikiem GOV-PASS.

## Ryzyka i Uwagi
- Workflow branch hygiene nie jest wymaganą bramką CI (uruchamia się wyłącznie dla zdarzenia `pull_request: closed`), dzięki czemu nie wpływa na listę `requiredChecks`.

## Granica katalogu
Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-237/`.
