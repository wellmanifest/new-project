# Ticket 475: Release new-project 0.20.167

- **ID**: ticket-475
- **Owner**: agent:codex
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-11-24

## Cel i Zakres
SESSION_EXECUTION_AUTHORIZATION. NP-058. Przygotować wydanie 0.20.167 ze
scaloną poprawką alokatora #681 oraz zmianami standardu przyjętymi od wydania
0.20.166. Wydanie pozwoli przypiąć poprawkę w repozytoriach docelowych.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: Numer 0.20.167 jest zgodny w VERSION, obu manifestach,
  metadanych pakietu i changelogu.
- [x] AC-02: Alokator z przygotowanego wydania zachowuje indeks w
  powiązanym worktree i pozwala go odświeżyć jawnie.

## Ryzyka i Uwagi
Wydanie może zostać opublikowane po niezależnym scaleniu i ponownym teście
zatwierdzonego commita. Adopcja w repozytoriach docelowych przebiega przez ich
własne przypięte aktualizacje.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-475/`.

<!-- ticket-radar:start -->
## Ticket Radar

Initial planned-scope estimate; advisory only, not execution or merge approval.

| Measure | Initial assessment |
| --- | --- |
| Impact score | 64/100 |
| Complexity | L |
| Estimated effort | 68 min |
| Planning budget | 30 min |
| Split recommended | yes |

Diagnostics: RADAR-ACCEPTANCE-MISSING, RADAR-BUDGET-EXCEEDED.
<!-- ticket-radar:end -->
