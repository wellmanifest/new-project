# Ticket 087: Mandate agents invoke validator-agent for trusted merge approval

- **ID**: ticket-087
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-08-15

## Cel i zakres

LLM-y i agenci codingowi wielokrotnie proszą człowieka o „użycie
validator-agent”, zamiast sami wywołać chroniony `direct-pr`. Ustandaryzować
w hubie `wellmanifest/new-project` (AGENTS + szablon adopcji): **MUST invoke**
`subactor/validator-agent` przez `bin/dispatch-direct-pr.sh` przy publikacji
wymagającej trusted approval; **MUST NOT** prosić człowieka o zastąpienie App.

Runtime Validatora pozostaje HOME w `subactor`; ten ticket tylko ADOPT-uje
kontrakt w hubie.

## Acceptance criteria

- [x] AC-01: `AGENTS.md` i `template/files/AGENTS.template.md` nakazują
      `dispatch-direct-pr.sh` (freeze + re-read head + optional `--merge`).
- [x] AC-02: Jawny zakaz: nie prosić człowieka o approve zamiast Validator App;
      chat ≠ trusted merge approval.
- [x] AC-03: `./project/governance-check.sh` → GOV-PASS; CONTRIBUTING /
      GOVERNANCE_ENFORCEMENT wskazują tę samą procedurę.

## SESSION_EXECUTION_AUTHORIZATION

User: execute autonomously; standardize so LLMs use validator-agent without
re-explaining; use the closest wellmanifest pack (`new-project`).

## Uczestnicy

- Human participant: unresolved
- Agent participant: `ai-composer.md`
