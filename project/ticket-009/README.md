# Ticket 009: Pilotaż adopcji z równoległymi agentami

- **ID**: ticket-009
- **Owner**: unresolved:human
- **Status**: BACKLOG
- **Workflow state**: BACKLOG
- **Utworzono**: 2026-08-04

## Cel i zakres

Sprawdzić standard w repozytorium z co najmniej dwoma rozłącznymi
workstreamami i odseparowanymi agentami/worktree. Pilot ma potwierdzić
rezerwacje, routing jednego ticketu na PR oraz integrację Validator App.

## Kryteria odbioru

- [ ] Rozłączne zakresy mogą pracować równolegle.
- [ ] Nakładające się zakresy i niejednoznaczny routing są odrzucane.
- [ ] `PLAN`/`BLOCKED` nie blokują nowego `IN_PROGRESS`.
- [ ] Approval Validator App wiąże dokładny HEAD, repozytorium, PR i ticket.
