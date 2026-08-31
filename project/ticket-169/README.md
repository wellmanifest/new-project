# Ticket 169: Release audited managed-drift adoption repair

- **ID**: ticket-169
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-08-31

## Cel i Zakres

Wydać zmergowaną naprawę atomowej adopcji driftującego managed targetu jako
nowy, niezmienny standard `0.19.17`.

## Kryteria Odbioru (Acceptance Criteria)
- [ ] AC-01: Wszystkie deklaracje i fixtury wskazują `0.19.17`.
- [ ] AC-02: Tag i opublikowany Release po protected merge wskazują dokładny
      commit z tą wersją.

## Ryzyka i Uwagi
- Risk 1: Tag jest niezmienny; mitygacją jest publikacja wyłącznie po
  niezależnej walidacji i merge bieżącego headu.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-169/`.
