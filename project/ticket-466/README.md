# Ticket 466: lease continuation: same owner renews its expired lease

- **ID**: ticket-466
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-11-20

## Cel i Zakres

Wygasły lease pierwszej natywnej adopcji nie miał żadnej kontynuacji:
`checkpoint-owner` odmawia dla wygasłych, a `takeover` i `recover-reservation`
czytają politykę idle z manifestu primary, którego repozytorium w trakcie
adopcji jeszcze nie ma (maskservice/maskauth PR #45). `renew-owner` pozwala
temu samemu właścicielowi przedłużyć własny lease: CAS na skrócie, rewizji i
fencingu, kanoniczna gałąź, pierwotna długość (15–480 min), przesunięty fencing.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: Ten sam właściciel odnawia wygasły lease z przesuniętym fencingiem.
- [x] AC-02: Inna tożsamość, żywy lease i nieaktualny CAS odmawiają.
- [x] AC-03: Istniejące testy kontynuacji i bramka repozytorium przechodzą.

## Ryzyka i Uwagi
- Odnowienie nie zmienia właściciela ani zakresu i nie daje uprawnień do recenzji ani merge.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-466/`.

<!-- ticket-radar:start -->
## Ticket Radar

Initial planned-scope estimate; advisory only, not execution or merge approval.

| Measure | Initial assessment |
| --- | --- |
| Impact score | 60/100 |
| Complexity | L |
| Estimated effort | 68 min |
| Planning budget | 30 min |
| Split recommended | yes |

Diagnostics: RADAR-ACCEPTANCE-MISSING, RADAR-BUDGET-EXCEEDED.
<!-- ticket-radar:end -->
