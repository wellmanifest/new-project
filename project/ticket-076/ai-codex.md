---
participant-id: agent:codex
participant: codex
role: agent
ticket: ticket-076
---
# Participant: codex (AI agent)

## Understanding

Obecny standard poprawnie zabrania uznawania tekstu sesji za trusted approval,
ale generowany preprompt błędnie zalicza `trusted merge approval` do skutków
wymagających kolejnego pytania. To miesza władzę do uruchomienia chronionego
procesu z dowodem wytwarzanym przez ten proces. Zmiana ma zachować fail-closed
approval, a jednocześnie pozwolić Validatorowi domknąć publikację bez
redundantnej zgody człowieka.

## Execution plan

1. Związać intent z bieżącym `origin/main` i wyłącznie nośnikami standardu
   autoryzacji oraz ich testami.
2. Doprecyzować `P-CORE-008`, procedurę approval i moduł ticket-lifecycle:
   sesja autoryzuje protected delivery invocation, Validator wytwarza evidence.
3. Ujednolicić AGENTS, preprompt, agent participant i fallback generatora.
4. Dodać regresje dla obu granic: brak ponownego promptu i zakaz traktowania
   sesji jako trusted evidence.
5. Uruchomić focused tests, pełny kontrakt huba i governance-check, następnie
   opublikować reviewable PR przez chroniony Validator.

## Actual changes

- Initialized the bounded ticket and recorded `SESSION_EXECUTION_AUTHORIZATION`
  from the request to execute this work.
- Updated `P-CORE-008`, `P-CORE-015` and their procedural projections so the
  session authorizes declared protected delivery invocation, while exact-head
  protected evidence alone authorizes merge.
- Updated the ticket-lifecycle module to version 2 with explicit process
  invocation and trusted evidence predicates.
- Synchronized hub and target AGENTS, preprompt, participant template and both
  `new-ticket.sh` paths so protected publication never triggers a redundant
  chat question and direct agent merge remains forbidden.
- Added adoption and generator regressions for the new boundary; all shell
  suites and Ruff pass.
- Kept the ticket `IN_PROGRESS / PUBLICATION` pending exact-head protected
  review and merge; no concurrent dirty main-worktree content entered the diff.
- The first Goal publication attempt correctly rejected a commit message that
  omitted Goal's canonical `[ticket-076]` prefix. A conventional-commit scope
  was also rejected, so the local commit was rebound to the exact protected
  format before any push.

## Blockers

- None inside the recorded intent; proceed without a second confirmation.
- New authority remains required only for destructive action, secret access,
  new external coordination or material objective expansion. Protected
  Validator delivery is inside this authorization; its exact-head approval is
  independent evidence, not session prose.
