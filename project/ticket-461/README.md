# Ticket 461: Compare Python version declarations by PEP 440 normal form

- **ID**: ticket-461
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-11-19

## Cel i Zakres

Owner request (2026-11-18): stop standards from producing errors that make no sense. During the
fleet adoption of 0.20.162, GOV-VERSION-001 rejected at least six adopters whose VERSION
`0.1.0-dev` and `pyproject.toml` `0.1.0.dev0` are the same PEP 440 version (build tools normalize
the former into the latter). Python declarations now compare by a dependency-free PEP 440 key.
Exact comparison stays for unparseable values and for semver manifests.

## Acceptance criteria

- AC-01: `tests/version-parity.test.sh` passes, including the new equivalent and distinct cases.
- AC-02: `project/governance-check.sh` and the hub pull-request scope gate pass.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-461/`.

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
