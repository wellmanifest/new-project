# Ticket 477: Reconcile scope of an existing first native adoption

- **ID**: ticket-477
- **Owner**: agent:codex
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-11-25

## Cel i Zakres
SESSION_EXECUTION_AUTHORIZATION. An existing first native adoption can reserve too few installer paths. The allocating
owner needs a way to reconcile that reservation against the exact published receipt
before any material commit.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: The current owner can add verified installer control paths under the same ticket.
- [x] AC-02: The controller refuses unrelated paths and stale or changed evidence before editing.
- [x] AC-03: Planning is read-only, apply is idempotent, and the packaging scope operation still works.

## Ryzyka i Uwagi
- Scope changes use the published receipt, exact installed bytes, and the current lease revision and fence.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-477/`.

<!-- ticket-radar:start -->
## Ticket Radar

Initial planned-scope estimate; advisory only, not execution or merge approval.

| Measure | Initial assessment |
| --- | --- |
| Impact score | 60/100 |
| Complexity | L |
| Estimated effort | 61 min |
| Planning budget | 30 min |
| Split recommended | yes |

Diagnostics: RADAR-ACCEPTANCE-MISSING, RADAR-BUDGET-EXCEEDED.
<!-- ticket-radar:end -->
