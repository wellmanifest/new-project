# Ticket 213: Preserve active exact ticket refs without changing activity defaults

- **ID**: ticket-213
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Utworzono**: 2026-09-11

## Cel i zakres

Bezstratnie uzgodnić zamknięty PR #322 z bieżącym `main`. Zachować ostrożną
domyślną politykę `status-projection` oraz jawny target-owned opt-in z ticketu
214. Dostarczyć wyłącznie poprawkę rozpoznawania niezakończonych refów
`ticket/NNN` i `ticket/NNN/...`, obok już obsługiwanych `ticket/NNN-...`.
Historia trzech poprzednich commitów pozostaje zachowana. Odrzucona zmiana
globalnego defaultu nie jest częścią dostawy; nie zwiększamy budżetu plików.

## Kryteria Odbioru (Acceptance Criteria)

- [x] AC-01: Default pozostaje `status-projection`; jawny target-owned opt-in
  i odrzucenie niepoprawnego override zachowują semantykę bieżącego `main`.
- [x] AC-02: Lokalne i fetched refy dokładne, z sufiksem i zagnieżdżone
  utrzymują niezakończony ticket jako aktywny. Sąsiednie numery ticketów i refy
  zawarte w target nie rezerwują jego zakresu. Testy oraz bramka przechodzą.

## Ryzyka i uwagi

Przekazanie 2026-09-13: PR #322 jest zamknięty bez scalenia. Zachowano HEAD
`ae40ca802e0b859de8b8e95bcc08bf531068096b` oraz wszystkie trzy unikalne commity.
Rezerwacja nieaktywnego writera została zwolniona przed wznowieniem; następnie
uzgodniono semantykę z bieżącym targetem i przeprowadzono walidację.
Snapshot przed przekazaniem:
`sha256:8b40cc3645b7ed52a1a6fdfcbfff896c751ba089e22cd04a140d017d6ad651fd`.

Wznowienie 2026-09-13: użytkownik przekazał ticket do bezstratnego uzgodnienia
oraz bezpiecznej publikacji standardu. Komentarz zamknięcia PR #322 odrzuca
globalny domyślny `git-ancestry` z powodu regresji bezpieczeństwa. Uzgodnienie
zachowuje obecną politykę `status-projection` i target-owned opt-in z `main`;
oddzielnie waliduje poprawkę rozpoznawania dokładnych refów ticketowych.
Sesja autoryzuje tę korektę w dotychczasowych trzech ścieżkach implementacji,
nie samodzielne zatwierdzenie merge ani odtworzenie odrzuconej polityki.

Walidacja lokalna: 18 zestawów `tests/*.test.sh`, 22 testy work-start,
governance 0 błędów, focused overlap 0 błędów, skan sekretów 0 trafień.
Test porównawczy obejmuje 10 refów: poprzedni `main` pomijał cztery;
poprawka rozpoznaje wszystkie. CI Windows i niezależny exact-head review
pozostają wymagane przed merge; lokalny PASS nie jest zatwierdzeniem.

- Pierwotne AC zmiany globalnego defaultu zastępują powyższe kryteria po
  odrzuceniu PR #322 za regresję bezpieczeństwa; pierwotny intent jest w
  zachowanej historii i snapshocie, nie jest traktowany jako zrealizowany.
- Resolver pozostaje fail-closed dla otwartego ticket branch oraz carrier-only
  zmian, co ogranicza ryzyko przedwczesnego zwolnienia rezerwacji.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-213/`.
