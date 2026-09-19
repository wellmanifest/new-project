# Ticket 251: Release Wellmanifest new-project 0.20.34

- **ID**: ticket-251
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-09-19

## Cel i Zakres

Opublikować poprawkę szablonu `AGENTS.md` z ticketu 250 jako
`wellmanifest/new-project` 0.20.34. Wersja musi być identyczna w `VERSION`,
pakiecie Wellman, obu manifestach kanonicznych oraz instrukcji aktualizacji
adopterów.

## Kryteria Odbioru (Acceptance Criteria)
- [ ] AC-01: Wszystkie kanoniczne projekcje deklarują `0.20.34`.
- [ ] AC-02: Bramka governance i test adopcji przechodzą dla jednego,
  bezbłędnego formatowo diffu.

## Ryzyka i Uwagi
- Ryzyko niespójnych numerów wersji ogranicza atomowy commit oraz porównanie
  wszystkich projekcji przed publikacją taga i GitHub Release.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-251/`.
