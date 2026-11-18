# Ticket 459: Admit carrier-only follow-up commits on branches with material delivery

- **ID**: ticket-459
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-11-18

## Cel i Zakres

Owner request (2026-11-18): stop the standards from producing errors that make
no sense. In semcod/monag#174 the gate asked for a delivery contract after the
material commit. The pre-commit hook rejected the follow-up commit with
GOV-AGENT-HOST-007 because the staged change held only ticket carriers, although
the branch already delivered `pyproject.toml`. The only way through was a
history rewrite and a force push.

The hook now inspects `merge-base(HEAD, origin/<targetBranch>)..HEAD` before
rejecting, and admits the carrier-only commit only when that range already holds
a material path. Branches without one, and checkouts without the target ref,
are still rejected. CI keeps checking the whole range (GOV-MATERIAL-001).

## Acceptance criteria

- AC-01: `tests/agent-hosts.test.sh` covers rejection without a target, admission
  after material delivery, and rejection when nothing material lies beyond the target.
- AC-02: `project/governance-check.sh` and the hub pull-request scope gate pass.

## Ryzyka i Uwagi

- The hook trusts the local `origin/<target>` ref; the CI range check remains the authority.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-459/`.

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
