# Ticket 411: Reject incomplete Git object IDs in lease evidence

- **ID**: ticket-411
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Utworzono**: 2026-11-06

## Cel i Zakres
Reject incomplete Git object IDs in canonical lease evidence and retain complete SHA-1/SHA-256 support. Synchronize existing bundled assets; include material0.20.140 release. Other review findings remain outside this slice.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: Lease/request/receipt validators reject malformed lengths and retain40/64 and permitted null.
- [x] AC-02: Bundle parity and native governance pass.
- [ ] AC-03: Declared real CI and independent exact-head publication precede release.

## Ryzyka i Uwagi
- Existing invalid lease documents will fail closed; no automatic repair, ownership transfer or policy override.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-411/`.

<!-- ticket-radar:start -->
## Ticket Radar

Initial planned-scope estimate; advisory only, not execution or merge approval.

| Measure | Initial assessment |
| --- | --- |
| Impact score | 72/100 |
| Complexity | L |
| Estimated effort | 101 min |
| Planning budget | 30 min |
| Split recommended | yes |

Diagnostics: RADAR-ACCEPTANCE-MISSING, RADAR-BUDGET-EXCEEDED.
<!-- ticket-radar:end -->

## Session execution authorization
SESSION_EXECUTION_AUTHORIZATION: user requested continued implementation, tests and protected merges. Bounded scope: exact Git object ID validation, existing bundle parity and material0.20.140 release. Independent Validator owns approval/merge.

