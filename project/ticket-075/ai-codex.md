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
- Synchronized the six release carriers and assertions from `0.16.2` to
  `0.17.0`, preserving the historical 0.16.2 changelog entry.
- Added release notes for repository topology, opt-in Docker, closed XS/S/M/L
  budgets and separation of ticket status from workflow state.
- Passed deterministic governance, all nine Linux shell suites, required-check
  parity and Ruff 0.15.21. Ruff 0.16.1 reports the same 13 pre-existing
  findings on base and candidate, so no unrelated lint repair entered scope.
- Verified Goal 2.1.300 and the absence of a pre-existing v0.17.0 tag/release;
  moved the ticket to `IN_PROGRESS / PUBLICATION` for trusted review.
- Goal opened PR #116, whose exact HEAD `751faec` passed hosted Linux/Windows
  checks and trusted Validator review before merge as `4d0a618` with an
  identical tree.
- Re-ran all nine Linux suites, pinned Ruff and required-check parity on clean
  merged `main`; both post-merge and tag-triggered hosted runs passed.
- Goal direct-main publication created final release `v0.17.0`; annotated tag
  object `45d1e15` peels exactly to merge `4d0a618`. Closed the ticket through
  a separate governance-only delivery.

## Blockers

- None inside the recorded intent; proceed without a second confirmation.
- New authority is still required for destructive action, secret access, new
  external coordination, material objective expansion and trusted merge.
