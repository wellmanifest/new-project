# Ticket 226: Observe publication evidence separately from admission and delivery authority

- **ID**: ticket-226
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Utworzono**: 2026-09-13

## Cel i Zakres
Rozdzielić dowody niezapisanej pracy, obecności commitów na zdalnym serwerze,
zgodności brancha i ancestry targetu. Dodać opcjonalny odczyt do istniejącego
zarządzanego narzędzia, bez nowej bazy ticketów, obowiązkowej bramki lub
uprawnień do efektów. Kanoniczny wynik:
[kontrolowane streamowanie](../../docs/information/controlled-change-streaming.md).

Użytkownik zlecił poprawę widoczności i płynności publikacji oraz wypchnięcie
zmian standardu. Agent `codex` ma autoryzację wykonania i wywołania chronionej
publikacji w tym zakresie, ale nie jest trusted reviewerem.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: Odczyt rozróżnia brak push, publikację na innym branchu i obecność w target; sam ahead względem main nie oznacza braku push.
- [x] AC-02: Brakujące obiekty, niedostępny lub zmienny remote, niezapisana praca i wadliwe dane pozostają jawne; brak fałszywego DONE.
- [x] AC-03: Testy Git i schematu, brak mutacji, zgodność domyślnego admission oraz aktualna dokumentacja są zweryfikowane.

Dowody: `tests/work_start_test.py` — 48 testów PASS w przypiętym, izolowanym
obrazie; `tests/rule-enforcement.test.sh` PASS; governance 0 błędów; docs check
6 dokumentów PASS. Surowe wyniki w prywatnym receipt store sesji
`publication-observer-20260914.VFKAWc`, poza historią repozytorium.
Digest wyniku testów:
`sha256:50c4c346ee9fbf3b992b0f1d65e9926feb5fcc1052677924d7b3d53aef52852c`.
Rejestr zewnętrzny: https://github.com/wellmanifest/new-project/issues/344.
Wyniki lokalne nie stanowią trusted approval; wymagany pozostaje chroniony
przepływ publikacji i odczyt jego exact-head receiptu.

## Ryzyka i Uwagi
- Obserwacja Git nie dowodzi review, merge przez chroniony proces, wydania
  paczki lub deploymentu. Te etapy potrzebują osobnych zewnętrznych receiptów.
- Dane pozostają lokalne i mogą zawierać prywatne ścieżki oraz nazwy branchy;
  nie wyświetlać URL z poświadczeniami, stderr Git lub zawartości plików.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-226/`.
