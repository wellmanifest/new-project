# Ticket 158: Support system Python on self-hosted governance runners

- **ID**: ticket-158
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-08-30

## Cel i Zakres

Naprawić regresję ujawnioną przez adopcję 0.19.11 w `subactor/agents`:
zarządzany check wybiera self-hosted runner poprawnie, lecz bezwarunkowe
`actions/setup-python` nie publikuje Python 3.11 dla Ubuntu 25.10. Standard ma
używać pinned setup na GitHub-hosted i istniejącego `python3` na self-hosted,
zachowując identyczną bramkę. Wydać poprawkę jako immutable 0.19.12.

## Kryteria Odbioru (Acceptance Criteria)

- [x] AC-01: Test kontraktu wymusza warunkowy setup i jawny preflight `python3`.
- [x] AC-02: Pełny deterministyczny zestaw testów standardu przechodzi.
- [ ] AC-03: `subactor/agents` adoptuje dokładny release i realny self-hosted
      `governance / enforce` przechodzi.

## Ryzyka i Uwagi

- Self-hosted runner musi sam dostarczać `python3`; workflow sprawdzi to jawnie
  i fail-closed, bez instalowania pakietów ani mutowania hosta.
- SESSION_EXECUTION_AUTHORIZATION: Founder polecił kontynuować, wdrażać i
  testować; chroniona publikacja nadal wymaga niezależnego Validatora.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-158/`.
