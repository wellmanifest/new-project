# Ticket 049: Support provenance-bound initial standard adoption

- **ID**: ticket-049
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-08-11

## Cel i Zakres

Rozszerzyć istniejącą transakcję `standardAdoption`, która dziś obsługuje
wyłącznie upgrade między dwoma lockami, o bezpieczny pierwszy bootstrap targetu
bez bazowego pakietu i locka. `fromRevision: null` ma jednoznacznie oznaczać
initial adoption.

Walidator może wyłączyć ze zwykłego budżetu i workstreamu tylko nowe,
nieistniejące w bazie targety `managed` zgodne z head package manifestem i
lockiem. Zarządzany target, który istniał przed adopcją, pozostaje normalną
zmianą targetu — musi należeć do ticketu, workstreamu i budżetu.

## Kryteria Odbioru (Acceptance Criteria)

- [x] AC-01: Polecenie użytkownika, aby poprawiać standard po pilocie `glon`,
  stanowi bounded `SESSION_EXECUTION_AUTHORIZATION` dla lokalnej naprawy.
- [ ] AC-02: Intent schema i walidator akceptują `fromRevision: null` wyłącznie
  jako bootstrap do pełnego immutable `toRevision`.
- [ ] AC-03: Bootstrap wymaga braku bazowego package manifestu i locka oraz
  kryptograficznie sprawdza head package, lock i każdy wyłączany managed target.
- [ ] AC-04: Nowy managed target nieobecny w bazie jest wyłączony z normalnego
  scope, ale zastępowany plik targetu pozostaje objęty ownershipem i budżetem.
- [ ] AC-05: Dotychczasowa transakcja upgrade oraz jej negatywne mutacje nadal
  przechodzą, podobnie jak pełny kontrakt Linux.

## Ryzyka i Uwagi

- `null` jest nowym wariantem publicznego intent v3. Zachowuje kompatybilność z
  dotychczasowym SHA i jest fail-closed, gdy w bazie istnieje już lock/pakiet.
- Nie wolno wyłączyć kolizji z istniejącym plikiem targetu: inaczej adopcja
  mogłaby ominąć review odpowiedzialności, np. przejąć wcześniejszy skrypt.
- Ticket nie zmienia domyślnego wymogu Docker, mapowania workstreamów, pakietu
  adopcyjnego, zależności, wersji ani wydania; te ustalenia są osobne.

## Reprodukcja

Pierwsza adopcja kandydata na `glon` dodała 26 plików managed. Ponieważ baza nie
ma locka, aktualny wyjątek upgrade nie działa i gate zwraca `GOV-TICKET-005`:
diff nie może rozwiązać się do dokładnie jednego aktywnego ticketu mimo pełnej
proweniencji wygenerowanego locka.

## Autoryzacja

Dozwolone są lokalne zmiany i testy z tego intentu. Push, PR, merge, tag i
publikacja nie są autoryzowane.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-049/`.
