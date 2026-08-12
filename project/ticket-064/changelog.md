# Ticket changelog (ticket-064)

## [0.1.0] - 2026-08-12

- Zarejestrowano regresję: poprawne repozytorium bez pierwszego commita
  przerywa fleet audit workspace podczas `git rev-parse HEAD`.
- Dodano zawężone rozpoznanie porcelain v2 `branch.oid (initial)` i nullable
  evidence `head` dla pustych checkoutów.
- Dodano regresję duplicate empty clone oraz clean state z pojedynczym unborn
  primary; błędy uszkodzonego HEAD nadal pozostają fail-closed.
