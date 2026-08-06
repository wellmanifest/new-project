# Ticket 032: Emit recomputable decision records from validator-agent direct-pr

- **ID**: ticket-032
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Utworzono**: 2026-08-06

## Cel

Ticket-031 dostarczył kontrakt i bramkę w hubie, ale **validator-agent nie emitował**
wpisu. Ten ticket domyka emisję: po deterministycznym APPROVE review zawiera
blok ` ```dsl DECISION … ` (przeliczalny, z INPUT + APPLIED_RULE).

## Acceptance criteria

- [x] AC-01: Po approve review body zawiera fence `dsl` z `DECISION`, `HEAD_SHA`, `INPUT`, `VERDICT AUTHORITY DETERMINISTIC`.
- [x] AC-02: Raport direct-pr niesie pole `decision_dsl`.
- [x] AC-03: Testy unit pokrywają obecność bloku i regułę P-CORE-015.
- [ ] AC-04: (opcjonalnie) append do `project/{ticket}/decisions.md` na head PR — osobny follow-up (wymaga pusha App).

## Deliverable

PR `subactor/validator-agent#13`.
