# Ticket 110: Separate the managed adopter pre-commit payload

- **ID**: ticket-110
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-08-22

## Cel i Zakres

`.githooks/pre-commit` pełnił dwie role naraz: był aktywnym hookiem huba i
źródłem pliku `managed` dla adopterów. Próba skomponowania go z worktree guardem
ujawniła, że zmiana dystrybuowanego payloadu natychmiast zmienia również bramkę
wykonującą commit w repozytorium źródłowym. Przy istniejących, brudnych worktree
huba tworzy to paradoks samomodyfikującej się kontroli.

Ten slice rozdziela odpowiedzialności bez zmiany zachowania: dodaje dedykowany
szablon payloadu o tej samej logice lifecycle i przełącza na niego manifest
pakietu. Następny, zależny ticket może bezpiecznie skomponować payload adoptera
z guardem w limicie klasy S, nie modyfikując aktywnego hooka huba.

## Kryteria Odbioru (Acceptance Criteria)

- [x] AC-01: manifest dystrybuuje dedykowany
  `template/files/pre-commit.template.sh` jako `.githooks/pre-commit`.
- [x] AC-02: `bash tests/agent-hosts.test.sh` i
  `bash tests/adoption-lock.test.sh` potwierdzają niezmienione zachowanie
  bootstrapu i poprawny digest nowego źródła.
- [x] AC-03: pełny zestaw testów i governance gate przechodzą na exact base/head.

## Ryzyka i Uwagi

- Risk 1: ten ticket celowo nie komponuje jeszcze worktree guarda; atomowa
  kompozycja runtime jest zakresem bezpośrednio zależnego ticketu.
- Risk 2: aktywny hook huba pozostaje lifecycle-only. Historyczne dirty
  worktree muszą zostać odzyskane albo skwarantannowane decyzją właściciela;
  runbook zabrania ich automatycznego usuwania.
- Risk 3: pierwsza, sześcioplikowa próba została odrzucona przez
  `GOV-BUDGET-001`. Zakres został podzielony zamiast sztucznego zwiększania
  budżetu lub użycia `--no-verify`.

## Evidence before publication

- `bash tests/agent-hosts.test.sh`: PASS.
- `bash tests/adoption-lock.test.sh`: PASS.
- `set -e; for test in tests/*.test.sh; do bash "$test"; done`: 10/10 PASS na
  exact headzie po ostatecznym zawężeniu.
- `./project/governance-check.sh --actor agent --base cd9a15a... --head HEAD`:
  `GOV-PASS`, 0 errors, 0 warnings.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-110/`.
