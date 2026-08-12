# Ticket 064: Obsługa repozytoriów bez pierwszego commita w audycie workspace

- **ID**: ticket-064
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
- **Utworzono**: 2026-08-12

## Cel i zakres

Naprawić fail-closed fleet audit, który traktuje poprawne repozytorium Git bez
pierwszego commita jak uszkodzenie metadanych i przerywa skan wszystkich
workspace. Checker ma jawnie reprezentować unborn HEAD, nadal wykrywać
zduplikowany pusty klon i nie tworzyć sztucznego commita w audytowanym repo.

## Kryteria odbioru

- [x] AC-01: Bieżące zlecenie autonomicznego dokończenia audytu stanowi bounded
  `SESSION_EXECUTION_AUTHORIZATION` dla tej poprawki i publikacji PR.
- [x] AC-02: Pojedyncze repozytorium z unborn HEAD nie przerywa audytu i nie
  otrzymuje fałszywego findingu lifecycle.
- [x] AC-03: Dwa puste checkouty o tej samej tożsamości nadal dają dokładny
  finding duplicate-clone z `head: null`.
- [x] AC-04: Focused workspace regression, pełny Linux contract i Ruff
  przechodzą; hosted Linux/Windows zostaną związane z exact head PR.
- [x] AC-05: todo2code wymaga LLM i pozostaje fail-closed bez substytutu przy
  niedostępnym providerze; niezależny Validator GLM zatwierdza exact head.

## Ryzyka i uwagi

- Nie zmieniać audytowanych repozytoriów ani nie tworzyć w nich commitów.
- Nie osłabiać błędów dla uszkodzonych repozytoriów; `null` jest dozwolony
  wyłącznie po rozpoznaniu porcelain v2 `branch.oid (initial)`.
- Checker pozostaje read-only i ograniczony limitem repozytoriów.

## Dowody zakończenia

- PR #92 został scalony jako `b27e68744966bff2a23a501ce4bf125e9b55ed9a`.
- Post-merge run `31553673726` przeszedł kompletny Linux contract i Windows na
  dokładnym merge commitcie.
- Validator `31553565297` użył GLM 5.2 na exact headzie
  `c088f9557080847fc3ce9532d1337f1af91fdff0`: dwa chunki, `APPROVE`, zero
  findings.
- todo2code `20260812T012500Z-6f465038` wymagał GLM 5.2 na finalnym headzie i
  zakończył się fail-closed na limicie providera, bez grafu i fallbacku.

## Uczestnicy

- Human participant: unresolved; `user-*` jest tworzony wyłącznie przez jego
  właściciela albo zaufaną granicę intake.
- Agent participant: `ai-codex.md`.
