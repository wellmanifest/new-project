# Ticket 458: Stop unprovable baseline levels and incomplete managed copies from failing adopters

- **ID**: ticket-458
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-11-18

## Cel i Zakres

Owner request (2026-11-18): stop the standards from producing errors an adopter
cannot fix. Observed while adopting 0.20.156 in semcod/diagit (#80),
subactor/reflex (#58) and semcod/monag (#173):

1. `managed-copies.json` omits `.governance/docs/information/continuity-namespaces.md`.
   The wellmanifest/docs checker then rejects that managed copy in every adopter;
   semcod/monag went from `ok: true` to four DOCS_* errors.
2. The baseline profile demands S3 (a required CI check) for worktrees, logs and
   docs, but the adopter workflow runs none of their checkers, and worktree
   placement is checkable only by local hooks. No adopter can satisfy this, so
   none can reach `enforce`.

Changes: baseline requires worktrees and docs at S2 and drops logs
(runtime-service keeps logs at S5). The inventory is derived from the package
manifest. One regression test guards both. The pre-commit carrier rule ships as
a separate ticket.

## Acceptance criteria

- AC-01: `tests/standard-pack-check.test.sh` passes with the derived inventory
  and the baseline guard; the wellmanifest/docs checker accepts monag with the
  new inventory (`ok: true`, 4 managed copies verified).
- AC-02: `project/governance-check.sh` and the hub pull-request scope gate pass.

## Ryzyka i Uwagi

- Lowering baseline levels relaxes the profile, but only for levels the
  standard gave adopters no means to prove; runtime-service still requires logs.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-458/`.

<!-- ticket-radar:start -->
## Ticket Radar

Initial planned-scope estimate; advisory only, not execution or merge approval.

| Measure | Initial assessment |
| --- | --- |
| Impact score | 36/100 |
| Complexity | M |
| Estimated effort | 37 min |
| Planning budget | 30 min |
| Split recommended | yes |

Diagnostics: RADAR-ACCEPTANCE-MISSING, RADAR-BUDGET-EXCEEDED.
<!-- ticket-radar:end -->
