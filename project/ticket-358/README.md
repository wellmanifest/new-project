# Ticket 358: Document first adoption route for a fresh repository (issue 499)

- **ID**: ticket-358
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-10-20

## Cel i Zakres
Issue #499: `docs/GOAL_ADOPTION.md` nie wskazywał drogi pierwszej adopcji świeżego repozytorium, więc
zgłaszający utknął w `pending-delta`/`RECONCILE`. Istniejący tryb `--bootstrap-native-adoption` (0.20.84)
zapisuje wymagany receipt; zweryfikowano na v0.20.101 w repozytorium testowym: receipt `fresh`,
admission `NEW_TICKET_CANDIDATE`, `new-ticket.sh --bootstrap-adoption-digest` przydziela ticket-001.
Przekazywanie flagi przez `goal`: semcod/goal#193.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: sekcja „Nowe repozytorium bez governance” z Goal, fallbackiem generatora i alokacją z digestem.
- [x] AC-02: link do STANDARD_UPGRADE.md działa; brak zmian kodu.

## Ryzyka i Uwagi
- Opcja Goal jest dostępna dopiero po wydaniu semcod/goal#193; dokument podaje bezpośredni fallback.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-358/`.
