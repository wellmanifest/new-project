# Ticket 420: Scope ActivityReadBatch worktree fence to inspected checkout

- **ID**: ticket-420
- **Owner**: agent:antigravity
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-11-10

## Cel i Zakres
`ActivityReadBatch.__enter__` previously cached raw `git worktree list --porcelain` across all linked worktrees and raw `git for-each-ref` across unconsulted sibling ticket branches, causing concurrent commits or allocations in disjoint sibling worktrees to trigger false-positive `GOV-TICKET-ACTIVITY-001: Git state changed during activity inspection; retry`. Scope the worktree registration fence to the inspected checkout's own stanza and revalidate `for-each-ref` strictly for ticket numbers consulted during the batch.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: Concurrent commits and worktree allocations on disjoint sibling ticket branches do not invalidate `ActivityReadBatch` on the inspected checkout, while mutations to the inspected checkout's own registration, `HEAD`, target ref, or consulted ticket branches still raise `ActivityError`.
- [x] AC-02: `packages/wellman/sync_bundled.py --check`, `tests/ticket_activity_batch_test.py`, `tests/ticket-activity.test.sh`, `tests/worktree-overlap.test.sh`, `./project/governance-check.sh`, and `wellman check` pass cleanly.

## Ryzyka i Uwagi
- Risk 1: Weakening TOCTOU detection on the inspected checkout or consulted ticket branches. Mitigated by fencing `--git-common-dir`, `HEAD`, the inspected checkout's exact `worktree list --porcelain -z` stanza, target refs, and every consulted ticket number's branch object IDs.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-420/`.
