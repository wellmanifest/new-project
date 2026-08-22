# Ticket 110: Compose managed ticket and worktree pre-commit gates

- **ID**: ticket-110
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-08-22

## Cel i Zakres

Zarządzany `.githooks/pre-commit` kończy poprawną ścieżkę `IN_PROGRESS` lub
governance-only `DONE` przez `exit 0`, zanim uruchomi worktree guard. Ponieważ
ten sam hook jest od wersji 0.18.5 rozsyłany jako plik `managed`, adopcja może
nadpisać poprawnie skomponowany hook adoptera i wyłączyć ochronę przed
równoległymi procesami dotykającymi tego samego zakresu.

Ticket komponuje obie deterministyczne bramki w jednym źródłowym hooku. Każda
dozwolona ścieżka ticketowa musi przed sukcesem uruchomić repozytoryjny
`worktree_guard.py`; brak runnera albo negatywny werdykt pozostają fail-closed.
Kontrakt hostów deklaruje kompletny runtime hooka, dzięki czemu bootstrap nie
może już skopiować samego hooka bez runnera, checkera i konfiguracji.

## Kryteria Odbioru (Acceptance Criteria)

- [ ] AC-01: poprawny commit `IN_PROGRESS` uruchamia worktree guard przed
  sukcesem, a jego negatywny werdykt blokuje commit.
- [ ] AC-02: poprawna governance-only ścieżka `DONE` również uruchamia guard;
  brak `.governance/worktree_guard.py` i `scripts/worktree_guard.py` blokuje
  commit z jawną remediacją.
- [ ] AC-03: `bash tests/agent-hosts.test.sh`, pełny zestaw testów shellowych i
  governance gate przechodzą.

## Ryzyka i Uwagi

- Risk 1: źródłowe repozytorium trzyma runner w `scripts/`, a adopter w
  `.governance/`; hook wybiera wyłącznie te dwie jawne lokalizacje i odrzuca
  brak obu.
- Risk 2: rzeczywisty konflikt w istniejących worktree może zablokować commit
  implementacji. To oczekiwane zachowanie; konflikt musi zostać usunięty lub
  zgodnie zadeklarowany, a nie ominięty przez `--no-verify`.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-110/`.
