# Ticket 111: Compose managed pre-commit with worktree guard runtime

- **ID**: ticket-111
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-08-23

## Cel i Zakres

Ticket 110 oddzielił aktywny hook huba od zarządzanego payloadu adoptera.
Teraz payload może atomowo połączyć dwie bramki: staged-snapshot lifecycle oraz
repozytoryjny worktree guard. Każda dozwolona ścieżka `IN_PROGRESS` i
governance-only `DONE` ma uruchomić guard przed sukcesem.

Kontrakt hostów deklaruje runtime payloadu. Dzięki temu bootstrap kopiuje
razem hook, runner, checker i konfigurację, a aktywacja failuje, jeśli któregokolwiek
elementu brakuje.

## Kryteria Odbioru (Acceptance Criteria)

- [ ] AC-01: poprawne ścieżki `IN_PROGRESS` i `DONE` uruchamiają guard; jego
  negatywny werdykt blokuje commit.
- [ ] AC-02: brak zadeklarowanego runnera blokuje commit i aktywację hosta z
  jawną remediacją.
- [ ] AC-03: bootstrap jest atomowy, pełne testy i exact-base governance PASS.

## Ryzyka i Uwagi

- Risk 1: runtimeFiles rozszerza kontrakt hostów; schema wymaga niepustej,
  unikalnej listy, a test bootstrapu dowodzi, że każdy target ma źródło w
  package manifest.
- Risk 2: aktywny hook huba nie jest zmieniany. Ten ticket egzekwuje kompozycję
  u adopterów, nie obchodzi historycznych dirty worktree repozytorium źródłowego.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-111/`.
