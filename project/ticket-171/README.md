# Ticket 171: Release complete required-check projection

- **ID**: ticket-171
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-08-31

## Cel i Zakres

Opublikować zmergowaną poprawkę kompletnej projekcji wymaganych checków jako
nowy, niezmienny standard `0.19.18`.

## Kryteria Odbioru (Acceptance Criteria)
- [ ] AC-01: Wersja, manifesty i fixtury wskazują `0.19.18`.
- [ ] AC-02: Po protected merge tag i GitHub Release wskazują dokładny commit
      zawierający poprawkę z PR #275.

## Ryzyka i Uwagi
- Risk 1: Nie wolno przesuwać istniejących tagów; ewentualną korektę publikuje
  się jako następną wersję.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-171/`.
