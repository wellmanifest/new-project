# Ticket 117: Scope local worktree commit guard to the current checkout

- **ID**: ticket-117
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-08-25

## Cel i Zakres

Make repository pre-commit checks report only overlap findings that involve the
checkout being committed. Repository-wide and workspace-wide audits continue
to report every discovered conflict.

## Kryteria Odbioru (Acceptance Criteria)

- [x] AC-01: The checker accepts an explicit focus checkout without changing repository identity filtering.
- [x] AC-02: The guard applies focus automatically only for repository commit gates.
- [x] AC-03: Conflicts involving the current checkout still fail closed.
- [x] AC-04: `tests/worktree-overlap.test.sh` passes.

## Ryzyka i Uwagi

- Full repository and workspace audits remain unfiltered, preserving fleet visibility.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-117/`.
