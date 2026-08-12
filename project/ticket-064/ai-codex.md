---
participant-id: agent:codex
participant: codex
role: agent
ticket: ticket-064
---
# Participant: codex

## Understanding

`workspace_lifecycle_check.py` zakłada, że każdy checkout ma rozwiązywalne
`HEAD`. Poprawne repo bez pierwszego commita łamie to założenie i abortuje cały
fleet audit kodem `GOV-WORKSPACE-LIFECYCLE-003`, mimo że jego common git dir,
branch, status i remote nadal są audytowalne.

## Execution plan

1. Zapisać bounded intent oraz regresję rzeczywistego przypadku unborn HEAD.
2. Rozpoznać wyłącznie porcelain v2 `branch.oid (initial)` jako brak commita.
3. Reprezentować taki HEAD przez JSON `null` i zachować wszystkie inne błędy.
4. Uruchomić focused/full contract, todo2code i exact-head Validator.
5. Scalić i potwierdzić post-merge przed zamknięciem ticketu.

## Actual changes

- Reprodukowano abort na `/home/tom/github/subactor/www-sub-actor` bez
  modyfikowania tego repozytorium.
- Dodano `checkout_head()`, które uznaje brak SHA wyłącznie wtedy, gdy Git
  porcelain v2 raportuje `branch.oid (initial)`; wszystkie inne błędy są dalej
  propagowane jako fail-closed.
- Fixture zawiera pusty primary i jego duplicate clone. Duplicate ma
  `head: null`, a po usunięciu duplikatu pozostawiony unborn primary przechodzi.
- Live audit `/home/tom/github/subactor` zakończył inspekcję bez kodu 003 i
  ujawnił 50 zachowanych live workspace. Pełny root nadal poprawnie blokuje się
  na uszkodzonym `test-repo` z HEAD wskazującym `refs/heads/.invalid`.
- Focused regression, wszystkie suite Linux CI, kontrakty JSON, kompletność
  traceability i Ruff przechodzą po zmianie.
- todo2code `20260812T012417Z-3710f5ae` wymagał GLM 5.2 na implementacji
  `a1ac355`, lecz skonfigurowany klucz nadal otrzymał limit tygodniowy. Run
  zakończył się fail-closed na NL, bez grafu i bez fallbacku.

## Blockers

- Brak.
