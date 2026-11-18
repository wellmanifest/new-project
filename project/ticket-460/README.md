# Ticket 460: Deduplicate worktree registry reads during overlap checks

- **ID**: ticket-460
- **Owner**: agent:codex
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-11-18

## Cel i Zakres

Reduce repeated Git registry discovery in the overlap checker while retaining
the full fail-closed inventory and conflict findings. The change is limited to
the checker and its shell fixture.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: A registered worktree is discovered once per repository registry,
  including linked worktrees outside the initial candidate set.
- [x] AC-02: Independent clones with the same network remote remain separate
  identities and malformed or unknown registry data still fails closed.
- [x] AC-03: Existing overlap fixture passes and records deterministic command
  count evidence for the reduced registry reads.

## Ryzyka i Uwagi
- Risk 1: {Opis ryzyka i mitygacja}

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-460/`.

<!-- ticket-radar:start -->
## Ticket Radar

Initial planned-scope estimate; advisory only, not execution or merge approval.

| Measure | Initial assessment |
| --- | --- |
| Impact score | 52/100 |
| Complexity | M |
| Estimated effort | 51 min |
| Planning budget | 30 min |
| Split recommended | yes |

Diagnostics: RADAR-ACCEPTANCE-MISSING, RADAR-BUDGET-EXCEEDED.
<!-- ticket-radar:end -->
