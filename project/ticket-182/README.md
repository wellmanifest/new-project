# Ticket 182: Neutralize terminal review governance reruns

- **ID**: ticket-182
- **Owner**: requesting user, represented by the conversation
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Utworzono**: 2026-09-01
- **GitHub issue**: https://github.com/wellmanifest/new-project/issues/292
- **Authorization**: SESSION_EXECUTION_AUTHORIZATION

## Cel i zakres

Usunąć fałszywie czerwone uruchomienia reusable governance, które zostały
wyzwolone przez `pull_request_review`, lecz w chwili egzekwowania dotyczą już
terminalnego (merged albo closed) pull requestu. Chroniony workflow ma pobrać
bieżący stan PR z GitHub API i rozstrzygnąć go przed rozwiązywaniem ownership
ticketu.

Stan `open` pozostaje fail-closed: musi przejść niezmienioną walidację ticketu,
intencji, zakresu i exact-head approval. Nieznany, niespójny lub źle związany
snapshot stanu PR ma zatrzymać workflow stabilnym diagnostykiem.

## Kryteria odbioru

- [x] AC-01: Reusable workflow pobiera live PR state i waliduje repozytorium,
  numer oraz exact event head przed krokiem ticket ownership.
- [x] AC-02: `closed`/`merged` kończy diff/approval enforcement neutralnie,
  bez próby rozwiązywania aktywnego ticketu.
- [x] AC-03: `open` nadal uruchamia pełne ownership, intent, scope i approval
  enforcement; błędny snapshot pozostaje fail-closed.
- [ ] AC-04: Testy pozytywne i negatywne oraz pełny kontrakt governance
  przechodzą; PR zamyka issue #292 przez chronionego Validatora.

## Ryzyka i uwagi

- Najważniejszym ryzykiem jest przypadkowy bypass otwartego PR. Ogranicza go
  zamknięty snapshot, exact bindings oraz jawny warunek `gate == enforce` na
  wszystkich krokach diff/approval.
- Brak lub nieznany stan nie jest neutralny: kończy się błędem i bez merge.
- Zakres nie obejmuje adopterskich repinów, release, tagów ani cleanup.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-182/`.
