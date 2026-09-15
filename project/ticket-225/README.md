# Ticket 225: Recognize exact integrated commit trees before blocking work admission

- **ID**: ticket-225
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Utworzono**: 2026-09-13

## Cel i Zakres
Rozpoznawać identyczne drzewa wszystkich odrębnych commitów starego lokalnego
brancha w historii docelowej, zanim guard uzna go za kolidującą nową deltę.
Dotyczy tylko branchy bez zarejestrowanego worktree. Zachować refy, brak
authority i dotychczasowe zabezpieczenia rzeczywistych writerów. Publikacja
dotyczy źródeł; nowe wydanie wymaga osobnej walidacji wersjonowanych projekcji.

Kanoniczny wynik: [kontrolowane streamowanie](../../docs/information/controlled-change-streaming.md).
Rejestracja zdalna: [Issue #342](https://github.com/wellmanifest/new-project/issues/342).
Użytkownik polecił kontynuację optymalizacji i chronioną publikację. Agent
`codex` realizuje ten zakres; autoryzacja sesji nie stanowi review ani zgody
na kasowanie innych branchy, osłabienie merge lub ręczną zmianę adopterów.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: Pełna zgodność drzew wszystkich odrębnych commitów usuwa tylko fałszywą kolizję niezarejestrowanego brancha; ref pozostaje w inwentarzu.
- [x] AC-02: Częściowa zgodność, unikalny commit po integracji, nieznana historia, brudny lub aktywny worktree nadal wymagają reconcile/handoff/serialize.
- [x] AC-03: Testy prawdziwego Git, niezmienność stanu i schematu, governance oraz wersja i dokumentacja są zgodne.

## Walidacja

37 testów work-start oraz rule-enforcement PASS w izolowanym, bezsieciowym
obrazie `sha256:b856811ab56d71a80744e11e5204809fbdec50de1ba9d4b7d27d2ae98d0a3a0d`.
Dwa nowe przypadki odtworzyły błąd na bazie. Raport testów zachowano poza Git:
`receipt:sha256:9a9f84cafc69e6c3fb11ee6a84eab91221b08fbaee90633d801ff29ccc726cac`.
Jawny governance dla zakresu dostawy, diff-check i kontrola dokumentacji
PASS. Testy lokalne nie są trusted review ani dowodem publikacji wydania.

Pełna pierwsza próba publikacji odrzuciła zmianę VERSION: test adopcji ma
literalny numer 0.20.27, podobnie szerszy test walidatora. Zawężono tę dostawę
do naprawy admission bez zmiany wersji; nie wyłączono ani nie pominięto testu.

## Ryzyka i Uwagi
- Pełne drzewo Git obejmuje wszystkie pliki, tryby i gitlinki; sam patch-id,
  podobieństwo ścieżek lub nazwa recovery nie są wystarczające.
- Porównanie obejmuje target dopiero po wspólnym przodku; wcześniejszy snapshot
  nie może zamienić nowego celowego rollbacku w historyczną dostawę.
- Zgodność historycznej zawartości nie dowodzi aktualnego zachowania ani
  trusted merge. Nie zamyka ticketu i nie uprawnia do cleanup.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-225/`.
