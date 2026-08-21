# Ticket 102: Allow proven managed target takeover during adoption

- **ID**: ticket-102
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-08-21

## Cel i Zakres

Permit an existing target to become a changed managed payload during an atomic
standard upgrade only when the adoption intent authorizes the exact path and
binds the exact SHA-256 digest observed at its accepted Git base.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: The Platform 0.18.2 pilot reproduces `GOV-SYNC-001` for a real
  pre-existing worktree guard target.
- [ ] AC-02: A matching digest-bound takeover passes while missing, wrong and
  unused declarations fail closed.
- [ ] AC-03: Head managed hash, lock binding and ordinary scope gates remain
  unchanged.
- [ ] AC-04: Full governance validator and exact-base governance pass.
- [ ] AC-05: The change is delivered by exact-head Validator approval.

## Ryzyka i Uwagi

- Risk: a broad exception could launder target content; mitigation is exact
  path, exact base digest, accepted-base Git observation and mandatory use.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-102/`.
