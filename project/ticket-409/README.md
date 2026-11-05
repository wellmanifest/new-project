# Ticket 409: Preserve decision codec and typed policy diagnostics

- **ID**: ticket-409
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Utworzono**: 2026-11-05

## Cel i Zakres
Repair decision-v1 field-name/alternative roundtrip and malformed governance profile/lock diagnostics in source and bundle. Keep existing approval authority, valid CLI behavior and all limits. Material version138 belongs to this same repair.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: Source/bundle schema-valid decision identifiers roundtrip; legacy bare tokens/canonical history remain compatible; fixtures grant no approval.
- [x] AC-02: Invalid profile/lock types yield existing typed001 diagnostics through source/bundle CLI; valid/default cases remain accepted.
- [ ] AC-03: Native gate, full canonical and Goal tests, actualCI and independentApp approval precede immutable138 publication.

## Ryzyka i Uwagi
- Serialization compatibility and deterministic diagnostics are protected by positive/negative source+bundle regressions, original suites and independent review.
- Bounded13path repair, S25minutes/15files/3components; initial allocator radar predates completed acceptance criteria and is advisory.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-409/`.

<!-- ticket-radar:start -->
## Ticket Radar

Initial planned-scope estimate; advisory only, not execution or merge approval.

| Measure | Initial assessment |
| --- | --- |
| Impact score | 68/100 |
| Complexity | L |
| Estimated effort | 92 min |
| Planning budget | 30 min |
| Split recommended | yes |

Diagnostics: RADAR-ACCEPTANCE-MISSING, RADAR-BUDGET-EXCEEDED.
<!-- ticket-radar:end -->
