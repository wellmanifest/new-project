---
participant-id: agent:codex
participant: codex
role: agent
ticket: ticket-075
---
# Participant: codex (AI agent)

## Understanding

Ticket 074 został zintegrowany i zamknięty, lecz jego nowe profile delivery
istnieją wyłącznie na ruchomym `main`. Ostatni immutable release `v0.16.2`
wskazuje wcześniejszy commit `63a03d0`, dlatego downstream Hub deterministycznie
odrzuca pole `delivery.profiles`. Ten ticket publikuje zintegrowany kontrakt
jako minor `0.17.0` bez dalszej zmiany zachowania.

## Execution plan

1. Związać wydanie z `main@59a0298`, ticketem 074 i sześcioma nośnikami.
2. Zsynchronizować VERSION, oba manifesty, aktywne asercje testów i changelog.
3. Uruchomić focused oraz pełny kontrakt Linux, Ruff i governance.
4. Opublikować PR, uzyskać exact-head Validator approval i scalić identyczne
   drzewo.
5. Powtórzyć testy na czystym merge `main`, a następnie utworzyć immutable tag
   i GitHub Release `v0.17.0` przez zweryfikowany Goal.
6. Zweryfikować peeled SHA i zamknąć ticket osobnym governance-only PR.

## Actual changes

- Initialized the bounded ticket and recorded `SESSION_EXECUTION_AUTHORIZATION`
  from the request to execute this work.

## Blockers

- None inside the recorded intent; proceed without a second confirmation.
- New authority is still required for destructive action, secret access, new
  external coordination, material objective expansion and trusted merge.
