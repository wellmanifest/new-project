# Ticket 465: scaffold bootstrap: admit unchanged committed legacy ticket carriers

- **ID**: ticket-465
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-11-20

## Cel i Zakres

`--migrate-wellman-scaffold` instaluje się w repozytoriach takich jak
maskservice/viewer i maskservice/stacknet, ale ich pierwsza natywna alokacja
odmawiała („Scaffold bootstrap acknowledgement is first-allocation only”), bo
historia zawiera już nośniki `project/ticket-*`. Ścieżka fresh już przyjmuje
dokładne, niezmienione zacommitowane nośniki i rezerwuje numer powyżej ich
najwyższego ID; ścieżka scaffold stosuje teraz tę samą obserwację.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: Scaffold z zacommitowanym ticket-007 alokuje ticket-008 i zachowuje nośnik.
- [x] AC-02: Zmienione, brakujące, nieśledzone lub symlinkowane nośniki, żywe gałęzie ticketów i wcześniejsze rezerwacje nadal odmawiają.
- [x] AC-03: Istniejące testy bootstrapu i bramka repozytorium przechodzą.

## Ryzyka i Uwagi
- Nośniki historyczne nie dostają właściciela ani statusu; zmiana nie nadaje uprawnień zapisu ani publikacji.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-465/`.

<!-- ticket-radar:start -->
## Ticket Radar

Initial planned-scope estimate; advisory only, not execution or merge approval.

| Measure | Initial assessment |
| --- | --- |
| Impact score | 68/100 |
| Complexity | L |
| Estimated effort | 84 min |
| Planning budget | 30 min |
| Split recommended | yes |

Diagnostics: RADAR-ACCEPTANCE-MISSING, RADAR-BUDGET-EXCEEDED.
<!-- ticket-radar:end -->
