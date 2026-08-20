# Ticket 094: Ship the worktree guard schema and error document to adopters

- **ID**: ticket-094
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-08-20

## Cel i Zakres

Domknięcie dwóch rzeczy, które ticket-092 zapisał jako follow-up, gdy uderzył
w limit 9 plików implementacyjnych: dostarczenie `error/GOV-WORKTREE-OVERLAP.md`
adopterom i przywrócenie schematu JSON dla `worktree-guard.yaml`.

## Kryteria Odbioru (Acceptance Criteria)
- [ ] AC-01: Zbudowany adopter zawiera `.governance/error/GOV-WORKTREE-OVERLAP.md`,
  dzięki czemu trzy wpisy katalogu wskazują na niego zamiast nieść `null`.
- [ ] AC-02: Katalog diagnostyk nadal rejestruje każdy emitowany kod.
- [ ] AC-03: `governance/worktree-guard.schema.json` istnieje ponownie i parsuje się.

## Ryzyka i Uwagi
- Kolejność jest wymuszona: `tests/adoption-lock.test.sh` wymaga, by każda
  niepusta ścieżka `documentation` istniała w `.governance/` adoptera. Wskazanie
  katalogu na dokument przed jego dostarczeniem wywraca ten test.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-claude.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-094/`.
