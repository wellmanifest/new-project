# Ticket 163: Authenticate adoption release verification

- **ID**: ticket-163
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Utworzono**: 2026-08-31

## Cel i Zakres
Generator adopcji wykorzystuje uwierzytelnioną sesję GitHub CLI wyłącznie do
odczytu finalnego release, gdy anonimowy limit API jest wyczerpany.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: Weryfikacja release używa tokenu z procesu tylko po wyczerpaniu
  konfiguracji środowiska.
- [x] AC-02: Token nie jest zapisywany ani wypisywany; test potwierdza nagłówek
  autoryzacji.

## Ryzyka i Uwagi
- Risk 1: {Opis ryzyka i mitygacja}

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-163/`.
