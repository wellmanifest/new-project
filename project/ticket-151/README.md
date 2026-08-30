# Ticket 151: Unify atomic adoption scope with verified managed paths

- **ID**: ticket-151
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Utworzono**: 2026-08-30

## Cel i Zakres

Usunąć niespójność, w której atomowa adopcja najpierw potwierdza zarządzane
pliki na podstawie package manifestu, locków, bazowego commita i digestów, ale
wcześniejsza kontrola workstreamu nie używa tego potwierdzonego zbioru. Obie
bramki mają korzystać z jednego, dynamicznie wyliczonego rejestru ścieżek.

## Kryteria Odbioru (Acceptance Criteria)

- [x] AC-01: digest-bound pliki `managed` mogą przekraczać targetowe granice
      workstreamów w jednym atomowym tickecie adopcyjnym.
- [x] AC-02: pliki `extendable`, `seed`, niezgodne z lockiem i zwykłe ścieżki
      nadal wymagają własnego workstreamu.
- [x] AC-03: pełna suita i exact-base governance gate przechodzą.

## Ryzyka i Uwagi

- Wyjątek nie pochodzi z `allowedPaths`: zbiór jest wyliczany wyłącznie po
  kryptograficznej weryfikacji opublikowanego pakietu i zaakceptowanej bazy.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-151/`.
