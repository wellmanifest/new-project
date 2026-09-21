# Ticket 257: Enforce wellman worktrees and ticket baseline across active repositories

- **ID**: ticket-257
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-09-21

## Cel i Zakres
Ustanowić jeden, mierzalny baseline dla aktywnych repozytoriów: `wellman`
ma być dostępny jako checker, adopcja ma wymagać pakietów
`wellmanifest/new-project`, `wellmanifest/worktrees` i
`wellmanifest/ticket-lifecycle`, a każda zmiana ma mieć ślad ticketu.
Rozszerzyć raport floty tak, aby potrafił audytować repozytoria zagnieżdżone
w workspace oraz wskazywał brak runtime'u `wellman`, kontraktu worktrees lub
nośników ticketów. Raport pozostaje read-only; ten ticket nie tworzy ticketów
ani worktree dla innych repozytoriów.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: Raport floty obsługuje tryb rekurencyjny z pominięciem archiwów,
  `.worktrees`, `.subactor`, `.deployments`, `node_modules` i baz danych.
- [x] AC-02: Raport dla każdego repozytorium pokazuje adopcję baseline,
  obecność bindingu `wellman`, projekcji `worktrees` oraz nośnika ticketów.
- [x] AC-03: `new-project` dostarcza do repozytorium managed checker,
  katalog pakietów, kontrakt worktrees i workflow wymagający `wellman`.
- [x] AC-04: Testy raportu obejmują repozytorium zagnieżdżone oraz przypadek
  repozytorium bez adopcji.

## Ryzyka i Uwagi
- Risk: raport może objąć repozytoria archiwalne lub checkouty techniczne;
  mitygacja: jawny tryb rekurencyjny i stała lista wykluczeń, bez żadnych
  operacji zapisu.
- Risk: samo wykrycie stringu `wellman` nie dowodzi poprawnej konfiguracji;
  mitygacja: wynik jest obserwacją audytową, a egzekwowanie pozostaje po
  stronie managed gate i wymaganego checka CI.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-257/`.
