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

- [x] AC-01: poprawne ścieżki `IN_PROGRESS` i `DONE` uruchamiają guard; jego
  negatywny werdykt blokuje commit.
- [x] AC-02: brak zadeklarowanego runnera blokuje commit i aktywację hosta z
  jawną remediacją.
- [x] AC-03: bootstrap jest atomowy, pełne testy i exact-base governance PASS.

## Evidence before publication

- `bash tests/agent-hosts.test.sh`: PASS; spy potwierdza trzy wywołania guarda,
  propagację negatywnego werdyktu i fail-closed brak runnera.
- `bash tests/adoption-lock.test.sh`: PASS.
- Fail-fast `tests/*.test.sh`: 10/10 PASS.
- Governance `ecafbb4..0b9b7e4`: `GOV-PASS`, 0 errors, 0 warnings.

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
