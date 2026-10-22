# Ticket 368: Bind required checks to the real repository on first adoption (issue 518)

- **ID**: ticket-368
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-10-22

## Cel i Zakres
Issue #518: pierwsza adopcja zostawiała `unresolved/adopter` w
`.governance/required-checks.json`, a pierwszy materialny PR padał na
GOV-SYNC-001. Adopter wiąże prawdziwą nazwę z `origin` (jak dotąd) lub z
`--repository OWNER/NAME` przed `git remote add`, a brak tożsamości jest jawny.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: fixture: repo z remote → prawdziwa nazwa w pierwszym przebiegu; `--repository` bez remote; niezgodność z origin odrzucona; brak tożsamości → placeholder + `UNBOUND`; CLI odrzuca złe i placeholderowe nazwy; komunikat bramki (źródło i kopia Wellman) podaje wykrytą nazwę albo jej brak i polecenie updatera; istniejące testy required-checks i adoption-lock przechodzą.
- [x] AC-02: `docs/STANDARD_UPGRADE.md`, test w CI, wersja 0.20.115.

## Ryzyka i Uwagi
- Obserwowane przypadki (shellmux, willcore, willenvs, willheal) zostały zaseedowane przed dodaniem `origin`; z istniejącym `origin` wiązanie działało już wcześniej (fixture `adoption-lock`).

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-368/`.
