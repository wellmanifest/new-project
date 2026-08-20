# Ticket 098: Allow staged governance-only closures through the host hook

- **ID**: ticket-098
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-08-20

## Cel i Zakres

Make the authoritative host-agnostic pre-commit hook permit the required
governance-only closure after a trusted merge without weakening the
`IN_PROGRESS` boundary for implementation. The hook must decide from the
staged ticket README and staged paths, not from an unstaged working-tree view.

A `DONE` ticket may commit only its own `project/ticket-NNN/**` evidence plus
the two repository-level governance indexes (`TODO.md`, `project/TICKETS.md`).
Any source, generated artifact, other ticket directory, deletion or empty
closure remains rejected. Ordinary `IN_PROGRESS` commits retain current
behavior and the worktree-overlap guard remains chained last by adopters.

## Kryteria Odbioru (Acceptance Criteria)

- [x] AC-01: The autonomous repair request is recorded as bounded session
      authorization without creating human-owned content.
- [x] AC-02: The hook reads ticket status from the Git index, preventing a
      staged/worktree status mismatch from bypassing the boundary.
- [x] AC-03: A `DONE` ticket can commit its own closure evidence plus TODO and
      ticket index, but implementation, foreign-ticket paths and deletions are
      rejected with stable `GOV-AGENT-HOST-003` diagnostics.
- [x] AC-04: Existing main, missing-ticket, BACKLOG and IN_PROGRESS fixtures
      retain their behavior; repeated installer adoption copies the fixed hook.
- [ ] AC-05: Focused and full hub suites, Bash syntax and exact-base governance
      pass before exact-head Validator review.

## Ryzyka i Uwagi

- The narrow path allowlist is intentionally stricter than general
  `governancePaths`; a closure cannot edit another ticket or generated file.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-098/`.
