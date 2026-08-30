# Ticket 155: Resolve ticket activity from terminal receipt registry

- **ID**: ticket-155
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: VALIDATION
- **Utworzono**: 2026-08-30

## Cel i Zakres

Usunąć deadlock, w którym historyczny tekst `IN_PROGRESS` nadal wygląda jak
aktywna rezerwacja mimo zakończonego, chronionego merge. Status w Markdown ma
pozostać konserwatywną projekcją, ale wspólny resolver aktywności ma uwzględniać
zewnętrzne terminalne receipty odkrywane z zarządzanego rejestru.

## Kryteria Odbioru (Acceptance Criteria)

- [x] AC-01: allocator, governance i worktree overlap korzystają z jednego
      resolvera, bez wyjątków per ticket lub repozytorium.
- [x] AC-02: zweryfikowany receipt `merged` zwalnia rezerwację mimo historycznej
      projekcji `IN_PROGRESS`.
- [x] AC-03: brak, uszkodzenie lub receipt niezgodny z Git nie daje fałszywego
      terminalnego wyniku i prowadzi do stabilnego ERROR z odzyskiwalną ścieżką.
- [x] AC-04: polityka rozdziela zakazy/inwarianty od implementacji i wymaga,
      aby każda blokada deklarowała bezpieczne wyjście.
- [x] AC-05: pełna suita oraz adopcyjny fixture/replay przechodzą; live adopcja
      `wellmanifest/logs` następuje po publikacji tej wersji standardu.

## Ryzyka i Uwagi

- Receipt pozostaje poza Git; rejestr w Git common dir nie jest merge approval.
- Wynik terminalny wymaga zgodności repozytorium, ticketu, head SHA, merge SHA,
  target branch oraz ancestry. Niezweryfikowany wpis pozostaje aktywny.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-155/`.
